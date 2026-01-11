from src.data_processor import DataProcessor
from src.vis_1_gdp_ratio import GdpRatioVisualizer
from src.vis_2_hollow import HollowVisualizer
from src.vis_3_map import RealMapVisualizer
from src.vis_5_spectrum import SpectrumVisualizer
from src.vis_4_regional_income import RegionalIncomeVisualizer
from src.vis_6_snapshot_regions import TableSnapshotVisualizer



if __name__ == "__main__":
    print("=== starting real money pipeline ===")
    DataProcessor().run() # run this just in case
    

    HollowVisualizer().run()
    RealMapVisualizer().run()
    SpectrumVisualizer().run()
    GdpRatioVisualizer().run()
    RegionalIncomeVisualizer().run()
    TableSnapshotVisualizer().run()
    
    print("=== pipeline complete ===")