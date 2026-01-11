import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from src.config import ProjectConfig

class RealMapVisualizer:
    def run(self):
        config = ProjectConfig()
        
        # ---------------------------------------------------------
        # UPDATED: Force ALL fonts to be bold globally
        # ---------------------------------------------------------
        plt.rcParams["font.weight"] = "bold"
        plt.rcParams["axes.labelweight"] = "bold"
        plt.rcParams["axes.titleweight"] = "bold"
        
        print("--- generating real geospatial map (Full UK Fix) ---")
        
        # 1. Load Data
        df = pd.read_csv(config.OUT_REGIONAL)
        latest = df[df['Year'] == df['Year'].max()].copy()
        
        # --- THE FIX: FILL MISSING DATA ---
        median_ratio = latest['Ratio'].median()
        if latest['Ratio'].isnull().any():
            print(f"Fixing missing housing data for: {latest[latest['Ratio'].isnull()]['Region'].unique()}")
            latest['Ratio'] = latest['Ratio'].fillna(median_ratio)
        
        # Calculate Solvency
        latest['Solvency'] = latest['Income'] / latest['Ratio']
        
        # 2. Map Download
        urls = {
            "ew": "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/eurostat/ew/nuts1.json",
            "sco": "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/eurostat/sco/nuts1.json",
            "ni": "https://raw.githubusercontent.com/martinjc/UK-GeoJSON/master/json/eurostat/nir/nuts1.json"
        }
        
        gdfs = []
        for part, url in urls.items():
            try:
                gdf_part = gpd.read_file(url)
                gdfs.append(gdf_part)
            except Exception:
                pass
        
        if not gdfs:
            print("CRITICAL: No map files. Check internet.")
            return

        gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
        
        # 3. Name Matching
        gdf['clean_name'] = gdf['NUTS112NM'].str.lower().str.replace(r" \(.*\)", "", regex=True).str.strip()
        latest['clean_name'] = latest['Region'].str.lower().str.strip()
        
        name_map = {
            'eastern': 'east of england',
            'yorkshire and the humber': 'yorkshire and the humber',
            'northern ireland': 'northern ireland',
            'scotland': 'scotland'
        }
        gdf['clean_name'] = gdf['clean_name'].replace(name_map)
        
        # 4. Merge
        merged = gdf.merge(latest, left_on='clean_name', right_on='clean_name', how='left')
        
        # 5. Plot
        fig, ax = plt.subplots(1, 1, figsize=(10, 12))
        
        median_solvency = latest['Solvency'].median()
        merged['Solvency'] = merged['Solvency'].fillna(median_solvency)
        
        merged.plot(column='Solvency', ax=ax, legend=True,
                    cmap='RdYlGn', 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend_kwds={
                        'label': "Solvency Score (Income ÷ Housing Cost)", 
                        'orientation': "horizontal", 
                        'shrink': 0.8,
                        'pad': 0.02,
                        'fraction': 0.05,
                       
                    })
        
        ax.set_axis_off()
        
        # Added fontweight='bold' explicitly here as well
        plt.title(f'Figure 3. Regional Housing Affordability Across the UK', fontsize=20, fontweight='bold')
        
        save_path = config.FIGURES_DIR / "03_real_map.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved complete map to {save_path}")

if __name__ == "__main__":
    RealMapVisualizer().run()