import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import ProjectConfig

class WalletSqueezeVisualizer:
    def run(self):
        config = ProjectConfig()
        print("--- Generating Comparison Graph: The Wallet Squeeze ---")
        
        # 1. Load Data
        df = pd.read_csv(config.OUT_NATIONAL)
        plot_df = df.dropna(subset=['Income', 'Ratio']).sort_values('Year')
        
        # 2. Setup Dual Axis Plot
        fig, ax1 = plt.subplots(figsize=(12, 7))
        sns.set_theme(style="whitegrid")
        
        # Axis 1: Disposable Income (The "Cash")
        color_inc = config.COLOR_INCOME # Orange/Pumpkin
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Avg. Disposable Income (£)', color=color_inc, fontsize=12, fontweight='bold')
        ax1.plot(plot_df['Year'], plot_df['Income'], color=color_inc, linewidth=3, label='Disposable Income (Cash)')
        ax1.tick_params(axis='y', labelcolor=color_inc)
        ax1.grid(False)
        
        # Axis 2: Housing Cost Ratio (The "Drain")
        ax2 = ax1.twinx()
        color_house = config.COLOR_HOUSING # Red
        ax2.set_ylabel('Housing Cost Ratio (Price/Earnings)', color=color_house, fontsize=12, fontweight='bold')
        ax2.plot(plot_df['Year'], plot_df['Ratio'], color=color_house, linewidth=3, linestyle='--', label='Housing Cost Burden')
        ax2.tick_params(axis='y', labelcolor=color_house)
        
        # 3. Add "Crisis Events" Annotation
        # Highlight 2008 and 2022 to show responsiveness
        plt.axvline(2008, color='grey', linestyle=':', alpha=0.5)
        plt.text(2008.5, plot_df['Ratio'].max()*0.95, "2008 Crash", fontsize=10, color='grey')
        
        plt.axvline(2022, color='grey', linestyle=':', alpha=0.5)
        plt.text(2022.5, plot_df['Ratio'].max()*0.95, "Cost of Living\nCrisis", fontsize=10, color='grey')
        
        # 4. A+ Title and Styling
        plt.title('Figure 4: The "Wallet Squeeze": Temporal Divergence Between\nHousehold Income and Asset Prices (1997–2023)', 
                 fontsize=14, fontweight='bold', pad=20)
        
        # Combined Legend
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', frameon=True)
        
        # Save
        plt.savefig(config.FIGURES_DIR / "04_wallet_squeeze_trend.png", dpi=300, bbox_inches='tight')
        print("Saved Figure 4: The Wallet Squeeze")

if __name__ == "__main__":
    WalletSqueezeVisualizer().run()