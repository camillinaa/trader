import requests
from datetime import datetime, timedelta
import os

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
    
    def fetch_all_data(self):
        """
        Fetch all macro indicators
        
        Returns:
            Dictionary with all current macro data
        """
        return {
            'gdp_growth': self.fetch_gdp_growth(),
            'inflation': self.fetch_inflation_yoy(),
            'real_rate': self.fetch_real_treasury_rate(),
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
