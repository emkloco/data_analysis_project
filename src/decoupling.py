import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import ProjectConfig

class DecouplingVisualizer:
    def run(self):
        config = ProjectConfig()
        df = pd.read_csv(config.OUT_NATIONAL)
        
        # indexing both lines to 100 so we can compare growth rates
        base_year = df['Year'].min()
        base_gdp = df.loc[df['Year'] == base_year, 'GDP'].values[0]
        base_inc = df.loc[df['Year'] == base_year, 'Income'].values[0]
        
        df['GDP_Index'] = (df['GDP'] / base_gdp) * 100
        df['Income_Index'] = (df['Income'] / base_inc) * 100
        
        plt.figure(figsize=(12, 6))
        sns.set_theme(style="whitegrid")
        
        # plotting the two lines
        plt.plot(df['Year'], df['GDP_Index'], label='GDP per Capita (Corporate Wealth)', color=config.COLOR_GDP, linewidth=3)
        plt.plot(df['Year'], df['Income_Index'], label='Disposable Income (Customer Cash)', color=config.COLOR_INCOME, linewidth=3, linestyle='--')
        
        # shading the gap to emphasize the problem
        plt.fill_between(df['Year'], df['GDP_Index'], df['Income_Index'], color='grey', alpha=0.1, label='The Wealth Gap')
        
        plt.title('Fig 1: The Great Decoupling (2000-2023)', fontsize=16)
        plt.ylabel('Growth Index (1997 = 100)')
        plt.legend()
        
        save_path = config.FIGURES_DIR / "01_decoupling_trend.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"saved: {save_path}")

if __name__ == "__main__":
    DecouplingVisualizer().run()