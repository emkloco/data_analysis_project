import pandas as pd
import numpy as np
import os
from src.config import ProjectConfig

class DataProcessor:
    def __init__(self):
        self.config = ProjectConfig()

    def run(self):
        print("--- starting data processing (fixed gini) ---")
        
        # 1. Load Standard Files
        try:
            # GDP: Skip 4 rows (World Bank Format)
            df_gdp = pd.read_csv(self.config.RAW_DIR / self.config.FILE_GDP, skiprows=4)
            # Income: Header on row 1 (ONS Format)
            df_income = pd.read_csv(self.config.RAW_DIR / self.config.FILE_INCOME, header=1)
            # Housing: Header on row 1 (ONS Format)
            df_housing = pd.read_csv(self.config.RAW_DIR / self.config.FILE_HOUSING, header=1)
        except Exception as e:
            print(f"CRITICAL: Core files missing. {e}")
            return

        # 2. Load Gini File (Specific Logic)
        uk_gini = pd.DataFrame(columns=['Year', 'Gini'])
        gini_path = self.config.RAW_DIR / self.config.FILE_GINI
        
        # If specific file doesn't exist, search for it
        if not gini_path.exists():
            for f in os.listdir(self.config.RAW_DIR):
                if 'gini' in f.lower() and f.endswith('.csv'):
                    gini_path = self.config.RAW_DIR / f
                    print(f"Found Gini file: {f}")
                    break
        
        if gini_path.exists():
            try:
                # FIX: Explicitly skip 4 rows, just like GDP file
                print(f"Loading Gini from {gini_path.name}...")
                df_gini = pd.read_csv(gini_path, skiprows=4)
                
                # Check if it loaded correctly (look for 'Country Code')
                if 'Country Code' in df_gini.columns:
                    # Filter for UK
                    uk_row = df_gini[df_gini['Country Code'] == 'GBR']
                    
                    if not uk_row.empty:
                        # Reshape from Wide (1990, 1991...) to Long
                        id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
                        val_vars = [c for c in uk_row.columns if c.isdigit()] # Only year columns
                        
                        uk_gini = uk_row.melt(id_vars=id_vars, value_vars=val_vars, var_name='Year', value_name='Gini')
                        
                        # Clean
                        uk_gini['Year'] = pd.to_numeric(uk_gini['Year'], errors='coerce')
                        uk_gini['Gini'] = pd.to_numeric(uk_gini['Gini'], errors='coerce')
                        uk_gini = uk_gini.dropna(subset=['Gini', 'Year'])
                        
                        print(f"Loaded {len(uk_gini)} years of Gini data.")
                    else:
                        print("WARNING: Gini file loaded, but 'GBR' row not found.")
                else:
                    print("WARNING: Gini file structure unrecognized (expected 'Country Code' in header).")
                    
            except Exception as e:
                print(f"Error processing Gini file: {e}")
        else:
            print("WARNING: Gini file not found.")

        # 3. Process National Trends (GDP + Income + Housing)
        # GDP
        uk_gdp = df_gdp[df_gdp['Country Code'] == 'GBR'].melt(
            id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
            var_name='Year', value_name='GDP'
        )
        uk_gdp['Year'] = pd.to_numeric(uk_gdp['Year'], errors='coerce')
        uk_gdp = uk_gdp.dropna(subset=['GDP', 'Year'])
        uk_gdp['GDP_GBP'] = uk_gdp['GDP'] * 0.78 

        # Income
        uk_income = df_income[df_income['Region name'] == 'United Kingdom'].melt(
            id_vars=['ITL', 'ITL code', 'Region name'], 
            var_name='Year', value_name='Income'
        )
        uk_income['Year'] = pd.to_numeric(uk_income['Year'], errors='coerce')
        uk_income['Income'] = pd.to_numeric(
            uk_income['Income'].astype(str).str.replace(',', ''), errors='coerce'
        )
        
        # Housing
        housing_melt = df_housing.melt(
            id_vars=['Country/Region code', 'Country/Region name', 'Local authority code', 'Local authority name'],
            var_name='Year', value_name='Ratio'
        )
        housing_melt['Year'] = pd.to_numeric(housing_melt['Year'], errors='coerce')
        housing_melt['Ratio'] = pd.to_numeric(housing_melt['Ratio'], errors='coerce')
        uk_housing = housing_melt.groupby('Year')['Ratio'].median().reset_index()
        
        # Merge National
        national = pd.merge(uk_gdp[['Year', 'GDP_GBP']], uk_income[['Year', 'Income']], on='Year', how='outer')
        national = pd.merge(national, uk_housing, on='Year', how='outer')
        
        # Merge Gini (Safe Merge)
        if not uk_gini.empty:
            national = pd.merge(national, uk_gini[['Year', 'Gini']], on='Year', how='left')
        
        # GUARANTEE Gini column exists (Fill NaN if missing)
        if 'Gini' not in national.columns:
            national['Gini'] = np.nan
            
        national = national.sort_values('Year')

        # 4. Process Regional Data
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
        
        # Clean Keys
        housing_reg['key'] = housing_reg['Region'].str.lower().str.strip()
        income_reg['key'] = income_reg['Region'].str.lower().str.strip()
        
        regional = pd.merge(income_reg, housing_reg, on=['key', 'Year'], how='inner')
        regional['Region'] = regional['Region_x']
        regional = regional[['Region', 'Year', 'Income', 'Ratio']]
        
        # Save
        national.to_csv(self.config.OUT_NATIONAL, index=False)
        regional.to_csv(self.config.OUT_REGIONAL, index=False)
        housing_melt.dropna(subset=['Ratio']).to_csv(self.config.OUT_LA, index=False)
        
        print("data processing complete. 'Gini' column guaranteed.")

if __name__ == "__main__":
    DataProcessor().run()