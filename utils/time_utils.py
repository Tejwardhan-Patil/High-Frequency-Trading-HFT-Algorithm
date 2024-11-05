import pytz
from datetime import datetime, timedelta, time
import time as time_module
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TimeUtilsError(Exception):
    """Custom exception class for TimeUtils-related errors."""
    pass

class TimeUtils:
    def __init__(self, timezone='UTC'):
        try:
            self.timezone = pytz.timezone(timezone)
            logging.info(f"Initialized with timezone: {timezone}")
        except pytz.UnknownTimeZoneError:
            raise TimeUtilsError(f"Unknown timezone: {timezone}")

    def current_time(self):
        """Returns the current time in the specified time zone."""
        now = datetime.now(self.timezone)
        logging.info(f"Current time in {self.timezone}: {now}")
        return now

    def convert_timezone(self, dt, target_timezone):
        """Converts a given datetime object to the target timezone."""
        try:
            target_tz = pytz.timezone(target_timezone)
            converted_time = dt.astimezone(target_tz)
            logging.info(f"Converted {dt} from {self.timezone} to {target_timezone}: {converted_time}")
            return converted_time
        except pytz.UnknownTimeZoneError:
            raise TimeUtilsError(f"Unknown timezone: {target_timezone}")

    def get_trading_session_times(self, market_open_time, market_close_time, timezone='UTC'):
        """
        Returns trading session start and end times in the specified time zone.
        Handles cases where the market has already closed and returns times for the next day.
        """
        try:
            market_tz = pytz.timezone(timezone)
            now = datetime.now(market_tz)
            logging.info(f"Current time in {timezone}: {now}")

            market_open = market_tz.localize(datetime.combine(now.date(), market_open_time))
            market_close = market_tz.localize(datetime.combine(now.date(), market_close_time))
            
            if now > market_close:
                logging.info("Market is already closed, adjusting times for the next day.")
                market_open += timedelta(days=1)
                market_close += timedelta(days=1)
            
            logging.info(f"Market open time: {market_open}, Market close time: {market_close}")
            return market_open, market_close
        except pytz.UnknownTimeZoneError:
            raise TimeUtilsError(f"Unknown timezone: {timezone}")

    def timestamp_to_datetime(self, timestamp, timezone='UTC'):
        """Converts a UNIX timestamp to a datetime object in the specified time zone."""
        try:
            tz = pytz.timezone(timezone)
            dt = datetime.fromtimestamp(timestamp, tz)
            logging.info(f"Converted timestamp {timestamp} to datetime {dt} in timezone {timezone}")
            return dt
        except (pytz.UnknownTimeZoneError, OSError) as e:
            raise TimeUtilsError(f"Error converting timestamp: {str(e)}")

    def datetime_to_timestamp(self, dt):
        """Converts a datetime object to a UNIX timestamp."""
        timestamp = int(dt.timestamp())
        logging.info(f"Converted datetime {dt} to timestamp {timestamp}")
        return timestamp

    def time_elapsed_since(self, past_time):
        """Returns the time elapsed in seconds since a given datetime object."""
        now = datetime.now(self.timezone)
        elapsed = now - past_time
        logging.info(f"Time elapsed since {past_time}: {elapsed.total_seconds()} seconds")
        return elapsed.total_seconds()

    def sleep_until(self, future_time):
        """Sleeps the process until the given future datetime."""
        now = datetime.now(self.timezone)
        sleep_duration = (future_time - now).total_seconds()
        if sleep_duration > 0:
            logging.info(f"Sleeping for {sleep_duration} seconds until {future_time}")
            time_module.sleep(sleep_duration)
        else:
            logging.warning(f"Future time {future_time} is in the past, no sleep performed")

    def is_market_open(self, current_time, market_open_time, market_close_time):
        """Checks if the market is currently open."""
        if market_open_time <= current_time.time() <= market_close_time:
            logging.info(f"Market is open at {current_time}")
            return True
        else:
            logging.info(f"Market is closed at {current_time}")
            return False

    def get_next_market_open(self, current_time, market_open_time, timezone='UTC'):
        """Returns the next market open datetime."""
        try:
            tz = pytz.timezone(timezone)
            now = current_time.astimezone(tz)
            market_open = tz.localize(datetime.combine(now.date(), market_open_time))

            if now > market_open:
                logging.info(f"Market has already opened today, adjusting to next day.")
                market_open += timedelta(days=1)

            logging.info(f"Next market open at: {market_open}")
            return market_open
        except pytz.UnknownTimeZoneError:
            raise TimeUtilsError(f"Unknown timezone: {timezone}")

    def add_seconds(self, dt, seconds):
        """Adds a specific number of seconds to a datetime object."""
        new_time = dt + timedelta(seconds=seconds)
        logging.info(f"Added {seconds} seconds to {dt}. New time: {new_time}")
        return new_time

    def format_datetime(self, dt, format_string="%Y-%m-%d %H:%M:%S"):
        """Formats a datetime object as a string using the given format."""
        formatted = dt.strftime(format_string)
        logging.info(f"Formatted datetime {dt} as {formatted}")
        return formatted

    def parse_datetime(self, date_string, format_string="%Y-%m-%d %H:%M:%S", timezone='UTC'):
        """Parses a datetime string into a datetime object with the specified timezone."""
        try:
            dt = datetime.strptime(date_string, format_string)
            tz = pytz.timezone(timezone)
            localized_dt = tz.localize(dt)
            logging.info(f"Parsed datetime string '{date_string}' to {localized_dt}")
            return localized_dt
        except (ValueError, pytz.UnknownTimeZoneError) as e:
            raise TimeUtilsError(f"Error parsing datetime: {str(e)}")

    def get_seconds_until_market_open(self, market_open_time, timezone='UTC'):
        """Returns the number of seconds until the market opens."""
        now = datetime.now(self.timezone)
        next_open = self.get_next_market_open(now, market_open_time, timezone)
        seconds_until_open = (next_open - now).total_seconds()
        logging.info(f"Seconds until market open: {seconds_until_open}")
        return seconds_until_open

    def wait_until_market_open(self, market_open_time, timezone='UTC'):
        """Pauses execution until the market opens."""
        seconds_until_open = self.get_seconds_until_market_open(market_open_time, timezone)
        logging.info(f"Waiting for {seconds_until_open} seconds until market opens.")
        time_module.sleep(seconds_until_open)

# Usage
if __name__ == "__main__":
    time_utils = TimeUtils('America/New_York')
    
    current_time = time_utils.current_time()
    print(f"Current time: {current_time}")

    market_open_time = time(9, 30)  # 9:30 AM
    market_close_time = time(16, 0)  # 4:00 PM
    
    market_open, market_close = time_utils.get_trading_session_times(market_open_time, market_close_time)
    print(f"Market open: {market_open}, Market close: {market_close}")

    next_open = time_utils.get_next_market_open(current_time, market_open_time)
    print(f"Next market open: {next_open}")

    # Wait until market opens
    time_utils.wait_until_market_open(market_open_time)