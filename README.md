# Analysis of Structural Economic Shifts in UK Grocery Demand
**Module:** DAT5501 - Analysis, Software and Career Practice  

## 1. Project Purpose
This project investigates the **"Solvency Paradox"** facing mid-market UK supermarkets. While national GDP suggests economic growth, mid-market retailers are seeing a decline in volume sales. 

This analysis aims to prove that rising housing costs have "hollowed out" the disposable income of the middle class, creating a structural disconnect between nominal wealth and effective spending power. The output is a data-driven recommendation for a **regional tiered pricing strategy**.

---

## 2. Design Decisions
To ensure professional quality and reproducibility, several key architectural decisions were made:

### 2.1 Modular Architecture
* **Separation of Concerns:** The workflow is strictly separated into `DataProcessor` (ETL logic) and distinct `Visualizer` classes. This ensures that data cleaning logic is not entangled with plotting code, making debugging easier.
* **Config Object:** A central `ProjectConfig` class manages all file paths and styling constants (colors, fonts), ensuring consistency across all figures without hardcoding strings.

### 2.2 Robust Data Handling
* **Median Imputation:** Missing housing data for devolved nations (Scotland/NI) was handled using median imputation rather than mean imputation. This decision was taken because financial distributions are often skewed; mean imputation would be sensitive to outliers, whereas the median preserves the robust central tendency of the data.
* **Geospatial Integration:** Data processing normalizes inconsistent regional naming conventions (e.g., "Eastern" vs "East of England") to allow seamless merging between ONS tabular data and GeoJSON map files.

### 2.3 Testing Strategy (Offline-First)
* **Mocking over Dependency:** The unit tests use `unittest.mock` to simulate file I/O and internet requests. This was a deliberate design choice to ensure the test suite works in **CI/CD environments (CircleCI)** where large raw data files or external API keys might be missing.

---

## 3. Dataset Descriptions
The analysis utilizes three high-authority sources to ensure validity:

| Dataset | Source | Description | Usage in Project |
| :--- | :--- | :--- | :--- |
| **Regional GDHI** | ONS | Gross Disposable Household Income per capita (1997-2023). | Measures the *nominal* wealth of consumers by region. |
| **Housing Affordability** | ONS / Land Registry | Ratio of median house prices to median earnings. | Acts as the proxy for *fixed structural costs*. |
| **Real GDP per Capita** | World Bank | Inflation-adjusted GDP per capita for the UK. | Represents the "headline" economic growth used for hypothesis testing. |

> **Note:** Raw data files should be placed in the `data/raw/` directory.

---

## 4. Setup Instructions

### Prerequisites
* Python 3.8+
* pip (Python Package Manager)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)[YOUR_USERNAME]/[REPO_NAME].git
    cd [REPO_NAME]
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 5. How to Run Analysis

The analysis pipeline is designed to be run in two stages: **Processing** and **Visualization**.

### Step 1: Run the Data Pipeline
This script cleans raw ONS/WorldBank data, merges it, and handles missing values.
```bash
python src/data_processor.py
Output: Generates cleaned CSVs in data/processed/.
Step 2: Generate Visualisations
Run run_workflow.py to automatically generate all visualisations.

Bash

python run_workflow.py

Output: All images are saved to reports/figures/.

```
### 6. How Tests Work
This project maintains a professional Unit Test Suite located in tests/test_project.py.

Testing Philosophy
The tests do not require the actual raw CSV files. They utilize Mocks (unittest.mock.patch) to simulate:
pandas.read_csv: Returns dummy DataFrames to test logic flow.
matplotlib.pyplot.savefig: Verifies graphs are generated without actually writing files.
geopandas.read_file: Simulates map data downloads.
Running Tests
To verify the integrity of the code:
```
Bash
pytest tests/

```
Expected Output: 9 passed in 0.xx seconds
