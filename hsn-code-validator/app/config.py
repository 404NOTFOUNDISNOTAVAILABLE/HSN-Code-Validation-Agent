import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = os.path.join(BASE_DIR, 'data')
MASTER_DATA_FILE = os.path.join(DATA_DIR, 'HSN_Master_Data.xlsx')

# App configuration
DEBUG = True
HOST = '127.0.0.1'
PORT = 5000