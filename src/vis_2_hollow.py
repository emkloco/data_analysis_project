import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import ProjectConfig

class HollowVisualizer:
    def run(self):
        config = ProjectConfig()
        df = pd.read_csv(config.OUT_LA)
        
        plt.figure(figsize=(12, 6))
        plt.rcParams["axes.titleweight"] = "bold"
        sns.set_theme(style="whitegrid")
        
        # comparing 2002 vs 2022 
        sns.kdeplot(data=df[df['Year'] == 2002], x='Ratio', color=config.COLOR_GOOD, fill=True, alpha=0.3, label='2002 Distribution (Affordable)')
        sns.kdeplot(data=df[df['Year'] == 2022], x='Ratio', color=config.COLOR_BAD, fill=True, alpha=0.3, label='2022 Distribution (Crisis)')
        
        plt.title('Figure 2. Shifts in the UK Income Distribution Over Time', fontsize=16)
        plt.xlabel('Housing Cost Ratio (Price / Income)')
        plt.xlim(0, 20)
        plt.legend(fontsize=14)
        
        plt.text(4, 0.15, "", color=config.COLOR_GOOD, ha='center')
        plt.text(12, 0.05, "", color=config.COLOR_BAD, ha='center')
        
        plt.savefig(config.FIGURES_DIR / "02_hollow_middle.png", dpi=300, bbox_inches='tight')
        print("saved fig 2")

if __name__ == "__main__":
    HollowVisualizer().run()