from flask import Flask, render_template, jsonify
from datetime import datetime
import os
from data_fetcher import MacroDataFetcher
from signals import Signals
from database import Database
from notifier import Notifier
from gemini_analyzer import GeminiAnalyzer

app = Flask(__name__)

# Initialize components
db = Database()
fetcher = MacroDataFetcher()
signals = Signals()
notifier = Notifier()
analyzer = GeminiAnalyzer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/current-data')
def get_current_data():
    """API endpoint to get current macro data"""
    data = db.get_latest_data() or {}
    data = _add_regime_score(data)
    return jsonify(data)

@app.route('/api/history')
def get_history():
    """API endpoint to get 365-day history for all 8 macro series (for sparklines)."""
    days = 365
    try:
        history = fetcher.fetch_all_historical(days=days)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-data')
def update_data():
    """Manually trigger macro data refresh (boxes + charts). Does not run AI."""
    try:
        macro_data = fetcher.fetch_all_data()
        db.save_data(macro_data)

        signal = calculate_signal(macro_data)
        if signal:
            notifier.send_notification(
                f"Trading Signal: {signal['action']}",
                f"GDP: {macro_data['gdp_growth']:.2f}%, "
                f"Inflation: {macro_data['inflation']:.2f}%, "
                f"Unemployment: {macro_data['unemployment']:.2f}%"
            )

        macro_data = _add_regime_score(macro_data)
        return jsonify({
            'success': True,
            'data': macro_data,
            'signal': signal,
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-ai-summary')
def generate_ai_summary():
    """Generate AI trading overview from current macro data (on-demand only)."""
    try:
        macro_data = fetcher.fetch_all_data()
        ai_summary = analyzer.generate_trading_summary(macro_data)
        return jsonify({'success': True, 'ai_summary': ai_summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def _add_regime_score(data):
    """Compute and add macro_regime_score to data if inputs are available."""
    required = ['gdp_growth', 'inflation', 'unemployment', 'manufacturing_index', 'real_rate', 'yield_spread', 'fed_stance']
    if not all(data.get(k) is not None for k in required):
        return data
    try:
        score = signals.calculate_macro_regime_score(
            data['gdp_growth'], data['inflation'], data['unemployment'],
            data['manufacturing_index'], data['real_rate'], data['yield_spread'],  # % pts
            data['fed_stance']
        )
        data['macro_regime_score'] = score
    except (TypeError, KeyError):
        pass
    return data


@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    """Send a test notification"""
    try:
        print("🔔 Test notification endpoint called")  # Debug log
        success = notifier.test_notification()
        return jsonify({
            'success': success,
            'topic': notifier.ntfy_topic,
            'message': 'Test notification sent!' if success else 'Failed to send notification'
        })
    except Exception as e:
        print(f"❌ Error in test endpoint: {e}")  # Debug log
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    
def calculate_signal(data):
    """
    Calculate buy/sell signal based on macro data
    This is a placeholder - you'll define your own rules
    """
    # Example simple rule (replace with your logic):
    # Buy if growth > 2% and inflation < 3% and real rate < 1%
    # Sell if growth < 0% or inflation > 4%
    
    if data['gdp_growth'] > 2 and data['inflation'] < 3 and data['real_rate'] < 1:
        return {
            'action': 'BUY',
            'reason': 'Strong growth, low inflation, low real rates'
        }
    elif data['gdp_growth'] < 0 or data['inflation'] > 4:
        return {
            'action': 'SELL',
            'reason': 'Negative growth or high inflation'
        }
    
    return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
