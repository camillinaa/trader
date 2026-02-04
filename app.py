from flask import Flask, render_template, jsonify
from datetime import datetime
import os
from data_fetcher import MacroDataFetcher
from database import Database
from notifier import Notifier

app = Flask(__name__)

# Initialize components
db = Database()
fetcher = MacroDataFetcher()
notifier = Notifier()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/current-data')
def get_current_data():
    """API endpoint to get current macro data"""
    data = db.get_latest_data()
    return jsonify(data)

@app.route('/api/update-data')
def update_data():
    """Manually trigger data update"""
    try:
        # Fetch latest data
        macro_data = fetcher.fetch_all_data()
        
        # Save to database
        db.save_data(macro_data)
        
        # Check if notification should be sent
        # (You'll define your rules here later)
        signal = calculate_signal(macro_data)
        if signal:
            notifier.send_notification(
                f"Trading Signal: {signal['action']}",
                f"Growth: {macro_data['gdp_growth']:.2f}%, "
                f"Inflation: {macro_data['inflation']:.2f}%, "
                f"Real Rate: {macro_data['real_rate']:.2f}%"
            )
        
        return jsonify({
            'success': True,
            'data': macro_data,
            'signal': signal
        })
    except Exception as e:
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
