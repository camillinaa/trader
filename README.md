# Macro Tracker - Personal Trading Signal App

A free, self-hosted web app that tracks key macroeconomic indicators (GDP growth, inflation, real interest rates) and sends you push notifications when trading conditions meet your criteria.
This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.

## Features

- 📊 Real-time tracking of GDP growth, CPI inflation, and 10-year TIPS rates
- 📱 Push notifications to your phone via ntfy.sh
- 💾 Data persistence with Supabase
- 🌐 Clean web dashboard
- 💰 100% free to run

## Tech Stack

- **Backend**: Python + Flask
- **Data Sources**: FRED API, US Treasury API
- **Database**: Supabase (PostgreSQL)
- **Notifications**: ntfy.sh
- **Hosting**: Run locally or deploy to free tier (Render, Railway)

## Setup Instructions

> **📝 Conda Users**: See [CONDA_QUICKSTART.md](CONDA_QUICKSTART.md) for a streamlined conda-specific guide!

### 1. Get Your Free API Keys

#### FRED API Key
1. Go to https://fred.stlouisfed.org/
2. Create a free account
3. Request an API key at https://fred.stlouisfed.org/docs/api/api_key.html
4. Copy your API key

#### Supabase Setup
1. Go to https://supabase.com and create a free account
2. Create a new project
3. Go to Project Settings > API
4. Copy your project URL and anon/public key
5. Go to SQL Editor and run this SQL to create the table:

```sql
CREATE TABLE macro_data (
    id BIGSERIAL PRIMARY KEY,
    gdp_growth DECIMAL(10, 2),
    inflation DECIMAL(10, 2),
    real_rate DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_macro_data_created_at ON macro_data(created_at DESC);
```

#### ntfy.sh Setup
1. Download the ntfy app on your phone:
   - iOS: https://apps.apple.com/us/app/ntfy/id1625396347
   - Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy
2. Choose a unique topic name (e.g., `macro-tracker-yourname-12345`)
3. Subscribe to your topic in the app

### 2. Install Dependencies

**Recommended: Using Conda**

```bash
# Navigate to project directory
cd macro_tracker

# Automated setup (Linux/Mac)
./setup_conda.sh

# OR Manual setup
conda env create -f environment.yml
conda activate macro_tracker
```

For Windows:
```bash
cd macro_tracker
setup_conda.bat
```

**Alternative: Using pip**
```bash
pip install -r requirements.txt
```

> 💡 **Why conda?** Isolated environment, better dependency management, works across platforms

### 3. Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use any text editor
```

Fill in your credentials:
```
FRED_API_KEY=your_actual_fred_key
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_actual_supabase_key
NTFY_TOPIC=macro-tracker-yourname-12345
```

### 4. Run the App

```bash
# Make sure conda environment is activated
conda activate macro_tracker

# Run the Flask app
python app.py
```

The app will start at http://localhost:5000

### 5. Test Everything

1. Open http://localhost:5000 in your browser
2. Click "🔄 Refresh Data" to fetch latest macro data
3. Click "📱 Test Notification" and check your phone

## How It Works

### Data Sources

The app fetches three key indicators:

1. **GDP Growth** (FRED: A191RL1Q225SBEA)
   - Real GDP year-over-year % change
   - Updated quarterly

2. **Inflation** (FRED: CPIAUCSL)
   - Consumer Price Index year-over-year % change
   - Updated monthly

3. **Real Interest Rate** (FRED: DFII10)
   - 10-year Treasury Inflation-Protected Securities yield
   - Updated daily

### Trading Signal Logic

Current example rules (customize in `app.py`):

- **BUY**: GDP growth > 2%, inflation < 3%, real rate < 1%
- **SELL**: GDP growth < 0% OR inflation > 4%
- **HOLD**: All other conditions

### Customizing Your Rules

Edit the `calculate_signal()` function in `app.py`:

```python
def calculate_signal(data):
    # Your custom logic here
    if data['gdp_growth'] > X and data['inflation'] < Y:
        return {'action': 'BUY', 'reason': '...'}
    # ... more conditions
```

## Automation

To automatically check data and send notifications:

### Option 1: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line to check daily at 9 AM
0 9 * * * curl http://localhost:5000/api/update-data
```

### Option 2: Python Scheduler

Create `scheduler.py`:

```python
import schedule
import time
import requests

def update_data():
    requests.get('http://localhost:5000/api/update-data')

# Run every day at 9 AM
schedule.every().day.at("09:00").do(update_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Deployment (Free Options)

### Render.com
1. Push code to GitHub
2. Connect to Render
3. Add environment variables
4. Deploy (free tier: sleeps after 15 min inactivity)

### Railway.app
1. Push code to GitHub
2. Connect to Railway
3. Add environment variables
4. Deploy (free tier: $5 credit/month)

### Keep Running 24/7
Use a Raspberry Pi, old laptop, or cloud VM to keep the app running continuously.

## Project Structure

```
macro_tracker/
├── app.py                 # Main Flask application
├── data_fetcher.py       # FRED/Treasury API client
├── database.py           # Supabase database operations
├── notifier.py           # ntfy.sh notifications
├── templates/
│   └── index.html       # Web dashboard
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Troubleshooting

### Conda environment issues
```bash
# If environment creation fails, try updating conda
conda update conda

# To recreate the environment
conda env remove -n macro_tracker
conda env create -f environment.yml

# List conda environments to verify
conda env list
```

### "Module not found" errors
```bash
# Make sure environment is activated
conda activate macro_tracker

# Verify packages are installed
conda list
```

### Database connection fails
- Check your Supabase URL and key in `.env`
- Verify the table was created in Supabase SQL editor

### No notifications received
- Verify you're subscribed to the correct topic in ntfy app
- Check the topic name matches in `.env`
- Test with the "Test Notification" button

### FRED API errors
- Verify your API key is correct
- Check you haven't exceeded rate limits (120 requests/minute)

## Next Steps

1. **Refine your trading rules** based on strategy
2. **Add more indicators** (unemployment, yield curve, etc.)
3. **Backtest strategy** using historical data
4. **Set up automated scheduling** for daily checks
5. **Add charting** to visualize trends over time

## Important Notes

⚠️ **This is for personal use only** - not financial advice
⚠️ **Test thoroughly** before relying on signals
⚠️ **Data lags** - macro data updates monthly/quarterly

## License

MIT - Feel free to modify and use as you wish!
