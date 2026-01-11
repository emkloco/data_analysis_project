import matplotlib.pyplot as plt
import pandas as pd
from src.config import ProjectConfig

class TableSnapshotVisualizer:
    def run(self):
        config = ProjectConfig()
        
        # 1. Setup the 2023 Data
        # I've sorted these by Income (descending) to match your screenshot's logic
        data = {
            'Region': [
                'London', 
                'South East', 
                'East of England',
                'South West', 
                'Scotland',
                'East Midlands', 
                'North West', 
                'West Midlands', 
                'Yorkshire and The Humber', 
                'Northern Ireland',
                'Wales', 
                'North East'
            ],
            'Income': [
                '£35,361', '£28,187', '£25,732', '£24,854', 
                '£22,908', '£21,656', '£21,543', '£21,141', 
                '£21,027', '£20,403', '£20,140', '£19,977'
            ],
            'Ratio': [
                12.5, 9.6, 9.2, 8.8, 
                5.6, 7.4, 6.6, 7.9, 
                6.4, 5.0, 6.1, 4.9
            ]
        }
        
        df = pd.DataFrame(data)

        # 2. Create the Table Plot
        # We use a figure size that fits a table (taller/narrower)
        plt.figure(figsize=(8, 6))
        
        # Remove the graph axes (we just want the table)
        ax = plt.gca()
        ax.axis('off')
        
        # Create the table
        # cellLoc='center' centers the text
        # loc='center' puts the table in the middle of the image
        table = plt.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1] # This stretches the table to fill the figure
        )

        # 3. Styling to match your screenshot
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        
        # Make the header row bold and slightly larger (optional, purely for looks)
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', size=13)
                cell.set_height(0.08) # Header height
            else:
                cell.set_height(0.06) # Row height

        plt.title('Appendix B: 2023 Regional Data Snapshot', fontsize=14, y=1.02)
        
        # 4. Save
        output_path = config.FIGURES_DIR / "06_regions_table_2023.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved table to {output_path}")

if __name__ == "__main__":
    TableSnapshotVisualizer().run()