import os
from pathlib import Path

class ProjectConfig:
    def __init__(self):
        # paths
        self.ROOT_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.ROOT_DIR / "data"
        self.RAW_DIR = self.DATA_DIR / "raw"
        self.PROCESSED_DIR = self.DATA_DIR / "processed"
        self.FIGURES_DIR = self.ROOT_DIR / "reports" / "figures"
        
        for d in [self.PROCESSED_DIR, self.FIGURES_DIR]:
            d.mkdir(parents=True, exist_ok=True)

        # filenames 
        self.FILE_GDP = "world_bank_gdp.csv"
        self.FILE_INCOME = "gross_disposable_household_income.csv"
        self.FILE_HOUSING = "house_price_to_earnings_ratio.csv"
        self.FILE_GINI = "gini_index.csv"
        
        # output files
        self.OUT_NATIONAL = self.PROCESSED_DIR / "national_trends.csv"
        self.OUT_REGIONAL = self.PROCESSED_DIR / "regional_snapshot.csv"
        self.OUT_LA = self.PROCESSED_DIR / "local_authority_data.csv"
        
        # colors
        self.COLOR_GDP = '#2c3e50'    
        self.COLOR_GINI = '#c0392b'  
        self.COLOR_GOOD = '#27ae60'
        self.COLOR_BAD = '#c0392b'
        self.COLOR_INCOME = '#e67e22' 
        self.COLOR_HOUSING = '#c0392b' 
        