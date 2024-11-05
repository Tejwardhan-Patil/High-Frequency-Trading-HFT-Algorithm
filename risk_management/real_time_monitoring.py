import threading
import time
import logging
import requests
from market_data.data_aggregation import get_latest_data
from execution.order_manager import get_active_orders, get_positions
from risk_management.limits import get_risk_limits

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RealTimeRiskMonitor:
    def __init__(self, update_interval=1):
        self.update_interval = update_interval  
        self.positions = {}  
        self.pnls = {} 
        self.exposure_by_asset_class = {} 
        self.total_exposure = 0 
        self.total_pnl = 0  
        self.risk_limits = get_risk_limits()  
        self.running = False

    def start_monitoring(self):
        logging.info("Starting real-time risk monitoring.")
        self.running = True
        threading.Thread(target=self.monitor_risk).start()

    def stop_monitoring(self):
        logging.info("Stopping risk monitoring.")
        self.running = False

    def monitor_risk(self):
        """Main loop to monitor positions, PnL, and enforce risk limits."""
        while self.running:
            try:
                self.positions = get_positions()
                self.update_exposure_by_asset_class()
                self.pnls = self.calculate_pnl(self.positions)
                self.total_exposure = sum([abs(pos['quantity']) for pos in self.positions.values()])
                self.total_pnl = sum(self.pnls.values())
                self.check_risk_limits()
            except Exception as e:
                logging.error(f"Error in monitoring risk: {e}")
            time.sleep(self.update_interval)

    def update_exposure_by_asset_class(self):
        """Update exposure metrics broken down by asset class."""
        self.exposure_by_asset_class = {}
        for symbol, position in self.positions.items():
            asset_class = self.get_asset_class(symbol)
            exposure = position['quantity'] * position['entry_price']
            if asset_class in self.exposure_by_asset_class:
                self.exposure_by_asset_class[asset_class] += exposure
            else:
                self.exposure_by_asset_class[asset_class] = exposure
        logging.info(f"Exposure by asset class: {self.exposure_by_asset_class}")

    def get_asset_class(self, symbol):
        """Determine the asset class of a given symbol."""
        if symbol.startswith("FX"):
            return "Forex"
        elif symbol.startswith("EQ"):
            return "Equities"
        elif symbol.startswith("COM"):
            return "Commodities"
        else:
            return "Other"

    def calculate_pnl(self, positions):
        """Calculate PnL for all current positions."""
        pnls = {}
        for symbol, position in positions.items():
            latest_data = get_latest_data(symbol)
            market_price = latest_data['price']
            pnl = self.calculate_position_pnl(position, market_price)
            pnls[symbol] = pnl
        logging.info(f"Updated PnL: {pnls}")
        return pnls

    def calculate_position_pnl(self, position, market_price):
        """Calculate the PnL for a single position."""
        entry_price = position['entry_price']
        quantity = position['quantity']
        fees = self.calculate_fees(position)
        pnl = (market_price - entry_price) * quantity - fees
        return pnl

    def calculate_fees(self, position):
        """Calculate any fees associated with the position."""
        fee_rate = 0.0001  
        return abs(position['quantity'] * position['entry_price'] * fee_rate)

    def check_risk_limits(self):
        """Enforce risk limits and trigger alerts when limits are breached."""
        if self.total_exposure > self.risk_limits['max_position_size']:
            self.trigger_risk_alert("Max position size exceeded")

        if self.total_pnl < self.risk_limits['max_loss']:
            self.trigger_risk_alert("Max loss threshold breached")

        for asset_class, exposure in self.exposure_by_asset_class.items():
            if exposure > self.risk_limits['max_exposure_by_asset_class'][asset_class]:
                self.trigger_risk_alert(f"Max exposure in {asset_class} exceeded")

        logging.info(f"Current Exposure: {self.total_exposure}, Current PnL: {self.total_pnl}")

    def trigger_risk_alert(self, message):
        logging.warning(f"RISK ALERT: {message}")
        
        self.halt_trading()
        self.liquidate_positions()
        self.send_alert(message)

    def halt_trading(self):
        logging.info("Trading has been halted.")

    def liquidate_positions(self):
        logging.info("Positions have been liquidated.")

    def generate_risk_report(self):
        """Generate a detailed report of current risk exposure and performance."""
        report = {
            'total_exposure': self.total_exposure,
            'total_pnl': self.total_pnl,
            'exposure_by_asset_class': self.exposure_by_asset_class,
            'positions': self.positions,
            'pnls': self.pnls
        }
        logging.info(f"Risk Report: {report}")
        return report

    def save_report(self, report, filename='risk_report.txt'):
        """Save the generated risk report to a file."""
        with open(filename, 'w') as file:
            for key, value in report.items():
                file.write(f"{key}: {value}\n")
        logging.info(f"Risk report saved to {filename}")

    def send_alert(self, alert_message):
        logging.info(f"Sending alert: {alert_message}")
        
        api_url = "https://api.website.com/send_alert"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer api_token"
        }
        payload = {
            "message": alert_message,
            "recipient": "risk_management_team@website.com"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logging.info("Alert sent successfully.")
        else:
            logging.error(f"Failed to send alert. Status code: {response.status_code}, Response: {response.text}")


def format_currency(value):
    """Utility function to format numbers as currency."""
    return f"${value:,.2f}"


def format_percentage(value):
    """Utility function to format numbers as percentages."""
    return f"{value:.2%}"


if __name__ == "__main__":
    monitor = RealTimeRiskMonitor(update_interval=1)

    try:
        monitor.start_monitoring()
        while True:
            time.sleep(10)  # Keep main thread alive for monitoring
            if int(time.time()) % 60 == 0:  # Generate report every 60 seconds
                report = monitor.generate_risk_report()
                monitor.save_report(report)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        logging.info("Risk monitoring stopped.")