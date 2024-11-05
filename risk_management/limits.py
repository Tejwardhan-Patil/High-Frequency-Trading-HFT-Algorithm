import logging
from datetime import datetime

logging.basicConfig(
    filename='risk_management.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RiskLimits:
    def __init__(self, max_position_size, max_loss_per_day, max_trade_loss, stop_loss_threshold, max_orders_per_minute):
        self.max_position_size = max_position_size   
        self.max_loss_per_day = max_loss_per_day      
        self.max_trade_loss = max_trade_loss        
        self.stop_loss_threshold = stop_loss_threshold  
        self.max_orders_per_minute = max_orders_per_minute  

        # Initialize tracking variables
        self.current_position_size = 0
        self.current_loss_per_day = 0
        self.current_trade_loss = 0
        self.orders_this_minute = 0
        self.last_order_time = None
        self.daily_limit_breached = False

        # Initialize trade tracking
        self.trades = []
        self.closed_positions = []

    def log_event(self, event, message):
        """
        Logs a specific event in the risk management system.
        """
        logging.info(f"{event}: {message}")

    def can_take_position(self, position_size):
        """
        Checks if a new position can be taken based on the position size limit.
        """
        if abs(self.current_position_size + position_size) > self.max_position_size:
            self.log_event('PositionLimitExceeded', f"Attempted position size: {position_size}, Current size: {self.current_position_size}")
            return False
        return True

    def update_position_size(self, position_size):
        """
        Updates the current position size after taking a new position.
        """
        self.current_position_size += position_size
        self.trades.append({'timestamp': datetime.now(), 'position_size': position_size})
        self.log_event('PositionUpdate', f"New position size: {self.current_position_size}")

    def can_take_loss(self, trade_loss):
        """
        Checks if a trade can be executed based on the maximum allowable loss per trade.
        """
        if abs(trade_loss) > self.max_trade_loss:
            self.log_event('TradeLossLimitExceeded', f"Attempted trade loss: {trade_loss}")
            return False
        return True

    def update_trade_loss(self, trade_loss):
        """
        Updates the current loss after a trade has been executed.
        """
        self.current_trade_loss += trade_loss
        self.current_loss_per_day += trade_loss
        self.log_event('TradeLossUpdate', f"Current trade loss: {self.current_trade_loss}, Daily loss: {self.current_loss_per_day}")

    def check_daily_loss_limit(self):
        """
        Checks if the daily loss has exceeded the allowable limit.
        """
        if abs(self.current_loss_per_day) > self.max_loss_per_day:
            self.log_event('DailyLossLimitExceeded', f"Daily loss limit exceeded: {self.current_loss_per_day}")
            self.daily_limit_breached = True
            return False
        return True

    def should_trigger_stop_loss(self, current_position_value):
        """
        Checks if stop-loss should be triggered based on the stop-loss threshold.
        """
        if abs(current_position_value) <= self.stop_loss_threshold:
            self.log_event('StopLossTriggered', f"Stop-loss threshold reached: {current_position_value}")
            return True
        return False

    def reset_daily_limits(self):
        """
        Resets the daily limits at the start of a new trading day.
        """
        self.current_loss_per_day = 0
        self.current_trade_loss = 0
        self.daily_limit_breached = False
        self.log_event('DailyReset', "Daily risk limits have been reset.")

    def check_order_rate(self):
        """
        Checks if the order rate per minute exceeds the allowable limit.
        """
        current_time = datetime.now()
        if self.last_order_time:
            time_diff = (current_time - self.last_order_time).seconds / 60.0
            if time_diff < 1:
                self.orders_this_minute += 1
            else:
                self.orders_this_minute = 1
            self.last_order_time = current_time
        else:
            self.last_order_time = current_time
            self.orders_this_minute = 1

        if self.orders_this_minute > self.max_orders_per_minute:
            self.log_event('OrderRateLimitExceeded', f"Orders per minute: {self.orders_this_minute}")
            return False
        return True

    def close_position(self, position_value):
        """
        Closes the current position and logs the event.
        """
        self.closed_positions.append({'timestamp': datetime.now(), 'closed_position_value': position_value})
        self.current_position_size = 0
        self.log_event('PositionClosed', f"Position closed with value: {position_value}")

    def get_risk_summary(self):
        """
        Returns a summary of current risk metrics.
        """
        return {
            'current_position_size': self.current_position_size,
            'current_loss_per_day': self.current_loss_per_day,
            'current_trade_loss': self.current_trade_loss,
            'orders_this_minute': self.orders_this_minute,
            'daily_limit_breached': self.daily_limit_breached
        }

    def evaluate_risk(self):
        """
        Comprehensive risk evaluation to be used before every trade.
        """
        risk_summary = self.get_risk_summary()
        if not self.check_daily_loss_limit():
            return False
        if not self.check_order_rate():
            return False
        self.log_event('RiskEvaluation', f"Risk evaluation passed with summary: {risk_summary}")
        return True

# Usage
if __name__ == "__main__":
    # Risk parameters
    max_position_size = 100000 
    max_loss_per_day = 50000    
    max_trade_loss = 10000     
    stop_loss_threshold = -20000  
    max_orders_per_minute = 5  

    risk_limits = RiskLimits(max_position_size, max_loss_per_day, max_trade_loss, stop_loss_threshold, max_orders_per_minute)

    # Checking and updating position size
    position_size = 50000
    if risk_limits.can_take_position(position_size):
        risk_limits.update_position_size(position_size)
    else:
        print("Position size limit exceeded. Cannot take this position.")

    # Checking and updating trade loss
    trade_loss = 7000
    if risk_limits.can_take_loss(trade_loss):
        risk_limits.update_trade_loss(trade_loss)
    else:
        print("Trade loss limit exceeded. Cannot execute this trade.")

    # Daily loss check
    if not risk_limits.check_daily_loss_limit():
        print("Daily loss limit exceeded. Trading halted.")

    # Stop-loss trigger check
    current_position_value = -25000
    if risk_limits.should_trigger_stop_loss(current_position_value):
        print("Stop-loss triggered. Closing all positions.")
        risk_limits.close_position(current_position_value)

    # Order rate check
    if not risk_limits.check_order_rate():
        print("Order rate limit exceeded. Slow down order submission.")
    
    # Reset daily limits at end of trading day
    risk_limits.reset_daily_limits()

    # Risk evaluation before executing a trade
    if not risk_limits.evaluate_risk():
        print("Risk evaluation failed. Cannot proceed with trade.")