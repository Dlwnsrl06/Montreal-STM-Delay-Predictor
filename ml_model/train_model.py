import csv
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta  # Required for your time logic
import meteostat as ms
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def train_and_save_model():
    #Phase 1: loading the csv
    df = pd.read_csv("data/montreal_travel_time.csv")

    #convert the timestamp text into a smart Pandas datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    #Extract the 'hour' to match with weather data
    df['hour'] = df['timestamp'].dt.floor('h')


    #Phase 2: Collecting montreal weather data
    end_date = datetime.now() 
    start_date = end_date - timedelta(days=10)

    weather_df = ms.hourly(
        station='71627',
        start=start_date,
        end=end_date
    ).fetch().reset_index()
    weather_df = weather_df.fillna(0)


    #Phase 3: Merging datasets
    transit_df = pd.read_csv('data/montreal_travel_time.csv')

    transit_df['timestamp'] = pd.to_datetime(transit_df['timestamp'])
    weather_df['time'] = pd.to_datetime(weather_df['time'])

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
    

    #Phase 4: Training ML model
    final_dataset['Hour'] = final_dataset['timestamp'].dt.hour #extract raw date and time numbers from the timestamp
    final_dataset['DayOfWeek'] = final_dataset['timestamp'].dt.dayofweek # 0=Monday, 6=Sunday

    #define codomain and domain for the model
    y = final_dataset['travel_minutes']
    X = final_dataset.drop(columns=['timestamp', 'route_id', 'travel_seconds', 'travel_minutes'])

    #rewrite every column name as pure text
    X.columns = [str(c) for c in X.columns]

    #split the data into 80% train and 20% test data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #train the model with the train data
    model = LinearRegression()
    print("Training the model...")
    model.fit(X_train, y_train)
    print("Training complete! The AI has learned the traffic patterns.")

    #test the model against the test data
    predictions = model.predict(X_test)

    #analyze the results
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))


    #Phase 5: Recoding the mae and rmse
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #this creates a timestamp specific to the moment you run the notebook

    # Define the log file name
    log_file = 'data/performance_log.csv'

    rounded_mae = round(mae, 2)
    rounded_rmse = round(rmse, 2)


    # Prepare the data to write
    file_exists = os.path.isfile(log_file)
    data = [timestamp, len(final_dataset), rounded_mae, rounded_rmse]

    # Append to the log
    with open(log_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'num_rows', 'mae', 'rmse'])
        writer.writerow(data)

    print(f"Model trained. MAE: {rounded_mae}, RMSE: {rounded_rmse}. Logged to {log_file}")
    

    #Phase 6: Save the model itself
    os.makedirs('model_versions', exist_ok=True)
    joblib.dump(model, 'model_versions/transit_model.pkl')

if __name__ == "__main__":
    train_and_save_model()