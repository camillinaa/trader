import requests
import os

class GeminiAnalyzer:
    """Generate AI trading summaries using Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', '')
        self.api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
    
    def generate_trading_summary(self, macro_data):
        """
        Generate AI trading summary from macro data
        
        Args:
            macro_data: Dictionary with all macro indicators
        
        Returns:
            AI-generated trading summary as string
        """
        if not self.api_key:
            return "Gemini API key not configured. Set GEMINI_API_KEY in .env file."
        
        prompt = self._build_prompt(macro_data)
        
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                return text.strip()
            
            return "Unable to generate summary"
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _build_prompt(self, data):
        """Build the prompt for Gemini"""
        
        # Format the data nicely
        fed_stance_desc = "restrictive" if (data.get('fed_stance') or 0) > 0 else "accommodative"
        yield_curve = "inverted" if (data.get('yield_spread') or 0) < 0 else "normal"
        
        prompt = f"""You are a quantitative macro analyst. Analyze these economic indicators and provide a concise trading summary (3-4 sentences max).

CURRENT MACRO DATA:
- GDP Growth: {data.get('gdp_growth', 'N/A')}% YoY
- Inflation (CPI): {data.get('inflation', 'N/A')}% YoY
- Unemployment: {data.get('unemployment', 'N/A')}%
- Manufacturing Index: {data.get('manufacturing_index', 'N/A')}
- 10Y Real Rate (TIPS): {data.get('real_rate', 'N/A')}%
- 2Y-10Y Yield Spread: {data.get('yield_spread', 'N/A')}% ({yield_curve})
- Fed Funds Rate: {data.get('fed_funds', 'N/A')}%
- Fed Stance vs Neutral: {data.get('fed_stance', 'N/A')}% ({fed_stance_desc})

Provide:
1. Overall economic regime (expansion/slowdown/recession)
2. Asset class positioning (equities/bonds/commodities - bullish/neutral/bearish)
3. Key risks to watch
4. Specific actionable insight

Be direct and actionable. No disclaimers about not being financial advice."""

        return prompt

# Example usage
if __name__ == '__main__':
    analyzer = GeminiAnalyzer()
    
    test_data = {
        'gdp_growth': 4.40,
        'inflation': 2.65,
        'unemployment': 4.1,
        'manufacturing_index': 10.0,
        'real_rate': 1.92,
        'yield_spread': 0.15,
        'fed_funds': 4.50,
        'neutral_rate': 2.5,
        'fed_stance': 2.0
    }
    
    summary = analyzer.generate_trading_summary(test_data)
    print("AI Trading Summary:")
    print(summary)
