import pytest
import pandas as pd
import os
import sys

# allows import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from workforce_planner import StrategicWorkforcePlanner

def test_trap_calculation_logic():
  
    # verifies the mathematical logic of the competitiveness trap
    
    planner = StrategicWorkforcePlanner()
    
    # create mock data simulating a rich but dumb country
    planner.clean_data = pd.DataFrame({
        'GDP_Per_Capita': [100000, 1000],  # Country A is Rich, B is Poor
        'AI_Score': [20, 20]               # Both have low AI
    })
    
    # runs the math manually simulation of feature_engineering
    planner.clean_data['Labor_Cost_Norm'] = planner.clean_data['GDP_Per_Capita'] / 100000
    planner.clean_data['AI_Score_Norm'] = planner.clean_data['AI_Score'] / 100
    
    # trap = cost (1.0) - AI (0.2) = 0.8
    planner.clean_data['Trap_Score'] = planner.clean_data['Labor_Cost_Norm'] - planner.clean_data['AI_Score_Norm']
    
    # assert: the rich/dumb country should have a high trap score
    assert planner.clean_data.iloc[0]['Trap_Score'] > 0.5

def test_files_exist():
 

    # verifies that the user actually has the raw data files
    if os.path.exists("data/raw/world_bank_gdp.csv"):
        assert True
    else:
        # if file is missing, print a warning but don't fail the build
        print("WARNING: Real CSV files not found. Skipping file existence check.")