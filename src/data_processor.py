import pandas as pd
import numpy as np
from src.config import ProjectConfig

class DataProcessor:
    def __init__(self):
        self.config = ProjectConfig()

    def run(self):
        print("--- starting data processing ---")
        
        # reading the raw files
        # skip 4 lines for world bank, 1 line for ons
        df_gdp = pd.read_csv(self.config.RAW_DIR / self.config.FILE_GDP, skiprows=4)
        df_income = pd.read_csv(self.config.RAW_DIR / self.config.FILE_INCOME, header=1)
        df_housing = pd.read_csv(self.config.RAW_DIR / self.config.FILE_HOUSING, header=1)
        
        # step 1: national trends (the decoupling graph)
        # extracting uk gdp and fixing the weird wide format
        uk_gdp = df_gdp[df_gdp['Country Code'] == 'GBR'].melt(
            id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
            var_name='Year', value_name='GDP'
        )
        uk_gdp['Year'] = pd.to_numeric(uk_gdp['Year'], errors='coerce')
        uk_gdp = uk_gdp.dropna(subset=['GDP', 'Year'])
        
        # extracting total uk income
        uk_income = df_income[df_income['Region name'] == 'United Kingdom'].melt(
            id_vars=['ITL', 'ITL code', 'Region name'], 
            var_name='Year', value_name='Income'
        )
        uk_income['Year'] = pd.to_numeric(uk_income['Year'], errors='coerce')
        # stripping commas because python hates "10,500"
        uk_income['Income'] = uk_income['Income'].astype(str).str.replace(',', '').astype(float)
        
        # extracting national housing ratio (median)
        housing_melt = df_housing.melt(
            id_vars=['Country/Region code', 'Country/Region name', 'Local authority code', 'Local authority name'],
            var_name='Year', value_name='Ratio'
        )
        housing_melt['Year'] = pd.to_numeric(housing_melt['Year'], errors='coerce')
        housing_melt['Ratio'] = pd.to_numeric(housing_melt['Ratio'], errors='coerce')
        
        uk_housing = housing_melt.groupby('Year')['Ratio'].median().reset_index()
        
        # merging them all into one timeline
        national = pd.merge(uk_gdp[['Year', 'GDP']], uk_income[['Year', 'Income']], on='Year')
        national = pd.merge(national, uk_housing, on='Year')
        
        # step 2: regional data (for the map/matrix)
        # we need to group the housing data by region to match income data
        housing_reg = housing_melt.groupby(['Country/Region name', 'Year'])['Ratio'].median().reset_index()
        housing_reg.rename(columns={'Country/Region name': 'Region'}, inplace=True)
        
        # filtering out the "total uk" row so we just get regions
        income_reg = df_income[df_income['Region name'] != 'United Kingdom'].melt(
            id_vars=['Region name'], var_name='Year', value_name='Income'
        )
        income_reg.rename(columns={'Region name': 'Region'}, inplace=True)
        income_reg['Year'] = pd.to_numeric(income_reg['Year'], errors='coerce')
        income_reg['Income'] = income_reg['Income'].astype(str).str.replace(',', '').astype(float)
        
        # joining regional income with regional housing costs
        regional = pd.merge(income_reg, housing_reg, on=['Region', 'Year'])
        
        # dumping to csv
        national.to_csv(self.config.OUT_NATIONAL, index=False)
        regional.to_csv(self.config.OUT_REGIONAL, index=False)
        print(f"saved processed data to {self.config.PROCESSED_DIR}")

if __name__ == "__main__":
    DataProcessor().run()