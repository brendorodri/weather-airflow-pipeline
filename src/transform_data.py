import json
import pandas as pd
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

path_name = Path(__file__).parent.parent / 'data' / 'weather_data.json'

columns_to_drop = ['weather', 'weather_icon', 'sys.type']

columns_to_rename = {
        "base": "base",
        "visibility": "visibility",
        "dt": "datetime",
        "timezone": "timezone",
        "id": "city_id", 
        "name": "city_name",
        "cod": "code",
        "coord.lon": "longitude",
        "coord.lat": "latitude",
        "main.temp": "temperature",
        "main.feels_like": "feels_like",
        "main.temp_min": "temp_min",
        "main.temp_max": "temp_max",
        "main.pressure": "pressure",
        "main.humidity": "humidity",
        "main.sea_level": "sea_level",
        "main.grnd_level": "grnd_level",
        "wind.speed": "wind_speed",
        "wind.deg": "wind_deg",
        "wind.gust": "wind_gust",
        "clouds.all": "clouds", 
        "sys.type": "sys_type",                 
        "sys.id": "sys_id",                
        "sys.country": "country",                
        "sys.sunrise": "sunrise",                
        "sys.sunset": "sunset",
        # weather_id, weather_main, weather_description 
    }

columns_to_convert_datetime = ['datetime', 'sunrise', 'sunset']


def create_dataframe(path_name:str) -> pd.DataFrame:
    """
    Creates a DataFrame from the JSON data.
    
    """
    
    logging.info("→ Creating DataFrame from JSON data")

    path = Path(path_name)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)

    logging.info(f"✓ DataFrame created with {len(df)} row(s)")
    return df

def normalize_dataframe_columns(df:pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes the column names of the weather DataFrame by converting them to lowercase and replacing spaces with underscores.

    Args:
        df (pd.DataFrame): The DataFrame whose columns need to be normalized.

    Returns:
        pd.DataFrame: A DataFrame with normalized column names.
    """
    df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))
    
    df_weather = df_weather.rename(columns={
        'id': 'weather_id',
        'main': 'weather_main',
        'description': 'weather_description',
        'icon': 'weather_icon'
    })
    
    df = pd.concat([df, df_weather], axis=1) # Concatenate the original DataFrame with the normalized weather DataFrame
    
    logging.info(f"\n✓ Column names normalized successfully - {len(df.columns)} columns in total")
    return df

def drop_columns(df:pd.DataFrame, columns_to_drop:list[str]) -> pd.DataFrame:
    """
    Drops the specified columns from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame from which to drop columns.
        columns_to_drop (list[str]): A list of column names to be dropped.

    Returns:
        pd.DataFrame: A DataFrame with the specified columns dropped.
    """
    logging.info(f"\n→ Dropping columns: {columns_to_drop}")
    
    df = df.drop(columns=columns_to_drop, errors='ignore')  # Drop specified columns, ignore if they don't exist
    
    logging.info(f"\n✓ Columns dropped successfully - {len(df.columns)} columns remaining")
    return df

def rename_columns(df:pd.DataFrame, column_mapping:dict[str, str]) -> pd.DataFrame:
    """
    Renames the columns of the DataFrame to more descriptive names.

    Args:
        df (pd.DataFrame): The DataFrame whose columns need to be renamed.
        column_mapping (dict[str, str]): A dictionary mapping old column names to new column names.

    Returns:
        pd.DataFrame: A DataFrame with renamed columns.
    """
    logging.info(f"\n→ Renaming columns: {list(column_mapping.keys())}")

    df = df.rename(columns=column_mapping)

    logging.info(f"\n✓ Columns renamed successfully - {len(df.columns)} columns in total")
    
    return df

def normalize_datetime_columns(df: pd.DataFrame, columns_names:list[str]) -> pd.DataFrame:
    logging.info(f"\n→ Converting columns to datetime: {columns_names}")
    
    for name in columns_names:
        df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert('America/Sao_Paulo')
    
    logging.info("✓ Columns converted to datetime\n")    
    return df



def data_transformations() -> pd.DataFrame:
    logging.info("→ Starting data transformation process")
    
    df = create_dataframe(path_name)
    df = normalize_dataframe_columns(df)
    df = drop_columns(df, columns_to_drop)
    df = rename_columns(df, columns_to_rename)
    df = normalize_datetime_columns(df, columns_to_convert_datetime)
    
    logging.info("→ Data transformation process completed")
    return df