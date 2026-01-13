import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import ProjectConfig

class RegionalIncomeVisualizer:
    def run(self):
        config = ProjectConfig()
        print("--- Generating Figure 4: Regional Income Trends (High Contrast) ---")
        
        # 1. load data
        df = pd.read_csv(config.OUT_REGIONAL)
        
        # 2. filter for key regions
        target_regions = [
            'London', 
            'South East', 
            'West Midlands', 
            'North West', 
            'North East'
        ]
        
        subset = df[df['Region'].isin(target_regions)].copy()
        
        # 3. plot setup
        plt.figure(figsize=(12, 7))
        sns.set_theme(style="whitegrid")
        
        # 4. HIGH CONTRAST PALETTE
        # distinct colors so lines never blend together.
        custom_palette = {
            'London':        '#c0392b',  
            'South East':    '#8e44ad',  
            'West Midlands': '#f39c12',  
            'North West':    '#27ae60',  
            'North East':    "#2b41c0"   
        }
        
        sns.lineplot(
            data=subset, 
            x='Year', 
            y='Income', 
            hue='Region', 
            palette=custom_palette, 
            linewidth=3
        )
        
        # 5. styling & annotations
        plt.title('Figure 3. Real Household Disposable Income per Head by Region (1997–2023)', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.ylabel('Average Disposable Income (£)', fontsize=12, fontweight='bold')
        plt.xlabel('Year', fontsize=12, fontweight='bold')
        
        # highlight the gap at the end
        latest_year = subset['Year'].max()
        london_val = subset[(subset['Region'] == 'London') & (subset['Year'] == latest_year)]['Income'].values[0]
        ne_val = subset[(subset['Region'] == 'North East') & (subset['Year'] == latest_year)]['Income'].values[0]
        gap = london_val - ne_val
        
        # draw a line showing the gap
        plt.plot([latest_year, latest_year], [ne_val, london_val], color='grey', linestyle=':', alpha=0)
        plt.text(latest_year + 0.5, (london_val + ne_val)/2, f"", 
                 color='grey', fontweight='bold', ha='left', va='center')

        # gegend outside to prevent clutter
        plt.legend(title='Region', loc='upper left', frameon=True, framealpha=0.9, fontsize=14)
        
        # 6. save
        plt.savefig(config.FIGURES_DIR / "03_regional_income_trend.png", dpi=300, bbox_inches='tight')
        print("Saved Figure 3: Regional Income Trend (Distinct Colors)")

if __name__ == "__main__":
    RegionalIncomeVisualizer().run()