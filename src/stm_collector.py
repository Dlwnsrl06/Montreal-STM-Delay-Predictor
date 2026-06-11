import time 
import os
import random
from datetime import datetime 
import requests
from google.transit import gtfs_realtime_pb2

API_KEY = "l7f8098095215344e5828c55e56dba3d4a" 
URL = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
CSV_FILE = "montreal_travel_time.csv"

def fetch_transit_data(): # Phase 1: API Request
    params = {
        "apikey": API_KEY
    }
    headers = {
        "Accept": "application/x-protobuf"
    }

    try: #inside try block in case internet crashes -> so doesn't crash the whole program
        response = requests.get(URL, headers=headers, params=params) #grabs live binary data stream

        if response.status_code == 200: #if connection is successful
            # Phase 2: Decoding the Protocol Buffers

            feed = gtfs_realtime_pb2.FeedMessage() #creates empty container to house formatted data
            feed.ParseFromString(response.content) #converts binary data -> readable data

            #prepwork to collect snapshot of data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            records_saved = 0


            # Phase 3: Extracting Target Variables
            for entity in feed.entity: #loops through all objects in data
                if entity.HasField('trip_update'): #discards anything that is not vehicles with dynamic schedule records
                    trip = entity.trip_update.trip
                    route_id = trip.route_id

                    stops = entity.trip_update.stop_time_update

                    if len(stops) >= 2: #need two stops to measure travel time
                        stop_1 = stops[0]
                        stop_2 = stops[1]

                        #confirm arrival time exists in API
                        if stop_1.HasField('departure') and stop_2.HasField('arrival'):
                            time_1 = stop_1.departure.time
                            time_2 = stop_2.arrival.time

                            #calculate the travel time in seconds
                            travel_time_seconds = time_2 - time_1

                            #common sense check -> if its positive value
                            if travel_time_seconds > 0 and travel_time_seconds < 3600:
                                travel_minutes = round(travel_time_seconds / 60.0, 2)

                                if random.random() < 0.10: #collect for 10% of the values to save storage 
                                    #create clean data row
                                    record = f"{timestamp},{route_id},{travel_time_seconds},{travel_minutes}\n"

                                    save_record(record)
                                    records_saved += 1

                    
                        
            print(f"[{timestamp}] Successfully captured snapshot and appended {records_saved} travel segments.")

        elif response.status_code == 401:
            print("Error: Unauthorized. Check that your API key is pasted correctly inside quotes.")
        
        else:
            print(f"Failed to connect. HTTP Status Code: {response.status_code}")
        
    except Exception as e:
        print(f"An unexpected connection error occured: {e}")

def save_record(row_text): #Writing snapshot record to hard drive
    #check if file exists and if not, write the header row first
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a") as f:
        if not file_exists:
            f.write("timestamp,route_id,travel_seconds,travel_minutes\n")
        f.write(row_text)

# Phase 4: Polling Loop
print("Starting the Montreal STM Data Collector... Press Ctrl+C to stop.")
while True:
    fetch_transit_data()
    time.sleep(600) #snapshots data every 10 minutes 
