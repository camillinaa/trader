import requests
from datetime import datetime, timedelta
import os
import time

class MacroDataFetcher:
    """Fetches macro economic data from FRED and US Treasury APIs"""
    
    def __init__(self):
        # FRED API key - get yours free at https://fred.stlouisfed.org/docs/api/api_key.html
        self.fred_api_key = os.getenv('FRED_API_KEY', '')
        self.fred_base_url = 'https://api.stlouisfed.org/fred/series/observations'
        
    def fetch_fred_data(self, series_id, limit=1):
        """
        Fetch data from FRED API
        
        Args:
            series_id: FRED series identifier
            limit: Number of most recent observations to fetch
        
        Returns:
            Latest value as float
        """
        params = {
            'series_id': series_id,
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': limit
        }
        
        response = requests.get(self.fred_base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data['observations']:
            latest = data['observations'][0]
            return {
                'value': float(latest['value']),
                'date': latest['date']
            }
        return None

    def fetch_fred_series_history(self, series_id, days=365, limit=500):
        """
        Fetch time series from FRED for the last N days.
        Uses desc + limit then filters to date range (works for all frequencies).
        Returns list of {date, value} sorted ascending by date (oldest first).
        Skips observations with missing (.) values.
        """
        if not self.fred_api_key:
            return []
        end = datetime.now()
        start = end - timedelta(days=days)
        params = {
            'series_id': series_id,
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': limit,
        }
        try:
            response = requests.get(self.fred_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            out = []
            for obs in data.get('observations', []):
                v = obs.get('value')
                if v is None or v == '.':
                    continue
                dt_str = obs.get('date')
                if not dt_str:
                    continue
                if dt_str < start.strftime('%Y-%m-%d') or dt_str > end.strftime('%Y-%m-%d'):
                    continue
                try:
                    out.append({'date': dt_str, 'value': float(v)})
                except (ValueError, TypeError):
                    continue
            out.sort(key=lambda x: x['date'])
            return out
        except Exception:
            return []

    def fetch_inflation_yoy_history(self, days=365):
        """Fetch CPI and return YoY % change for each month (last 24 months of YoY)."""
        if not self.fred_api_key:
            return []
        # Get last 36 months of CPI (desc), then compute YoY for each month that has 12m prior
        params = {
            'series_id': 'CPIAUCSL',
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 36,
        }
        try:
            response = requests.get(self.fred_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            observations = list(data.get('observations', []))
            # observations are newest first; reverse so oldest first for indexing
            observations = [o for o in observations if o.get('value') and o.get('value') != '.']
            observations.sort(key=lambda o: o['date'])
            out = []
            for i in range(12, len(observations)):
                cur = observations[i].get('value')
                prev = observations[i - 12].get('value')
                if cur and prev and cur != '.' and prev != '.':
                    try:
                        yoy = ((float(cur) - float(prev)) / float(prev)) * 100
                        out.append({'date': observations[i]['date'], 'value': yoy})
                    except (ValueError, TypeError):
                        continue
            # Keep only last 24 months within the requested window
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            out = [x for x in out if x['date'] >= cutoff]
            return out[-24:] if len(out) > 24 else out
        except Exception:
            return []

    def fetch_all_historical(self, days=365):
        """
        Fetch last 365 days of history for all 8 dashboard series.
        Returns dict: metric_key -> list of {date, value} (ascending by date).
        """
        def _fetch(series_id, **kwargs):
            out = self.fetch_fred_series_history(series_id, days=days, **kwargs)
            time.sleep(0.15)  # avoid FRED rate limiting
            return out

        neutral = self.estimate_neutral_rate()
        gdp = _fetch('A191RL1Q225SBEA')
        inflation = self.fetch_inflation_yoy_history(days)
        time.sleep(0.15)
        unemployment = _fetch('UNRATE')
        manufacturing_index = _fetch('GACDISA066MSFRBNY')
        real_rate = _fetch('DFII10')
        yield_spread = _fetch('T10Y2Y')
        fed_funds = _fetch('FEDFUNDS')
        fed_stance = [{'date': x['date'], 'value': x['value'] - neutral} for x in fed_funds]
        return {
            'gdp_growth': gdp,
            'inflation': inflation,
            'unemployment': unemployment,
            'manufacturing_index': manufacturing_index,
            'real_rate': real_rate,
            'yield_spread': yield_spread,
            'fed_funds': fed_funds,
            'fed_stance': fed_stance,
        }
    
    def fetch_gdp_growth(self):
        """
        Fetch GDP growth rate (year-over-year % change)
        Series: A191RL1Q225SBEA (Real GDP % change)
        """
        result = self.fetch_fred_data('A191RL1Q225SBEA')
        return result['value'] if result else None
    
    def fetch_inflation(self):
        """
        Fetch CPI inflation rate (year-over-year % change)
        Series: CPIAUCSL (Consumer Price Index)
        We'll need to calculate YoY change
        """
        # Get last 13 months to calculate year-over-year
        result = self.fetch_fred_data('CPIAUCSL', limit=13)
        
        if result:
            # For simplicity, return the latest value
            # In production, you'd calculate YoY % change
            return result['value']
        return None
    
    def fetch_inflation_yoy(self):
        """
        Fetch year-over-year CPI inflation
        Series: CPIAUCSL
        """
        params = {
            'series_id': 'CPIAUCSL',
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 13  # Get 13 months to calculate YoY
        }
        
        response = requests.get(self.fred_base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        observations = data['observations']
        
        if len(observations) >= 13:
            current = float(observations[0]['value'])
            year_ago = float(observations[12]['value'])
            inflation_rate = ((current - year_ago) / year_ago) * 100
            return inflation_rate
        
        return None
    
    def fetch_real_treasury_rate(self):
        """
        Fetch 10-year TIPS (Treasury Inflation-Protected Securities) rate
        Series: DFII10 (Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, Inflation-Indexed)
        """
        result = self.fetch_fred_data('DFII10')
        return result['value'] if result else None
    
    def fetch_unemployment_rate(self):
        """
        Fetch unemployment rate
        Series: UNRATE (Unemployment Rate)
        """
        result = self.fetch_fred_data('UNRATE')
        return result['value'] if result else None
    
    def fetch_manufacturing_index(self):
        """
        Fetch manufacturing index
        Series: GACDISA066MSFRBNY (New York Fed Empire State Manufacturing Survey: General Business Conditions Index)
        """
        result = self.fetch_fred_data('GACDISA066MSFRBNY')
        return result['value'] if result else None
    
    def fetch_yield_spread_2_10(self):
        """
        Fetch 2Y-10Y Treasury yield spread
        Series: T10Y2Y (10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity)
        """
        result = self.fetch_fred_data('T10Y2Y')
        return result['value'] if result else None
    
    def fetch_fed_funds_rate(self):
        """
        Fetch effective federal funds rate
        Series: FEDFUNDS (Effective Federal Funds Rate)
        """
        result = self.fetch_fred_data('FEDFUNDS')
        return result['value'] if result else None
    
    def estimate_neutral_rate(self):
        """
        Estimate neutral rate (r*) using simple Taylor Rule approximation
        Rough estimate: ~2.5% historically, adjust for current inflation expectations
        """
        # Simplified: neutral real rate (~0.5%) + inflation target (2%)
        return 2.5
    
    def fetch_all_data(self):
        """
        Fetch all macro indicators
        
        Returns:
            Dictionary with all current macro data
        """
        fed_funds = self.fetch_fed_funds_rate()
        neutral = self.estimate_neutral_rate()
        
        return {
            'gdp_growth': self.fetch_gdp_growth(),
            'inflation': self.fetch_inflation_yoy(),
            'real_rate': self.fetch_real_treasury_rate(),
            'unemployment': self.fetch_unemployment_rate(),
            'manufacturing_index': self.fetch_manufacturing_index(),
            'yield_spread': self.fetch_yield_spread_2_10(),
            'fed_funds': fed_funds,
            'neutral_rate': neutral,
            'fed_stance': fed_funds - neutral if fed_funds else None,
            'timestamp': datetime.now().isoformat()
        }
        
# Example usage
if __name__ == '__main__':
    fetcher = MacroDataFetcher()
    data = fetcher.fetch_all_data()
    print("Current Macro Data:")
    print(f"GDP Growth: {data['gdp_growth']:.2f}%")
    print(f"Inflation (YoY): {data['inflation']:.2f}%")
    print(f"Real Treasury Rate (10Y): {data['real_rate']:.2f}%")
