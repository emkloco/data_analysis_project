import pytest
import pandas as pd
import sys
import os

# this line adds the 'src' folder to Python's path so it can find your code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from workforce_planner import StrategicWorkforcePlanner

def test_initialization():
    """Checks if the class starts up correctly."""
    planner = StrategicWorkforcePlanner()
    assert planner.data is None
    assert planner.model is None

def test_data_generation():
    """Checks if the mock data loader actually creates data."""
    planner = StrategicWorkforcePlanner()
    planner.load_mock_data()
    
    # checks if we have 200 countries
    assert len(planner.data) == 200
    # checks if critical columns exist
    assert 'Workforce_Decline_Rate' in planner.data.columns
    assert 'AI_Readiness_Score' in planner.data.columns

def test_risk_classification():
    """Checks if the risk labels are valid (0 or 1)."""
    planner = StrategicWorkforcePlanner()
    planner.load_mock_data()
    planner.feature_engineering()
    
    # checks if Risk_Label contains only 0s and 1s
    assert planner.data['Risk_Label'].isin([0, 1]).all()