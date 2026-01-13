import unittest
import pandas as pd
import geopandas as gpd
import numpy as np
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
import sys
import os

# Add the project root to sys.path so we can import src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- THESE IMPORTS MUST MATCH YOUR ACTUAL FILE NAMES ---
from src.config import ProjectConfig
from src.data_processor import DataProcessor
from src.vis_1_gdp_ratio import GdpRatioVisualizer
from src.vis_2_hollow import HollowVisualizer
from src.vis_3_map import RealMapVisualizer
from src.vis_4_regional_income import RegionalIncomeVisualizer
from src.vis_5_spectrum import SpectrumVisualizer
from src.vis_6_snapshot_regions import TableSnapshotVisualizer

class TestProjectConfig(unittest.TestCase):
    def test_paths_and_colors(self):
        """Test that configuration initializes paths and colors correctly."""
        with patch('pathlib.Path.mkdir'): # Prevent actual folder creation during test
            config = ProjectConfig()
            
            # Check critical paths are defined
            self.assertTrue(hasattr(config, 'OUT_NATIONAL'))
            self.assertTrue(hasattr(config, 'OUT_REGIONAL'))
            self.assertTrue(hasattr(config, 'OUT_LA'))
            
            # Check critical colors (Hex format)
            self.assertTrue(config.COLOR_GDP.startswith('#'))
            self.assertTrue(config.COLOR_HOUSING.startswith('#'))

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        """Create dummy dataframes simulating the ONS/WorldBank raw files."""
        # 1. Mock GDP Data (World Bank Format with 4 header rows skipped)
        self.df_gdp = pd.DataFrame({
            'Country Name': ['United Kingdom'], 'Country Code': ['GBR'],
            'Indicator Name': ['GDP'], 'Indicator Code': ['XYZ'],
            '2020': [100.0], '2021': [105.0]
        })

        # 2. Mock Income Data (ONS Format)
        self.df_income = pd.DataFrame({
            'ITL': ['ITL1', 'ITL1'], 'ITL code': ['UKC', 'UKD'],
            'Region name': ['North East', 'North West'],
            '2020': ['25,000'], '2021': ['26,000'] # String with commas
        })
        
        # 3. Mock Housing Data (ONS Format - Long/Wide mixed simulation)
        self.df_housing = pd.DataFrame({
            'Country/Region code': ['E1', 'E2'], 'Country/Region name': ['North East', 'North West'],
            'Local authority code': ['LA1', 'LA2'], 'Local authority name': ['City A', 'City B'],
            '2020': [5.0, 6.0], '2021': [5.5, 6.5]
        })

        # 4. Mock Gini Data
        self.df_gini = pd.DataFrame({
            'Country Name': ['United Kingdom'], 'Country Code': ['GBR'],
            'Indicator Name': ['Gini'], 'Indicator Code': ['GINI'],
            '2020': [34.0], '2021': [35.0]
        })
        
        # 5. Mock Income for "United Kingdom" row (for National merge)
        self.df_income_uk = pd.DataFrame({
            'ITL': ['NaN'], 'ITL code': ['UK'], 
            'Region name': ['United Kingdom'],
            '2020': ['30,000'], '2021': ['31,000']
        })
        
        # Combine Income Mock
        self.df_income_full = pd.concat([self.df_income_uk, self.df_income])

    @patch('src.data_processor.pd.read_csv')
    @patch('src.data_processor.pd.DataFrame.to_csv')
    @patch('os.listdir')
    @patch('pathlib.Path.exists')
    def test_run_processing_success(self, mock_exists, mock_listdir, mock_to_csv, mock_read_csv):
        """Test full data processing pipeline with happy path."""
        # Setup Mocks
        mock_exists.return_value = True # Files exist
        mock_listdir.return_value = ['gini_index.csv'] # Found the gini file
        
        # side_effect defines what read_csv returns each time it is called.
        # Order in code: GDP -> Income -> Housing -> Gini
        mock_read_csv.side_effect = [
            self.df_gdp,
            self.df_income_full,
            self.df_housing,
            self.df_gini
        ]

        processor = DataProcessor()
        processor.run()

        # Assertions
        # 1. Check if input files were read
        self.assertEqual(mock_read_csv.call_count, 4)
        
        # 2. Check if output files were saved (National, Regional, LA)
        self.assertEqual(mock_to_csv.call_count, 3)
        
        # 3. Verify National Data Logic (GDP should be scaled by 0.78)
        # We grab the first DataFrame sent to to_csv (OUT_NATIONAL)
        national_df = mock_to_csv.call_args_list[0][0][0] # Arg 0 is the dataframe
        self.assertIn('GDP_GBP', national_df.columns)
        self.assertIn('Gini', national_df.columns)
        # Check calculation (100 * 0.78 = 78.0)
        self.assertAlmostEqual(national_df.iloc[0]['GDP_GBP'], 78.0)

    @patch('src.data_processor.pd.read_csv')
    def test_run_processing_missing_files(self, mock_read_csv):
        """Test graceful failure if core files are missing."""
        mock_read_csv.side_effect = Exception("File not found")
        
        processor = DataProcessor()
        # Should catch exception and print error, not crash
        try:
            processor.run()
        except Exception as e:
            self.fail(f"Processor crashed on missing file: {e}")

