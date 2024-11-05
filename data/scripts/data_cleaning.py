import pandas as pd
import numpy as np
from scipy import stats
import logging
import os

# Setup logging
logging.basicConfig(
    filename='data_cleaning.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DataCleaning:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.original_shape = data.shape
        self.cleaned_shape = None
        self.outliers_removed = 0
        logging.info("DataCleaning initialized with data shape: %s", self.original_shape)

    def validate_data(self):
        # Ensure that the data is a DataFrame
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        logging.info("Data validation passed.")

    def remove_missing_values(self):
        logging.info("Removing missing values...")
        initial_missing = self.data.isnull().sum().sum()
        logging.info("Initial missing values: %d", initial_missing)
        
        self.data = self.data.dropna()
        remaining_missing = self.data.isnull().sum().sum()
        logging.info("Remaining missing values after dropna: %d", remaining_missing)
        return self

    def fill_missing_values(self, method='ffill'):
        logging.info("Filling missing values using method: %s", method)
        initial_missing = self.data.isnull().sum().sum()
        logging.info("Initial missing values: %d", initial_missing)
        
        if method in ['ffill', 'bfill']:
            self.data = self.data.fillna(method=method)
        elif method == 'interpolate':
            self.data = self.data.interpolate()
        else:
            logging.error("Unknown method for filling missing values: %s", method)
            raise ValueError("Invalid method for filling missing values")

        remaining_missing = self.data.isnull().sum().sum()
        logging.info("Remaining missing values after fill: %d", remaining_missing)
        return self

    def handle_outliers(self, method='zscore', z_threshold=3):
        logging.info("Handling outliers using method: %s", method)
        numerical_data = self.data.select_dtypes(include=[np.number])
        
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(numerical_data))
            self.data = self.data[(z_scores < z_threshold).all(axis=1)]
        elif method == 'iqr':
            Q1 = numerical_data.quantile(0.25)
            Q3 = numerical_data.quantile(0.75)
            IQR = Q3 - Q1
            self.data = self.data[~((numerical_data < (Q1 - 1.5 * IQR)) | (numerical_data > (Q3 + 1.5 * IQR))).any(axis=1)]
        else:
            logging.error("Unknown method for handling outliers: %s", method)
            raise ValueError("Invalid method for handling outliers")

        self.outliers_removed = self.original_shape[0] - self.data.shape[0]
        logging.info("Outliers removed: %d", self.outliers_removed)
        return self

    def normalize_data(self, method='min-max'):
        logging.info("Normalizing data using method: %s", method)
        numerical_columns = self.data.select_dtypes(include=[np.number]).columns
        
        if method == 'min-max':
            self.data[numerical_columns] = (self.data[numerical_columns] - self.data[numerical_columns].min()) / (
                self.data[numerical_columns].max() - self.data[numerical_columns].min())
        elif method == 'zscore':
            self.data[numerical_columns] = (self.data[numerical_columns] - self.data[numerical_columns].mean()) / \
                                           self.data[numerical_columns].std()
        else:
            logging.error("Unknown method for data normalization: %s", method)
            raise ValueError("Invalid method for data normalization")
        
        logging.info("Data normalization complete.")
        return self

    def remove_duplicates(self):
        logging.info("Removing duplicate rows...")
        initial_rows = self.data.shape[0]
        self.data = self.data.drop_duplicates()
        final_rows = self.data.shape[0]
        logging.info("Duplicates removed: %d", initial_rows - final_rows)
        return self

    def clean_column_names(self):
        logging.info("Cleaning column names...")
        self.data.columns = self.data.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
        logging.info("Column names cleaned: %s", self.data.columns)
        return self

    def save_cleaned_data(self, filepath: str):
        logging.info("Saving cleaned data to file: %s", filepath)
        try:
            self.data.to_csv(filepath, index=False)
            logging.info("Cleaned data saved successfully.")
        except Exception as e:
            logging.error("Failed to save cleaned data: %s", str(e))
            raise

    def report_summary(self):
        logging.info("Reporting summary of the data cleaning process...")
        self.cleaned_shape = self.data.shape
        summary = {
            'Original Data Shape': self.original_shape,
            'Cleaned Data Shape': self.cleaned_shape,
            'Outliers Removed': self.outliers_removed,
        }
        logging.info("Cleaning Summary: %s", summary)
        return summary

    def full_clean(self, fill_method='ffill', outlier_method='zscore', normalize_method='min-max'):
        logging.info("Starting full data cleaning process...")
        self.validate_data()
        self.clean_column_names()
        self.remove_missing_values()
        self.handle_outliers(method=outlier_method)
        self.normalize_data(method=normalize_method)
        self.remove_duplicates()
        return self.report_summary()

# Utility functions
def load_data(file_path: str):
    logging.info("Loading data from file: %s", file_path)
    if os.path.exists(file_path):
        data = pd.read_csv(file_path)
        logging.info("Data loaded successfully with shape: %s", data.shape)
        return data
    else:
        logging.error("File not found: %s", file_path)
        raise FileNotFoundError(f"File not found: {file_path}")

def save_data(data: pd.DataFrame, file_path: str):
    logging.info("Saving data to file: %s", file_path)
    try:
        data.to_csv(file_path, index=False)
        logging.info("Data saved successfully.")
    except Exception as e:
        logging.error("Failed to save data: %s", str(e))
        raise

# Usage
if __name__ == "__main__":
    try:
        # Load raw market data
        raw_data_file = 'data/raw_market_data.csv'
        cleaned_data_file = 'data/cleaned_market_data.csv'
        data = load_data(raw_data_file)

        # Clean the data
        cleaner = DataCleaning(data)
        summary = cleaner.full_clean(fill_method='interpolate', outlier_method='iqr', normalize_method='zscore')

        # Save the cleaned data
        cleaner.save_cleaned_data(cleaned_data_file)
        logging.info("Data cleaning process completed successfully.")

    except Exception as e:
        logging.error("Data cleaning process failed: %s", str(e))