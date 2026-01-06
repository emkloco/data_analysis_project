import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import os

class StrategicWorkforcePlanner:
    """
    strategic intelligence tool for market efficiency analysis.
    handles data ingestion, cleaning, entity resolution, and decision tree logic.
    """
    
    def __init__(self):
        self.raw_gdp = None
        self.raw_ai = None
        self.clean_data = None
        self.model = None
        
        # relative paths
        self.RAW_PATH = 'data/raw/'
        self.PROCESSED_PATH = 'data/processed/'
        self.FIGURES_PATH = 'reports/figures/'
        
        # ensure output folders exist
        os.makedirs(self.PROCESSED_PATH, exist_ok=True)
        os.makedirs(self.FIGURES_PATH, exist_ok=True)

    def load_and_clean_data(self):
        """
        ingests world bank and ai readiness data.
        performs cleaning on messy headers and merges datasets.
        """
        print("--- starting data pipeline ---")
        
        # 1. world bank gdp data
        try:
            # skip 4 rows of metadata
            # encoding='latin1' handles special characters in country names
            self.raw_gdp = pd.read_csv(f'{self.RAW_PATH}world_bank_gdp.csv', skiprows=4, encoding='latin1')
            
            # grab country and 2023 data
            gdp_clean = self.raw_gdp[['Country Name', '2023']].copy()
            gdp_clean.columns = ['Country', 'GDP_Per_Capita']
            gdp_clean.dropna(subset=['GDP_Per_Capita'], inplace=True)
            print(f"loaded gdp data: {len(gdp_clean)} records")
            
        except FileNotFoundError:
            print("error: world_bank_gdp.csv missing")
            return

        # 2. ai readiness index
        try:
            # dual header, read from row 1
            # encoding='latin1' prevents UnicodeDecodeError
            self.raw_ai = pd.read_csv(f'{self.RAW_PATH}ai_readiness_index.csv', header=1, encoding='latin1')
            self.raw_ai.rename(columns={'Total score': 'AI_Score'}, inplace=True)
            
            ai_clean = self.raw_ai[['Country', 'AI_Score']].copy()
            ai_clean.dropna(subset=['AI_Score'], inplace=True)
            print(f"loaded ai data: {len(ai_clean)} records")
            
        except FileNotFoundError:
            print("error: ai_readiness_index.csv missing")
            return

        # 3. entity resolution
        name_map = {
            "United States": "United States", "USA": "United States",
            "United Kingdom": "United Kingdom", "UK": "United Kingdom",
            "Russia": "Russian Federation", "South Korea": "Korea, Rep.",
            "Egypt": "Egypt, Arab Rep.", "Iran": "Iran, Islamic Rep.",
            "Slovakia": "Slovak Republic", "Laos": "Lao PDR"
        }
        ai_clean['Country'] = ai_clean['Country'].replace(name_map)

        self.clean_data = pd.merge(gdp_clean, ai_clean, on='Country', how='inner')
        print(f"merge complete: {len(self.clean_data)} shared markets")

        # 4. feature engineering
        max_gdp = self.clean_data['GDP_Per_Capita'].max()
        self.clean_data['Labor_Cost_Norm'] = self.clean_data['GDP_Per_Capita'] / max_gdp
        
        max_ai = self.clean_data['AI_Score'].max()
        self.clean_data['AI_Score_Norm'] = self.clean_data['AI_Score'] / max_ai
        
        # trap score calculation
        self.clean_data['Trap_Score'] = (
            self.clean_data['Labor_Cost_Norm'] - self.clean_data['AI_Score_Norm']
        )
        
        # label: 1 (avoid), 0 (invest)
        self.clean_data['Strategy_Label'] = (self.clean_data['Trap_Score'] > 0.1).astype(int)
        
        self.clean_data.to_csv(f'{self.PROCESSED_PATH}strategy_data.csv', index=False)
        print(f"saved processed data")

    def train_model(self):
        """
        verifies the strategy using a decision tree.
        """
        if self.clean_data is None: return
        
        X = self.clean_data[['Labor_Cost_Norm', 'AI_Score_Norm']]
        y = self.clean_data['Strategy_Label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        self.model = DecisionTreeClassifier(max_depth=3, random_state=42)
        self.model.fit(X_train, y_train)
        
        accuracy = self.model.score(X_test, y_test)
        print(f"model verification accuracy: {accuracy:.2f}")

    def visualize_strategy(self):
        """
        generates the key figure: a quadrant analysis of cost vs capability.
        saves the figure to reports/figures/strategy_matrix.png
        """
        if self.clean_data is None: return
        
        print("--- generating strategy matrix ---")
        plt.figure(figsize=(10, 6))
        
        # use seaborn for a professional aesthetic
        # x = cost (gdp), y = tech (ai), hue = our strategy label
        sns.scatterplot(
            data=self.clean_data,
            x='GDP_Per_Capita',
            y='AI_Score',
            hue='Strategy_Label',
            palette={0: 'green', 1: 'red'},
            s=100, # dot size
            alpha=0.7
        )
        
        # add quadrant lines
        plt.axvline(x=self.clean_data['GDP_Per_Capita'].mean(), color='grey', linestyle='--')
        plt.axhline(y=self.clean_data['AI_Score'].mean(), color='grey', linestyle='--')
        
        plt.title('Global Strategy Matrix: Cost vs Capability')
        plt.xlabel('Labor Cost (GDP Per Capita $)')
        plt.ylabel('AI Readiness Score')
        plt.legend(title='Recommendation', labels=['Invest', 'Avoid'])
        plt.grid(True, alpha=0.3)
        
        # save high-res image
        save_path = f'{self.FIGURES_PATH}strategy_matrix.png'
        plt.savefig(save_path, dpi=300)
        print(f"saved key figure to {save_path}")

if __name__ == "__main__":
    app = StrategicWorkforcePlanner()
    app.load_and_clean_data()
    app.train_model()
    app.visualize_strategy()