class TestVisualizations(unittest.TestCase):
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show') # Block plots appearing
    @patch('pandas.read_csv')
    def test_vis_1_gdp_ratio(self, mock_read, mock_show, mock_save):
        """Test GdpRatioVisualizer generates plot and saves."""
        # Mock National Data
        mock_read.return_value = pd.DataFrame({
            'Year': [2000, 2001, 2002],
            'GDP_GBP': [25000, 26000, 27000],
            'Ratio': [5.0, 6.0, 7.0]
        })
        
        viz = GdpRatioVisualizer()
        viz.run()
        
        # Verify savefig called with correct filename pattern
        self.assertTrue(mock_save.called)
        args, _ = mock_save.call_args
        self.assertIn('04_gdp_ratio_scatter.png', str(args[0]))

    @patch('matplotlib.pyplot.savefig')
    @patch('pandas.read_csv')
    def test_vis_2_hollow(self, mock_read, mock_save):
        """Test HollowVisualizer (KDE) runs correctly."""
        # Mock LA Data (Needs Year and Ratio)
        mock_read.return_value = pd.DataFrame({
            'Year': [2002, 2002, 2022, 2022],
            'Ratio': [4.0, 4.5, 10.0, 11.0]
        })
        
        viz = HollowVisualizer()
        viz.run()
        
        self.assertTrue(mock_save.called)
        args, _ = mock_save.call_args
        self.assertIn('01_hollow_middle.png', str(args[0]))

    @patch('matplotlib.pyplot.savefig')
    @patch('geopandas.read_file') # Mock Internet Download
    @patch('pandas.read_csv')
    def test_vis_3_map(self, mock_read, mock_geo_read, mock_save):
        """Test RealMapVisualizer handles missing map data gracefully."""
        # Mock Regional Data
        mock_read.return_value = pd.DataFrame({
            'Region': ['North East'], 'Year': [2023], 'Income': [20000], 'Ratio': [5.0]
        })
        
        # Mock GeoJSON (Empty or Valid)
        mock_geo_read.return_value = gpd.GeoDataFrame({
            'NUTS112NM': ['North East'], 'geometry': [None]
        })
        
        viz = RealMapVisualizer()
        viz.run()
        
        self.assertTrue(mock_save.called)
        args, _ = mock_save.call_args
        self.assertIn('02_real_map.png', str(args[0]))

    @patch('matplotlib.pyplot.savefig')
    @patch('pandas.read_csv')
    def test_vis_4_regional_income(self, mock_read, mock_save):
        """Test RegionalIncomeVisualizer filters and plots."""
        # Mock Data with target regions
        mock_read.return_value = pd.DataFrame({
            'Region': ['London', 'North East', 'Other'],
            'Year': [2023, 2023, 2023],
            'Income': [40000, 20000, 10000]
        })
        
        viz = RegionalIncomeVisualizer()
        viz.run()
        
        self.assertTrue(mock_save.called)
        args, _ = mock_save.call_args
        self.assertIn('03_regional_income_trend.png', str(args[0]))

    @patch('matplotlib.pyplot.savefig')
    @patch('pandas.read_csv')
    def test_vis_5_spectrum(self, mock_read, mock_save):
        """Test SpectrumVisualizer sorts and plots."""
        mock_read.return_value = pd.DataFrame({
            'Region': ['London', 'North East'],
            'Year': [2023, 2023],
            'Income': [35000, 20000],
            'Ratio': [12.0, 5.0]
        })
        
        viz = SpectrumVisualizer()
        viz.run()
        
        self.assertTrue(mock_save.called)
        args, _ = mock_save.call_args
        self.assertIn('05_survival_spectrum.png', str(args[0]))

    @patch('matplotlib.pyplot.savefig')
    def test_vis_6_snapshot(self, mock_save):
        """Test Snapshot table generation (hardcoded data)."""
        viz = TableSnapshotVisualizer()
        viz.run()
        
        self.assertTrue(mock_save.called)
        args, _ = mock_save.call_args
        self.assertIn('06_regions_table_2023.png', str(args[0]))

if __name__ == '__main__':
    unittest.main()