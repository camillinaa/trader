from supabase import create_client, Client
from dotenv import load_dotenv

import os
from datetime import datetime

class Database:
    """Handles all database operations with Supabase"""
    
    def __init__(self):
        # Get Supabase credentials from environment variables
        load_dotenv()
        supabase_url = os.getenv('SUPABASE_URL', '')
        supabase_key = os.getenv('SUPABASE_KEY', '')
        
        if supabase_url and supabase_key:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None
            print("Warning: Supabase credentials not found. Set SUPABASE_URL and SUPABASE_KEY environment variables.")
    
    def save_data(self, macro_data):
        """
        Save macro data to Supabase
        
        Args:
            macro_data: Dictionary containing gdp_growth, inflation, real_rate, timestamp
        
        Returns:
            Inserted record or None if failed
        """
        if not self.supabase:
            print("Cannot save data: Supabase not initialized")
            return None
        
        try:
            data = {
                'gdp_growth': macro_data.get('gdp_growth'),
                'inflation': macro_data.get('inflation'),
                'real_rate': macro_data.get('real_rate'),
                'created_at': macro_data.get('timestamp', datetime.now().isoformat())
            }
            
            result = self.supabase.table('macro_data').insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            return None
    
    def get_latest_data(self):
        """
        Retrieve the most recent macro data
        
        Returns:
            Dictionary with latest data or None
        """
        if not self.supabase:
            return {
                'error': 'Database not connected',
                'gdp_growth': None,
                'inflation': None,
                'real_rate': None
            }
        
        try:
            result = self.supabase.table('macro_data') \
                .select('*') \
                .order('created_at', desc=True) \
                .limit(1) \
                .execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"Error fetching from Supabase: {e}")
            return None
    
    def get_historical_data(self, limit=30):
        """
        Retrieve historical macro data
        
        Args:
            limit: Number of records to retrieve
        
        Returns:
            List of data records
        """
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.table('macro_data') \
                .select('*') \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return []

# SQL schema for Supabase table (run this in Supabase SQL editor):
"""
CREATE TABLE macro_data (
    id BIGSERIAL PRIMARY KEY,
    gdp_growth DECIMAL(10, 2),
    inflation DECIMAL(10, 2),
    real_rate DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on created_at for faster queries
CREATE INDEX idx_macro_data_created_at ON macro_data(created_at DESC);
"""
