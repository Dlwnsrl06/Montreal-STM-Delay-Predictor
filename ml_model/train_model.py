import csv
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta  # Required for your time logic
import meteostat as ms
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
import numpy as np

TRANSIT_CSV = 'data_collection/stm_travel_time.csv'
WEATHER_CACHE = 'data_collection/weather_cache.csv'
PERF_LOG = 'data_collection/ml_model_performance_log.csv'
MODEL_PATH = 'model_versions/transit_model.pkl'
STATION_ID = '71627'

def update_weather_cache():
    end_date = datetime.now()

    if os.path.isfile(WEATHER_CACHE):
        existing = pd.read_csv(WEATHER_CACHE, parse_dates=['time'])
        last_cached = existing['time'].max()
        start_date = last_cached - timedelta(hours=1)
        
    else:
        start_date = end_date - timedelta(days=30)
        existing = None
        print("No weather cache found. Fetching 30 days of history...")

    new_weather = ms.hourly(
        station=STATION_ID,
        start=start_date,
        end=end_date
    ).fetch().reset_index()

    if new_weather.empty:
        print("No new weather data - using existing cache.")
        existing['time'] = pd.to_datetime(existing['time']).dt.tz_localize(None)
        return existing

    # Save time column, convert everything else, put time back
    time_col = new_weather['time']
    new_weather = new_weather.drop(columns=['time'])
    new_weather = new_weather.apply(lambda col: pd.to_numeric(col, errors='coerce'))
    new_weather = new_weather.ffill().bfill().fillna(0)
    new_weather['time'] = time_col

    if existing is not None:
        combined = pd.concat([existing, new_weather]).drop_duplicates(subset='time')
    else:
        combined = new_weather

    combined = combined.sort_values('time').reset_index(drop=True)
    combined.to_csv(WEATHER_CACHE, index=False)
    print(f"Weather cache updated: {len(combined)} hourly records total.")
    
    # Return with clean types
    combined['time'] = pd.to_datetime(combined['time']).dt.tz_localize(None)
    return combined

def build_features(df): #centralized feature engineering so training and inference always use identical columns
    df = df.copy()
    df['Hour'] = df['timestamp'].dt.hour
    df['DayOfWeek'] = df['timestamp'].dt.dayofweek
    df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
    df['IsRushHour'] = df['Hour'].isin([7, 8, 9, 16, 17, 18]).astype(int)  
    df['Month'] = df['timestamp'].dt.month  #captures seasonality
    return df


def train_and_save_model():
    #Phase 1: loading the csv
    transit_df = pd.read_csv("data_collection/stm_travel_time.csv")

    #convert the timestamp text into a smart Pandas datetime object
    transit_df['timestamp'] = pd.to_datetime(transit_df['timestamp']).dt.tz_localize(None)


    #Phase 2: Collecting montreal weather data
    weather_df = update_weather_cache()
    weather_df['time'] = pd.to_datetime(weather_df['time']).dt.tz_localize(None)

    #Phase 3: Merging datasets
    transit_df['merge_hour'] = transit_df['timestamp'].dt.floor('h')

    #merging
    final_dataset = pd.merge(
        left=transit_df,
        right=weather_df,
        left_on='merge_hour',
        right_on='time',
        how='left'
    )
    final_dataset = final_dataset.drop(columns=['merge_hour','time'])
    
    weather_cols = [c for c in weather_df.columns if c != 'time']
    before = len(final_dataset)
    final_dataset = final_dataset.dropna(subset=weather_cols)
    dropped = before - len(final_dataset)
    if dropped:
        print(f"Dropped {dropped} rows with no matching weather data.")


    #Phase 4: Training ML model
    final_dataset = build_features(final_dataset)

    #define codomain and domain for the model
    y = final_dataset['travel_minutes']
    X = final_dataset.drop(columns=['timestamp', 'route_id', 'travel_seconds', 'travel_minutes'])

    #rewrite every column name as pure text
    X.columns = [str(c) for c in X.columns]

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    #train the model with the train data
    model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        random_state=42
    )

    model.fit(X_train, y_train)
    print("Training complete!")

    #test the model against the test data
    predictions = model.predict(X_test)

    #analyze the results
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    importance = pd.Series(model.feature_importances_, index=X.columns)
    print(f"Top 5 features: {importance.nlargest(5).to_dict()}")


    #Phase 5: Recoding the mae and rmse
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #this creates a timestamp specific to the moment you run the notebook

    rounded_mae = round(mae, 2)
    rounded_rmse = round(rmse, 2)


    # Prepare the data to write
    log_exists = os.path.isfile(PERF_LOG)

    # Append to the log
    with open(PERF_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        if not log_exists:
            writer.writerow(['timestamp', 'num_rows', 'mae', 'rmse'])
        writer.writerow([timestamp, len(final_dataset), rounded_mae, rounded_rmse])

    print(f"Model trained. MAE: {rounded_mae}, RMSE: {rounded_rmse}. Logged to {PERF_LOG}")
    

    #Phase 6: Save the model itself
    os.makedirs('model_versions', exist_ok=True)
    joblib.dump(model, 'model_versions/transit_model.pkl')

if __name__ == "__main__":
    train_and_save_model()