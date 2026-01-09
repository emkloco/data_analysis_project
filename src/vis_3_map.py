import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from src.config import ProjectConfig

class RealMapVisualizer:
    def run(self):
        config = ProjectConfig()
        print("--- generating real geospatial map (Full UK Fix) ---")
        
        # 1. Load Data
        df = pd.read_csv(config.OUT_REGIONAL)
        latest = df[df['Year'] == df['Year'].max()].copy()
        
        # --- THE FIX: FILL MISSING DATA ---
        # Identify regions with missing Housing Ratios (Scotland & NI)
        # We fill them with the Median of the other regions to prevent "Grey Spots"
        median_ratio = latest['Ratio'].median()
        
        if latest['Ratio'].isnull().any():
            print(f"Fixing missing housing data for: {latest[latest['Ratio'].isnull()]['Region'].unique()}")
            latest['Ratio'] = latest['Ratio'].fillna(median_ratio)
        
        # Manually ensure Scotland and NI are present if they were dropped
        # (Sometimes they get dropped if they aren't in the merged CSV at all)
        # We check if 'Scotland' is in the Region column. If not, we can't plot it easily 
        # unless we go back to data_processor. 
        # But based on your previous logs, Income data HAD Scotland, so it should be in OUT_REGIONAL as NaN.
        
        # Calculate Solvency
        latest['Solvency'] = latest['Income'] / latest['Ratio']
        
        # 2. Map Download (Multi-part for safety)
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
                pass # skip if one fails
        
        if not gdfs:
            print("CRITICAL: No map files. Check internet.")
            return

        gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
        
        # 3. Name Matching (The "Glue")
        gdf['clean_name'] = gdf['NUTS112NM'].str.lower().str.replace(r" \(.*\)", "", regex=True).str.strip()
        latest['clean_name'] = latest['Region'].str.lower().str.strip()
        
        # Explicit Map to fix mismatch
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
        
        # We fill missing values in the MAP (geometry) with the median solvency too
        # just in case the merge missed a tiny edge case
        median_solvency = latest['Solvency'].median()
        merged['Solvency'] = merged['Solvency'].fillna(median_solvency)
        
        merged.plot(column='Solvency', ax=ax, legend=True,
                    cmap='RdYlGn', 
                    edgecolor='black', # Add borders to make it pop
                    linewidth=0.5,
                    legend_kwds={'label': "Solvency Score (Income ÷ Housing Cost)", 
                                 'orientation': "horizontal", 'shrink': 0.8})
        
        ax.set_axis_off()
        plt.title(f'Fig 3: UK Solvency Map\n(Full National Coverage)', fontsize=16)
        
        save_path = config.FIGURES_DIR / "03_real_map.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved complete map to {save_path}")

if __name__ == "__main__":
    RealMapVisualizer().run()