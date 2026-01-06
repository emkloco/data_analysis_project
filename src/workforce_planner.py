import pandas as pd
import numpy as np
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
        
        # relative paths to ensure it works on any machine (or circleci)
        self.RAW_PATH = 'data/raw/'
        self.PROCESSED_PAT = 'data/processed/'
        
        # make sure the output folder exists so we don't get an error later
        os.makedirs(self.PROCESSED_PATH, exist_ok=True)

    def load_and_clean_data(self):
        """
        ingests world bank and ai readiness data.
        performs cleaning on messy headers and merges datasets based on country names.
        """
        print("--- starting data pipeline ---")
        
        # ---------------------------
        # world bank gdp data
        # ---------------------------
        try:
            # world bank csvs have 4 lines of metadata at the top that we don't need
            # skiprows=4 gets us to the actual header row
            self.raw_gdp = pd.read_csv(f'{self.RAW_PATH}world_bank_gdp.csv', skiprows=4)
            
            # we only care about the country name and the latest data (2023)
            gdp_clean = self.raw_gdp[['Country Name', '2023']].copy()
            gdp_clean.columns = ['Country', 'GDP_Per_Capita']
            
            # drop countries where we don't have economic data
            gdp_clean.dropna(subset=['GDP_Per_Capita'], inplace=True)
            print(f"loaded gdp data: {len(gdp_clean)} records")
            
        except FileNotFoundError:
            print("error: world_bank_gdp.csv missing")
            return

        # ---------------------------
        # ai readiness index
        # ---------------------------
        try:
            # this file has a double header. the real column names are on the second row (index 1)
            self.raw_ai = pd.read_csv(f'{self.RAW_PATH}ai_readiness_index.csv', header=1)
            
            # rename for consistency with our internal naming convention
            self.raw_ai.rename(columns={'Total score': 'AI_Score'}, inplace=True)
            
            # grab the score and remove any empty rows
            ai_clean = self.raw_ai[['Country', 'AI_Score']].copy()
            ai_clean.dropna(subset=['AI_Score'], inplace=True)
            print(f"loaded ai data: {len(ai_clean)} records")
            
        except FileNotFoundError:
            print("error: ai_readiness_index.csv missing")
            return

        # ---------------------------
        # entity resolution
        # ---------------------------
        # the two datasets use different names for the same places (e.g. USA vs United States)
        # we map everything to the world bank standard to ensure a clean merge
        name_map = {
            "United States": "United States", 
            "USA": "United States",
            "United Kingdom": "United Kingdom",
            "UK": "United Kingdom",
            "Russia": "Russian Federation",
            "South Korea": "Korea, Rep.",
            "Egypt": "Egypt, Arab Rep.",
            "Iran": "Iran, Islamic Rep.",
            "Slovakia": "Slovak Republic",
            "Laos": "Lao PDR"
        }
        ai_clean['Country'] = ai_clean['Country'].replace(name_map)

        # inner join ensures we only analyse markets where we have info for BOTH gdp and ai
        self.clean_data = pd.merge(gdp_clean, ai_clean, on='Country', how='inner')
        print(f"merge complete: {len(self.clean_data)} shared markets")

        # ---------------------------
        # feature engineering
        # ---------------------------
        # we need to compare cost (gdp) and skill (ai) on the same scale (0 to 1)
        
        # normalise labor cost
        max_gdp = self.clean_data['GDP_Per_Capita'].max()
        self.clean_data['Labor_Cost_Norm'] = self.clean_data['GDP_Per_Capita'] / max_gdp
        
        # normalise tech readiness
        max_ai = self.clean_data['AI_Score'].max()
        self.clean_data['AI_Score_Norm'] = self.clean_data['AI_Score'] / max_ai
        
        # calculate the 'competitiveness trap'
        # logic: if a country is expensive (high gdp) but dumb (low ai), the gap is high
        self.clean_data['Trap_Score'] = (
            self.clean_data['Labor_Cost_Norm'] - self.clean_data['AI_Score_Norm']
        )
        
        # create target labels
        # 1 = avoid (trap score > 0.1), 0 = invest
        self.clean_data['Strategy_Label'] = (self.clean_data['Trap_Score'] > 0.1).astype(int)
        
        # save the processed file so we can inspect it later if needed
        save_loc = f'{self.PROCESSED_PATH}strategy_data.csv'
        self.clean_data.to_csv(save_loc, index=False)
        print(f"saved processed data to {save_loc}")

    def train_model(self):
        """
        trains a decision tree to verify that our strategic zones are statistically distinct.
        """
        if self.clean_data is None: 
            return
        
        X = self.clean_data[['Labor_Cost_Norm', 'AI_Score_Norm']]
        y = self.clean_data['Strategy_Label']
        
        # split data to test model performance on unseen examples
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # using max_depth=3 to keep the model interpretable for business stakeholders
        self.model = DecisionTreeClassifier(max_depth=3, random_state=42)
        self.model.fit(X_train, y_train)
        
        accuracy = self.model.score(X_test, y_test)
        print(f"model verification accuracy: {accuracy:.2f}")

if __name__ == "__main__":
    app = StrategicWorkforcePlanner()
    app.load_and_clean_data()
    app.train_model()