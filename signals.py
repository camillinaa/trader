class Signals:
    """Calculates the signals for the macro data"""
    def __init__(self):
        pass

    @staticmethod
    def calculate_macro_regime_score(gdp_growth, inflation, unemployment, 
                                manufacturing_index, real_rate, 
                                yield_curve_spread, fed_stance):
        
        # Component scores (0-100 each)
        
        # 1. Growth score (target: 2-4% is ideal)
        growth_score = min(100, max(0, (gdp_growth / 6) * 100))
        
        # 2. Inflation score (target: closer to 2% is better)
        inflation_distance = abs(inflation - 2.0)
        inflation_score = max(0, 100 - (inflation_distance * 30))
        
        # 3. Employment score (target: 3.5-4.5% unemployment is healthy)
        if 3.5 <= unemployment <= 4.5:
            employment_score = 100
        elif unemployment < 3.5:
            employment_score = 80  # Too tight, inflation risk
        else:
            employment_score = max(0, 100 - ((unemployment - 4.5) * 20))
        
        # 4. Manufacturing score (above 0 is expansion)
        manufacturing_score = min(100, max(0, 50 + (manufacturing_index * 2)))
        
        # 5. Yield curve score (positive slope is healthy)
        curve_score = min(100, max(0, 50 + (yield_curve_spread * 0.5)))
        
        # 6. Fed policy score (closer to neutral is better)
        fed_score = max(0, 100 - (abs(fed_stance) * 40))
        
        # Weighted average
        regime_score = (
            growth_score * 0.25 +
            inflation_score * 0.20 +
            employment_score * 0.15 +
            manufacturing_score * 0.15 +
            curve_score * 0.15 +
            fed_score * 0.10
        )
        
        return round(regime_score, 1)

