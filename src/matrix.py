import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import ProjectConfig

class MatrixVisualizer:
    def run(self):
        config = ProjectConfig()
        df = pd.read_csv(config.OUT_REGIONAL)
        
        # grabbing only the latest data for the snapshot
        latest_year = df['Year'].max()
        df_latest = df[df['Year'] == latest_year].copy()
        
        plt.figure(figsize=(10, 8))
        
        # plotting income vs housing cost
        sns.scatterplot(
            data=df_latest, x='Ratio', y='Income', 
            hue='Region', s=200, style='Region', legend=False
        )
        
        # drawing the median lines to split the quadrants
        med_inc = df_latest['Income'].median()
        med_rat = df_latest['Ratio'].median()
        
        plt.axhline(med_inc, color='black', linestyle='--')
        plt.axvline(med_rat, color='black', linestyle='--')
        
        # labelling the regions so we know who is who
        for i, row in df_latest.iterrows():
            plt.text(row['Ratio']+0.1, row['Income'], row['Region'], fontsize=11)
            
        # explicit strategy labels
        plt.text(df_latest['Ratio'].min(), df_latest['Income'].max(), "PREMIUM ZONES\n(High Income, Low Housing Cost)", color='green', fontweight='bold')
        plt.text(df_latest['Ratio'].max(), df_latest['Income'].min(), "COST TRAPS\n(Low Income, High Housing Cost)", color='red', fontweight='bold')
        
        plt.title(f'Fig 2: Regional Strategy Matrix ({latest_year})', fontsize=16)
        plt.xlabel('Housing Cost (Years of Salary to Buy Home)')
        plt.ylabel('Disposable Income (£)')
        
        save_path = config.FIGURES_DIR / "02_strategy_matrix.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"saved: {save_path}")

if __name__ == "__main__":
    MatrixVisualizer().run()