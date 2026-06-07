import requests
import json
import os
from pathlib import Path

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.getenv('API_KEY')

def extract_weather_data(url:str) -> list[dict]:
    """
    Extracts data from the given URL and returns it as a list of dictionaries.

    Args:
        url (str): The URL to extract data from.

    Returns:
        list[dict]: A list of dictionaries containing the extracted data.
    """
    try:
        response = requests.get(url, timeout=30)  # Set a timeout for the request
        response.raise_for_status()  # Check if the request was successful
        data = response.json()  # Parse the JSON response
    
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred while fetching data: {e}")
        return []
    
    except json.JSONDecodeError as e:
        logging.error(f"An error occurred while parsing JSON: {e}")
        return []
    
    if not data:
        logging.warning("Unexpected data format: Expected a dictionary.")
        return []
    
    if not data:        
        logging.warning("No data found at the provided URL.")
        return []
    
    output_path = 'data/weather_data.json'
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)  # Save the data to a JSON file with indentation for readability
    
    logging.info(f"Data successfully extracted and saved to {output_path}")    
    
    return data

extract_weather_data(f'https://api.openweathermap.org/data/2.5/weather?q=Sao Paulo,BR&units=metric&appid={API_KEY}')