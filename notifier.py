import requests
import os

class Notifier:
    """Sends push notifications using ntfy.sh"""
    
    def __init__(self):
        # Your unique topic name - choose something unique like "macro-tracker-yourname-12345"
        self.ntfy_topic = os.getenv('NTFY_TOPIC')
        self.ntfy_url = f'https://ntfy.sh/{self.ntfy_topic}'
    
    def send_notification(self, title, message, priority='default', tags=None):
        """
        Send a push notification via ntfy.sh
        
        Args:
            title: Notification title
            message: Notification body
            priority: 'min', 'low', 'default', 'high', or 'urgent'
            tags: List of emoji tags (e.g., ['chart_with_upwards_trend', 'moneybag'])
        
        Returns:
            True if successful, False otherwise
        """
        try:
            headers = {
                'Title': title,
                'Priority': priority
            }
            
            if tags:
                headers['Tags'] = ','.join(tags)
            
            response = requests.post(
                self.ntfy_url,
                data=message.encode('utf-8'),
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"Notification sent successfully: {title}")
                return True
            else:
                print(f"Failed to send notification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending notification: {e}")
            return False
    
    def send_buy_signal(self, macro_data):
        """Send a BUY signal notification"""
        message = (
            f"📈 BUY Signal Generated\n\n"
            f"GDP Growth: {macro_data.get('gdp_growth', 'N/A'):.2f}%\n"
            f"Inflation: {macro_data.get('inflation', 'N/A'):.2f}%\n"
            f"Real Rate: {macro_data.get('real_rate', 'N/A'):.2f}%"
        )
        return self.send_notification(
            "Trading Signal: BUY",
            message,
            priority='high',
            tags=['chart_with_upwards_trend', 'moneybag']
        )
    
    def send_sell_signal(self, macro_data):
        """Send a SELL signal notification"""
        message = (
            f"📉 SELL Signal Generated\n\n"
            f"GDP Growth: {macro_data.get('gdp_growth', 'N/A'):.2f}%\n"
            f"Inflation: {macro_data.get('inflation', 'N/A'):.2f}%\n"
            f"Real Rate: {macro_data.get('real_rate', 'N/A'):.2f}%"
        )
        return self.send_notification(
            "Trading Signal: SELL",
            message,
            priority='high',
            tags=['chart_with_downwards_trend', 'warning']
        )
    
    def test_notification(self):
        """Send a test notification"""
        return self.send_notification(
            "Test Notification",
            "Your macro tracker is set up correctly! 🎉",
            priority='low',
            tags=['white_check_mark']
        )

# Example usage
if __name__ == '__main__':
    notifier = Notifier()
    print(f"Sending test notification to topic: {notifier.ntfy_topic}")
    print(f"Subscribe on your phone: https://ntfy.sh/{notifier.ntfy_topic}")
    notifier.test_notification()
