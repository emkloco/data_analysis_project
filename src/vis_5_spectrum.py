import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import ProjectConfig

class SpectrumVisualizer:
    def run(self):
        config = ProjectConfig()
        df = pd.read_csv(config.OUT_REGIONAL)
        
        latest = df[df['Year'] == df['Year'].max()].copy()
        
        # Metric: Solvency Score = Disposable Income / Housing Ratio
        # Meaning: "Real Spending Power" adjusted for housing stress.
        latest['Survival_Score'] = latest['Income'] / latest['Ratio']
        latest = latest.sort_values('Survival_Score', ascending=False)
        
        plt.figure(figsize=(12, 8))
        
        # 1. FIXED PALETTE: 'RdYlGn_r' (Reversed)
        # This makes the Top items (High Score) GREEN and Bottom items RED.
        sns.barplot(
            data=latest, 
            x='Survival_Score', 
            y='Region', 
            hue='Region', 
            palette='RdYlGn_r', 
            legend=False
        )
        
        # 2. FIXED FONTS: Much larger for readability
        plt.title('Figure 5: The Survival Spectrum', fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('Consumer Solvency Score (Income ÷ Housing Cost)', fontsize=14, fontweight='bold')
        plt.ylabel('', fontsize=12) # Hide Y label, the names are obvious
        
        # Make Region names (Y-axis) bigger
        plt.tick_params(axis='y', labelsize=14)
        plt.tick_params(axis='x', labelsize=12)
        
        
        
        plt.savefig(config.FIGURES_DIR / "05_survival_spectrum.png", dpi=300, bbox_inches='tight')
        print("Saved fig 5 (Fixed Colors & Fonts)")

if __name__ == "__main__":
    SpectrumVisualizer().run()