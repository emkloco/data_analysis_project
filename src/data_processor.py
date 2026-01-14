import pandas as pd
import numpy as np
import os
from src.config import ProjectConfig

class DataProcessor:
    def __init__(self):
        self.config = ProjectConfig()

    def run(self):
        print("--- starting data processing (fixed gini) ---")
        
        # 1. load standard files
        try:
            # gdp: skip 4 rows (world bank format)
            df_gdp = pd.read_csv(self.config.RAW_DIR / self.config.FILE_GDP, skiprows=4)
            # income: header on row 1 (ONS format)
            df_income = pd.read_csv(self.config.RAW_DIR / self.config.FILE_INCOME, header=1)
            # housing: header on row 1 (ONS format)
            df_housing = pd.read_csv(self.config.RAW_DIR / self.config.FILE_HOUSING, header=1)
        except Exception as e:
            print(f"CRITICAL: Core files missing. {e}")
            return

    

        # 2. process national trends (GDP + income + housing)
        # gdp
        uk_gdp = df_gdp[df_gdp['Country Code'] == 'GBR'].melt(
            id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
            var_name='Year', value_name='GDP'
        )
        uk_gdp['Year'] = pd.to_numeric(uk_gdp['Year'], errors='coerce')
        uk_gdp = uk_gdp.dropna(subset=['GDP', 'Year'])
        uk_gdp['GDP_GBP'] = uk_gdp['GDP'] * 0.78 

        # income
        uk_income = df_income[df_income['Region name'] == 'United Kingdom'].melt(
            id_vars=['ITL', 'ITL code', 'Region name'], 
            var_name='Year', value_name='Income'
        )
        uk_income['Year'] = pd.to_numeric(uk_income['Year'], errors='coerce')
        uk_income['Income'] = pd.to_numeric(
            uk_income['Income'].astype(str).str.replace(',', ''), errors='coerce'
        )
        
        # housing
        housing_melt = df_housing.melt(
            id_vars=['Country/Region code', 'Country/Region name', 'Local authority code', 'Local authority name'],
            var_name='Year', value_name='Ratio'
        )
        housing_melt['Year'] = pd.to_numeric(housing_melt['Year'], errors='coerce')
        housing_melt['Ratio'] = pd.to_numeric(housing_melt['Ratio'], errors='coerce')
        uk_housing = housing_melt.groupby('Year')['Ratio'].median().reset_index()
        
        # merge national
        national = pd.merge(uk_gdp[['Year', 'GDP_GBP']], uk_income[['Year', 'Income']], on='Year', how='outer')
        national = pd.merge(national, uk_housing, on='Year', how='outer')
        
        # merge gini (safe merge)
        if not uk_gini.empty:
            national = pd.merge(national, uk_gini[['Year', 'Gini']], on='Year', how='left')
        
        # guarantee gini column exists (fill NaN if missing)
        if 'Gini' not in national.columns:
            national['Gini'] = np.nan
            
        national = national.sort_values('Year')

        # 3. process regional data
        housing_reg = housing_melt.groupby(['Country/Region name', 'Year'])['Ratio'].median().reset_index()
        housing_reg.rename(columns={'Country/Region name': 'Region'}, inplace=True)
        
        income_reg = df_income[
            (df_income['Region name'] != 'United Kingdom') & 
            (df_income['ITL'] == 'ITL1')
        ].melt(
            id_vars=['ITL', 'ITL code', 'Region name'], 
            var_name='Year', value_name='Income'
        )
        income_reg.rename(columns={'Region name': 'Region'}, inplace=True)
        income_reg['Year'] = pd.to_numeric(income_reg['Year'], errors='coerce')
        income_reg['Income'] = pd.to_numeric(
            income_reg['Income'].astype(str).str.replace(',', ''), errors='coerce'
        )
        income_reg = income_reg.dropna(subset=['Income'])
        
        # clean keys
        housing_reg['key'] = housing_reg['Region'].str.lower().str.strip()
        income_reg['key'] = income_reg['Region'].str.lower().str.strip()
        
        regional = pd.merge(income_reg, housing_reg, on=['key', 'Year'], how='inner')
        regional['Region'] = regional['Region_x']
        regional = regional[['Region', 'Year', 'Income', 'Ratio']]
        
        # save
        national.to_csv(self.config.OUT_NATIONAL, index=False)
        regional.to_csv(self.config.OUT_REGIONAL, index=False)
        housing_melt.dropna(subset=['Ratio']).to_csv(self.config.OUT_LA, index=False)
        
        print("data processing complete. 'Gini' column guaranteed.")

if __name__ == "__main__":
    DataProcessor().run()