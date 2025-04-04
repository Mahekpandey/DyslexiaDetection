import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

class DataPreprocessor:
    def __init__(self, data_path):
        """Initialize the DataPreprocessor with the path to the dataset."""
        self.data_path = data_path
        self.scaler = StandardScaler()
        
    def load_data(self):
        """Load the dataset from CSV file."""
        try:
            self.data = pd.read_csv(self.data_path)
            print(f"Dataset loaded successfully with {self.data.shape[0]} rows and {self.data.shape[1]} columns")
            return True
        except Exception as e:
            print(f"Error loading dataset: {str(e)}")
            return False
    
    def handle_missing_values(self):
        """Handle missing values in the dataset."""
        # Check for missing values
        missing_values = self.data.isnull().sum()
        print("\nMissing values in each column:")
        print(missing_values)
        
        # Fill missing values with median for numerical columns
        self.data = self.data.fillna(self.data.median())
        return True
    
    def scale_features(self):
        """Scale numerical features using StandardScaler."""
        # Separate features and target
        X = self.data.drop('Dyslexic', axis=1)
        y = self.data['Dyslexic']
        
        # Scale the features
        X_scaled = self.scaler.fit_transform(X)
        
        # Convert back to DataFrame
        self.X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
        self.y = y
        
        # Save the scaler for later use
        if not os.path.exists('models'):
            os.makedirs('models')
        joblib.dump(self.scaler, 'models/scaler.pkl')
        return True
    
    def split_data(self, test_size=0.2, random_state=42):
        """Split the data into training and testing sets."""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X_scaled, self.y,
            test_size=test_size,
            random_state=random_state,
            stratify=self.y
        )
        
        print("\nData split summary:")
        print(f"Training set size: {len(self.X_train)} samples")
        print(f"Testing set size: {len(self.X_test)} samples")
        
        # Save the processed datasets
        if not os.path.exists('data/processed'):
            os.makedirs('data/processed')
            
        # Save train and test sets
        np.save('data/processed/X_train.npy', self.X_train)
        np.save('data/processed/X_test.npy', self.X_test)
        np.save('data/processed/y_train.npy', self.y_train)
        np.save('data/processed/y_test.npy', self.y_test)
        
        return True
    
    def process_data(self):
        """Run the complete data preprocessing pipeline."""
        if not self.load_data():
            return False
        
        print("\nStep 1: Handling missing values...")
        if not self.handle_missing_values():
            return False
        
        print("\nStep 2: Scaling features...")
        if not self.scale_features():
            return False
        
        print("\nStep 3: Splitting data...")
        if not self.split_data():
            return False
        
        print("\nData preprocessing completed successfully!")
        return True

if __name__ == "__main__":
    # Initialize preprocessor with the dataset path
    preprocessor = DataPreprocessor('data/dyslexia_eye_tracking_dataset (1).csv')
    
    # Run the preprocessing pipeline
    preprocessor.process_data() 