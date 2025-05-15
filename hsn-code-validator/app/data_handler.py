import pandas as pd
import os
from app.config import MASTER_DATA_FILE

class HSNDataHandler:
    """
    Handles the loading and preprocessing of HSN code data from Excel file
    """
    _instance = None
    
    def __new__(cls):
        # Singleton pattern to ensure data is loaded only once
        if cls._instance is None:
            cls._instance = super(HSNDataHandler, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        """Initialize the data handler by loading the Excel file"""
        print(f"Looking for master data file at: {MASTER_DATA_FILE}")
        if not os.path.exists(MASTER_DATA_FILE):
            raise FileNotFoundError(f"Master data file not found: {MASTER_DATA_FILE}")
    
        # Load the Excel file with additional error handling
        try:
            print("Attempting to read Excel file...")
            self.df = pd.read_excel(MASTER_DATA_FILE)
            print(f"Excel file loaded successfully. Columns: {self.df.columns.tolist()}")
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            raise
    
        # Try cleaning column names
        self.df.columns = self.df.columns.str.strip()
    
        # Ensure the required columns exist
        required_cols = ['HSNCode', 'Description']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            print(f"Missing columns: {missing_cols}")
            print(f"Available columns: {self.df.columns.tolist()}")
            raise ValueError(f"Excel file must contain 'HSNCode' and 'Description' columns. Missing: {missing_cols}")
    
        # Convert HSN codes to string type for consistent handling
        self.df['HSNCode'] = self.df['HSNCode'].astype(str)
        
        # Create a dictionary for faster lookups
        self.hsn_dict = dict(zip(self.df['HSNCode'], self.df['Description']))
        
        # Create a set of all valid HSN codes for faster validation
        self.valid_codes = set(self.df['HSNCode'])
        
        # Extract the unique lengths of HSN codes to validate format
        self.valid_lengths = set(len(code) for code in self.valid_codes)
        
        print(f"Loaded {len(self.valid_codes)} HSN codes with lengths: {sorted(self.valid_lengths)}")
    
    def get_description(self, hsn_code):
        """
        Get the description for a given HSN code
        
        Args:
            hsn_code (str): The HSN code to look up
            
        Returns:
            str: The description if found, None otherwise
        """
        return self.hsn_dict.get(str(hsn_code))
    
    def is_valid_code(self, hsn_code):
        """
        Check if the HSN code exists in the master data
        
        Args:
            hsn_code (str): The HSN code to check
            
        Returns:
            bool: True if the code exists, False otherwise
        """
        return str(hsn_code) in self.valid_codes
    
    def get_parent_codes(self, hsn_code):
        """
        Generate all parent codes for a given HSN code
        
        Args:
            hsn_code (str): The HSN code to analyze
            
        Returns:
            list: List of parent codes (from most specific to least)
        """
        hsn_code = str(hsn_code)
        parent_codes = []
        
        # Generate parent codes by reducing digits
        for i in range(len(hsn_code) - 2, 0, -2):
            if i > 0:
                parent = hsn_code[:i]
                parent_codes.append(parent)
        
        return parent_codes
    
    def validate_parent_hierarchy(self, hsn_code):
        """
        Check if the parent hierarchy of an HSN code is valid
        
        Args:
            hsn_code (str): The HSN code to validate
            
        Returns:
            dict: Dictionary with validation status and relevant parent information
        """
        hsn_code = str(hsn_code)
        parents = self.get_parent_codes(hsn_code)
        
        result = {
            "valid": True,
            "invalid_parents": [],
            "valid_parents": []
        }
        
        for parent in parents:
            if self.is_valid_code(parent):
                result["valid_parents"].append({
                    "code": parent,
                    "description": self.get_description(parent)
                })
            else:
                result["valid"] = False
                result["invalid_parents"].append(parent)
        
        return result