# run_project.py
from src.main import MainPipeline

if __name__ == "__main__":
  
    # it starts the engine inside the src folder
    app = MainPipeline()
    app.run()