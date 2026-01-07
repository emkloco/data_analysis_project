from src.data_processor import DataProcessor
from src.vis_1_decoupling import DecouplingVisualizer
from src.vis_2_matrix import MatrixVisualizer
from src.vis_3_map import MapVisualizer

if __name__ == "__main__":
    print("=== starting tesco strategy pipeline ===")
    
    # 1. clean the data
    DataProcessor().run()
    
    # 2. make the graphs
    DecouplingVisualizer().run()
    MatrixVisualizer().run()
    MapVisualizer().run()
    
    print("=== pipeline complete. check reports/figures folder ===")