# STM Transit Travel Time Predictor 🚌

A machine learning pipeline that **predicts STM (Société de transport de Montréal) bus travel times based on Montreal weather conditions**. The system continuously collects real-time transit data, trains a model on an automated schedule, and logs results for analysis.

---

## Overview

This project was inspired by a previous transit delay predictor built on a pre-defined Kaggle dataset. The goal here was to take that a step further — instead of working with clean, ready-made data, this project required pulling real-time data directly from the STM API and Meteostat library, cleaning it, and analyzing it from scratch, making it significantly more complex and a much closer reflection of real-world data engineering.

This project also went through several pivots informed by the actual data:

- The STM API uses an exception-based protocol that filters out minor schedule deviations, producing sparse, zero-heavy delay data
- The API doesn't expose a raw "delay" field — it contains actual arrival times, making delay calculation memory-intensive
- The final model focuses on **predicting travel time based on Montreal weather conditions** (temperature, precipitation, wind, etc.)

---

## Project Structure

```
stm-transit-eta-predictor/
├── src/
│   └── stm_collector.py       # Real-time STM data collector
├── ml_model/
│   └── train_model.py         # Model training script
├── data_collection/           # Raw collected transit data
├── model_versions/            # Saved model snapshots
├── main.ipynb                 # Results visualization notebook
├── run_pipeline.py            # Automated pipeline manager
└── patch_notes.md             # Development log
```

---

## How It Works

### `run_pipeline.py` — Pipeline Orchestrator
The main entry point. Just run this once and leave it running as it automatically calls the collector every **10 minutes** and triggers model retraining after every **6 cycles (1 hour)**. Logs all activity and retries automatically on errors.

### `src/stm_collector.py` — Data Collector
Called by the pipeline on each cycle. Polls the STM real-time API and records live bus arrival data paired with current Montreal weather conditions (temperature, precipitation, wind, etc.) from the Meteostat API. Each snapshot is saved to `data_collection/`.

### `ml_model/train_model.py` — Model Trainer
Called by the pipeline after every 6 collection cycles. Trains a regression model on the accumulated data, using weather as features to predict bus travel time. Saves each trained model to `model_versions/`.

### `main.ipynb` — Visualization
Run this separately in Jupyter once data has been collected. Lets you explore the dataset and evaluate model performance with charts and metrics.

---

## Setup

### Prerequisites
- Python 3.8+
- A virtual environment (strongly recommended)

### Installation

```bash
git clone https://github.com/Dlwnsrl06/stm-transit-eta-predictor.git
cd stm-transit-eta-predictor

python -m venv myvenv
# Windows
myvenv\Scripts\activate
# macOS/Linux
source myvenv/bin/activate

pip install -r requirements.txt
```

### Running the Pipeline

Simply run `run_pipeline.py` once — it handles data collection and model training automatically in the background:

```bash
python run_pipeline.py
```

> **Note:** Run during active transit hours for best data quality. Late-night collections have fewer buses and less representative data.

### Visualizing Results

Once data has been collected, open `main.ipynb` in Jupyter to explore the data and evaluate model performance:

```bash
jupyter notebook main.ipynb
```

---

## Tech Stack

- **Python** — core language
- **Meteostat** — Montreal weather data
- **STM Real-Time API** — live bus arrival data
- **scikit-learn / pandas** — model training and data processing
- **Jupyter Notebook** — results visualization

---

## Notes

- Avoid running the pipeline late at night — fewer buses operate and the data is less representative
- The pipeline is designed to keep running continuously; use `Ctrl+C` to stop gracefully
