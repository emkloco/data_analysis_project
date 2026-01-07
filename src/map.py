import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import ProjectConfig

class MapVisualizer:
    def run(self):
        config = ProjectConfig()
        df = pd.read_csv(config.OUT_REGIONAL)
        
        # calculating 'true wealth' score
        # income divided by housing burden
        latest_year = df['Year'].max()
        df_latest = df[df['Year'] == latest_year].copy()
        df_latest['True_Wealth_Score'] = df_latest['Income'] / df_latest['Ratio']
        
        # sorting so best is on top
        df_latest = df_latest.sort_values('True_Wealth_Score', ascending=False)
        
        plt.figure(figsize=(12, 8))
        
        # simple color logic: top 3 green, bottom 3 red
        palette = ['grey'] * len(df_latest)
        for i in range(3): palette[i] = 'green'
        for i in range(len(df_latest)-3, len(df_latest)): palette[i] = 'red'
        
        sns.barplot(data=df_latest, x='True_Wealth_Score', y='Region', palette=palette)
        
        plt.title(f'Fig 3: The "True Wealth" Leaderboard ({latest_year})\n(Disposable Income Adjusted for Housing Costs)', fontsize=16)
        plt.xlabel('Real Purchasing Power Score')
        
        save_path = config.FIGURES_DIR / "03_wealth_map.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"saved: {save_path}")

if __name__ == "__main__":
    MapVisualizer().run()