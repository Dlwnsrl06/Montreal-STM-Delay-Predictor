import subprocess
import time
import logging
import sys

# Configure logging to keep track of pipeline health
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
COLLECTOR_SCRIPT = "src/stm_collector.py"
TRAINER_SCRIPT = "ml_model/train_model.py"
WAIT_TIME_SECONDS = 600  # 10 minutes between collection runs
TRAIN_EVERY_N_RUNS = 6   # Train after 6 collection cycles (1 hour)

def run_pipeline():
    run_count = 6
    
    logging.info("Pipeline Manager Started.")
    
    while True:
        try:
            # 1. Run the Data Collector
            logging.info(f"--- Starting Collector Run {run_count + 1} ---")
            subprocess.run([sys.executable, COLLECTOR_SCRIPT], check=True)
            run_count += 1
            
            # 2. Check if it's time to train the model
            if run_count >= TRAIN_EVERY_N_RUNS:
                logging.info("--- 6 runs completed. Triggering model training... ---")
                subprocess.run([sys.executable, TRAINER_SCRIPT], check=True)
                run_count = 0  # Reset the counter
                
            logging.info(f"Waiting {WAIT_TIME_SECONDS // 60} minutes for next cycle...")
            time.sleep(WAIT_TIME_SECONDS)
            
        except subprocess.CalledProcessError as e:
            logging.error(f"A script failed: {e}")
            time.sleep(60) # Wait a minute before retrying after an error
        except KeyboardInterrupt:
            logging.info("Pipeline stopped by user.")
            break

if __name__ == "__main__":
    run_pipeline()