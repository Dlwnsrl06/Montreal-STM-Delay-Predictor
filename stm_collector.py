import time 
import os
from datetime import datetime 
import requests
from google.transit import gtfs_realtime_pb2

API_KEY = "l7f8098095215344e5828c55e56dba3d4a" 
URL = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
CSV_FILE = "montreal_transit_history.csv"

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
            new_records = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Phase 3: Extracting Target Variables
            for entity in feed.entity: #loops through all objects in data
                if entity.HasField('trip_update'): #discards anything that is not vehicles with dynamic schedule records
                    trip = entity.trip_update.trip
                    route_id = trip.route_id

                    #Look at the stop time updates to find delays
                    for stop_update in entity.trip_update.stop_time_update: #loops for every bus stop
                        if stop_update.HasField('departure'): #checks if it has departure timing deviation record
                            delay_seconds = stop_update.departure.delay #extracts the delay

                            #Calculate our target variables
                            delay_minutes = round(delay_seconds / 60.0, 2)

                            if delay_seconds > 60: #has to be a different minute to be considered delayed
                                is_delayed = 1
                            else:
                                is_delayed = 0

                            #create a clean data row
                            record = f"{timestamp},{route_id},{delay_seconds},{delay_minutes},{is_delayed}\n" #formatted string literal - put variables in strings
                            new_records = [] #resets for the inner loop 
                            save_record(record) #Helper function 
                        
            print(f"[{timestamp}] Successfully captured snapshot and appended the data.")

        elif response.status_code == 401:
            print("Error: Unauthorized. Check that your API key is pasted correctly inside the quotes.")
        
        else:
            print(f"Failed to connect. HTTP Status Code: {response.status_code}")
        
    except Exception as e:
        print(f"An unexpected connection error occured: {e}")

def save_record(row_text): #Writing snapshot record to hard drive
    #check if file exists and if not, write the header row first
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a") as f:
        if not file_exists:
            f.write("timestamp,route_id,delay_seconds,delay_minutes,is_delayed\n")
        f.write(row_text)

# Phase 4: Polling Loop
print("Starting the Montreal STM Data Collector... Press Ctrl+C to stop.")
while True:
    fetch_transit_data()
    time.sleep(300) #snapshots data every 5 minutes 
