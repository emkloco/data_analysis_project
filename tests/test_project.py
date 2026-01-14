import unittest
import pandas as pd
import geopandas as gpd
import numpy as np
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
import sys
import os

# add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        with patch('pathlib.Path.mkdir'):
            config = ProjectConfig()
            self.assertTrue(hasattr(config, 'OUT_NATIONAL'))
            self.assertTrue(hasattr(config, 'OUT_REGIONAL'))
            self.assertTrue(config.COLOR_GDP.startswith('#'))

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        # 1. mock GDP
        self.df_gdp = pd.DataFrame({
            'Country Name': ['United Kingdom'], 'Country Code': ['GBR'],
            'Indicator Name': ['GDP'], 'Indicator Code': ['XYZ'],
            '2020': [100.0], '2021': [105.0]
        })
        # 2. mock income
        self.df_income = pd.DataFrame({
            'ITL': ['ITL1', 'ITL1'], 'ITL code': ['UKC', 'UKD'],
            'Region name': ['North East', 'North West'],
            '2020': ['25,000', '25,500'], '2021': ['26,000', '26,500'] 
        })
        # 3. mock housing
        self.df_housing = pd.DataFrame({
            'Country/Region code': ['E1', 'E2'], 'Country/Region name': ['North East', 'North West'],
            'Local authority code': ['LA1', 'LA2'], 'Local authority name': ['City A', 'City B'],
            '2020': [5.0, 6.0], '2021': [5.5, 6.5]
        })
        # 4. mock national income row
        self.df_income_uk = pd.DataFrame({
            'ITL': ['NaN'], 'ITL code': ['UK'], 
            'Region name': ['United Kingdom'],
            '2020': ['30,000'], '2021': ['31,000']
        })
        self.df_income_full = pd.concat([self.df_income_uk, self.df_income])

    @patch('src.data_processor.pd.read_csv')
    @patch('src.data_processor.pd.DataFrame.to_csv', autospec=True) 
    @patch('os.listdir')
    @patch('pathlib.Path.exists')
    def test_run_processing_success(self, mock_exists, mock_listdir, mock_to_csv, mock_read_csv):
        mock_exists.return_value = True 
        
    
        mock_read_csv.side_effect = [
            self.df_gdp,
            self.df_income_full,
            self.df_housing,
        ]

        processor = DataProcessor()
        processor.run()

        # check if input files were read 
        self.assertEqual(mock_read_csv.call_count, 3)
        
        # check outputs
        self.assertEqual(mock_to_csv.call_count, 3)
        
        # verify National Data Logic
        national_df = mock_to_csv.call_args_list[0][0][0]
        self.assertIn('GDP_GBP', national_df.columns)
        self.assertAlmostEqual(national_df.iloc[0]['GDP_GBP'], 78.0)

    @patch('src.data_processor.pd.read_csv')
    def test_run_processing_missing_files(self, mock_read_csv):
        mock_read_csv.side_effect = Exception("File not found")
        processor = DataProcessor()
        try:
            processor.run()
        except Exception as e:
            self.fail(f"Processor crashed on missing file: {e}")

class TestVisualizations(unittest.TestCase):
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show') 
    @patch('pandas.read_csv')
    def test_vis_1_gdp_ratio(self, mock_read, mock_show, mock_save):
        mock_read.return_value = pd.DataFrame({
            'Year': [2000, 2001, 2002], 'GDP_GBP': [25000, 26000, 27000], 'Ratio': [5.0, 6.0, 7.0]
        })
        viz = GdpRatioVisualizer()
        viz.run()
        self.assertTrue(mock_save.called)

    @patch('matplotlib.pyplot.savefig')
    @patch('pandas.read_csv')
    def test_vis_2_hollow(self, mock_read, mock_save):
        mock_read.return_value = pd.DataFrame({
            'Year': [2002, 2002, 2022, 2022], 'Ratio': [4.0, 4.5, 10.0, 11.0]
        })
        viz = HollowVisualizer()
        viz.run()
        self.assertTrue(mock_save.called)

    @patch('geopandas.GeoDataFrame.plot')
    @patch('matplotlib.pyplot.savefig')
    @patch('geopandas.read_file') 
    @patch('pandas.read_csv')
    def test_vis_3_map(self, mock_read, mock_geo_read, mock_save, mock_plot):
        mock_read.return_value = pd.DataFrame({
            'Region': ['North East'], 'Year': [2023], 'Income': [20000], 'Ratio': [5.0]
        })
        mock_geo_read.return_value = gpd.GeoDataFrame({
            'NUTS112NM': ['North East'], 'geometry': [None]
        })
        viz = RealMapVisualizer()
        viz.run()
        self.assertTrue(mock_save.called)

    @patch('matplotlib.pyplot.savefig')
    @patch('pandas.read_csv')
    def test_vis_4_regional_income(self, mock_read, mock_save):
        mock_read.return_value = pd.DataFrame({
            'Region': ['London', 'North East', 'Other'], 'Year': [2023, 2023, 2023], 'Income': [40000, 20000, 10000]
        })
        viz = RegionalIncomeVisualizer()
        viz.run()
        self.assertTrue(mock_save.called)

    @patch('matplotlib.pyplot.savefig')
    @patch('pandas.read_csv')
    def test_vis_5_spectrum(self, mock_read, mock_save):
        mock_read.return_value = pd.DataFrame({
            'Region': ['London', 'North East'], 'Year': [2023, 2023], 'Income': [35000, 20000], 'Ratio': [12.0, 5.0]
        })
        viz = SpectrumVisualizer()
        viz.run()
        self.assertTrue(mock_save.called)

    @patch('matplotlib.pyplot.savefig')
    def test_vis_6_snapshot(self, mock_save):
        viz = TableSnapshotVisualizer()
        viz.run()
        self.assertTrue(mock_save.called)

if __name__ == '__main__':
    unittest.main()