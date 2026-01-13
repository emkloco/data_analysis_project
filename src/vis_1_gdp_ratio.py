import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import scipy.stats as stats
from src.config import ProjectConfig

class GdpRatioVisualizer:
    def run(self):
        config = ProjectConfig()
        print("--- Generating GDP vs Housing Ratio Reality Checks ---")
        
        # 1. Load Data
        df = pd.read_csv(config.OUT_NATIONAL)
        
        # 2. Clean Data (Ensure we have both metrics)
        plot_df = df.dropna(subset=['GDP_GBP', 'Ratio']).sort_values('Year')
        
        if len(plot_df) < 2:
            print("CRITICAL: Not enough data points.")
            return

        # ==========================================
        # FIGURE 7: SCATTER PLOT (The Correlation)
        # ==========================================
        plt.figure(figsize=(10, 7))
        sns.set_theme(style="ticks")
        
        # Calculate Stats
        r, p_value = stats.pearsonr(plot_df['GDP_GBP'], plot_df['Ratio'])
        r_squared = r**2
        
        # Scatter with Regression Line
        # We expect a positive correlation (Rich Country = Expensive Houses)
        ax = sns.regplot(
            data=plot_df, 
            x='GDP_GBP', 
            y='Ratio',
            scatter_kws={'s': 100, 'alpha': 0.7, 'color': config.COLOR_GDP, 'edgecolor': 'white'},
            line_kws={'color': config.COLOR_HOUSING, 'linewidth': 3},
            ci=95
        )
        
        # Labels
        plt.title('Figure 4. GDP per Capita and Housing Affordability in the UK', fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Real GDP per Capita (£)', fontsize=12, fontweight='bold')
        plt.ylabel('Housing Price to Income Ratio', fontsize=12, fontweight='bold')
        
        # Stats Box
        stats_text = (
            f"Correlation ($r$): {r:.2f}\n"
            f"R-Squared: {r_squared:.2f}\n"
            f"P-Value: < 0.001"
            
        )
        plt.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=14,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='lightgrey'))
        
        # Annotate Years
        min_pt = plot_df.loc[plot_df['GDP_GBP'].idxmin()]
        max_pt = plot_df.loc[plot_df['GDP_GBP'].idxmax()]
        plt.text(min_pt['GDP_GBP'], min_pt['Ratio']+0.2, str(int(min_pt['Year'])), fontweight='bold', color=config.COLOR_GDP)
        plt.text(max_pt['GDP_GBP'], max_pt['Ratio']-0.2, str(int(max_pt['Year'])), fontweight='bold', color=config.COLOR_GDP)
        
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.savefig(config.FIGURES_DIR / "04_gdp_ratio_scatter.png", dpi=300, bbox_inches='tight')
        print("Saved Figure 4: GDP vs Ratio Scatter")

       
        
        fig, ax1 = plt.subplots(figsize=(12, 7))
        sns.set_theme(style="whitegrid")
        
        # Left Axis: GDP
        color_1 = config.COLOR_GDP
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('GDP per Capita (£)', color=color_1, fontsize=12, fontweight='bold')
        ax1.plot(plot_df['Year'], plot_df['GDP_GBP'], color=color_1, linewidth=4, label='GDP (Economic Output)')
        ax1.tick_params(axis='y', labelcolor=color_1)
        ax1.grid(False)
        
        # Right Axis: Housing Ratio
        ax2 = ax1.twinx() 
        color_2 = config.COLOR_HOUSING
        ax2.set_ylabel('Housing Affordability Ratio (Lower is Better)', color=color_2, fontsize=12, fontweight='bold')
        ax2.plot(plot_df['Year'], plot_df['Ratio'], color=color_2, linewidth=4, linestyle='--', label='Housing Cost Ratio')
        ax2.tick_params(axis='y', labelcolor=color_2)
        ax2.grid(True, alpha=0.3)
        
        plt.title('The Broken Link: Economic Growth vs Housing Difficulty', fontsize=16, fontweight='bold')
        
        # Combined Legend
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=11)
        
        

if __name__ == "__main__":
    GdpRatioVisualizer().run()