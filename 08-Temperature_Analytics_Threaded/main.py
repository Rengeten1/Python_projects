from threading import Thread, Lock
from retry_requests import retry
import matplotlib.pyplot as plt
import openmeteo_requests
import requests_cache
import pandas as pd
import requests
import json

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Global lists to store data safely   
data = []
locations = []

# using lock to prevent other threads from writitng to the data list at same time
lock = Lock()  

# Open mateo API URL
URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"

# All required Parameters for the Open Meteo API to work
PARAM = [
    # Deggendorf, Germany
    {
    "latitude": 48.8409,
    "longitude": 12.9607,
	"start_date": "2024-05-01",
	"end_date": "2025-05-01",
	"daily": "temperature_2m_mean",
	"timezone": "auto"   
    },
    # Bharatpur, Nepal
    {
	"latitude": 27.6768,
	"longitude": 84.4359,
	"start_date": "2024-05-01",
	"end_date": "2025-05-01",
	"daily": "temperature_2m_mean",
	"timezone": "auto"
    },
    # Lisbon, Portugal
    {
	"latitude": 38.7167,
	"longitude": -9.1333,
	"start_date": "2024-05-01",
	"end_date": "2025-05-01",
	"daily": "temperature_2m_mean",
	"timezone": "auto"
    }
]
def threaded_api_call(param):
    result = calling_api(param)
    if result:
        processed = process_daily_data(result)
        with lock:
            data.append(processed)

# Calls the open meteo API
def calling_api(param):
    try:
        # Call the Open-Meteo API
        responses = openmeteo.weather_api(URL, params=param)
        # Check if the response is valid
        if not responses:
            print("No response received.")
            return None
        response = responses[0]
        return response
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f" ConnectionError : {e}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout: {e}")
    except requests.exceptions.RequestException as e:
        print(f"RequestException : {e}")


# Function to process the daily data
def process_daily_data(data):
    # Process daily data. The order of variables needs to be the same as requested.
    daily = data.Daily()
    daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
    daily_dataframe = pd.DataFrame(data = daily_data)
    
    return daily_dataframe

# Function to find the monthly average temperature
def find_monthly_average(data):
    # Find the monthly average of the data
    # Convert the date column to datetime
    data["date"] = data["date"].dt.tz_localize(None)
    # Convert the date column to datetime
    data["month"] = data["date"].dt.to_period("M")
    # Extract the month from the date
    monthly_avg = data.groupby("month")["temperature_2m_mean"].mean().reset_index()
    # Convert the month to string for readability
    monthly_avg['month'] = monthly_avg['month'].astype(str)
    return monthly_avg

# Function to plot the monthly average temperature
def plotting_monthly_avg(monthly_avg, location):
    # Ploting using matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot(monthly_avg['month'], monthly_avg['temperature_2m_mean'], marker='o')
    plt.title('Average Monthly Temperature for ' + location)
    plt.xlabel('Month') 
    plt.ylabel('Average Temperature (°C)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'monthly_avg_temperature_{location}.png')
    plt.close()

# Function to save the combined data to a JSON file
def save_combined_data(data_dict):
    serializable_dict = {}

    for city, df in data_dict.items():
        # Convert date and month (if they exist) to string
        for col in df.columns:
            if col in ["date", "month"]:
                df[col] = df[col].astype(str)

        # Convert DataFrame to list of dictionaries
        records = df.to_dict(orient="records")

        serializable_dict[city] = records

    # Save the full structure to JSON
    out_path = "combined_weather_data.json"
    with open(out_path, "w") as f:
        json.dump(serializable_dict, f, indent=2)


# Main function of the program
def main():  
    city_names = ["Deggendorf, Germany", "Bhaktapur, Nepal", "Lisbon, Portugal"]
    print("Starting data retrieval...")
    print("--" * 20)
    # Create threads for each location
    threads = []
    for param in PARAM:
        t = Thread(target=threaded_api_call, args=(param,))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
    
    # threaded plotting data
    for i, location in enumerate(city_names):
        monthly_avg = find_monthly_average(data[i])
        plotting_monthly_avg(monthly_avg, location)
        print(f"Monthly average temperature for {location} plotted and saved.")
        
    print("--" * 20)
    
    # Save combined data to a common JSON file
    save_combined_data({"Degendorf, Germany": data[0], "Bharatpur, Nepal": data[1], "Lisbon, Portugal": data[2] })

    print("Combined weather data saved to 'combined_weather_data.json'")

    print("All Processes Completed.")

# Main Function Execution
if __name__ == "__main__":
    main()

    