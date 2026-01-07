import os
from pathlib import Path

class ProjectConfig:
    def __init__(self):
        # grabbing the root directory so we don't have path issues
        self.ROOT_DIR = Path(__file__).parent.parent
        self.DATA_DIR = self.ROOT_DIR / "data"
        self.RAW_DIR = self.DATA_DIR / "raw"
        self.PROCESSED_DIR = self.DATA_DIR / "processed"
        self.FIGURES_DIR = self.ROOT_DIR / "reports" / "figures"
        
        # making sure the folders actually exist before we try to save stuff
        for d in [self.PROCESSED_DIR, self.FIGURES_DIR]:
            d.mkdir(parents=True, exist_ok=True)

        # input filenames - these need to match what's in data/raw
        self.FILE_GDP = "world_bank_gdp.csv"
        self.FILE_INCOME = "regionalgrossdisposablehouseholdincomeallitlregions2023.csv"
        self.FILE_HOUSING = "house_price_to_earnings_ratio.csv"
        
        # output filenames for the clean data
        self.OUT_NATIONAL = self.PROCESSED_DIR / "national_trends.csv"
        self.OUT_REGIONAL = self.PROCESSED_DIR / "regional_snapshot.csv"
        
        # graph colors - keeping it consistent across the report
        self.COLOR_GDP = '#1f77b4' 
        self.COLOR_INCOME = '#ff7f0e' 
        self.COLOR_TRAP = '#d62728'   