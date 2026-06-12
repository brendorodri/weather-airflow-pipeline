import pytest
import pandas as pd
from transform_data import normalize_dataframe_columns, drop_columns, rename_columns

@pytest.fixture
def raw_df():
    """Fixture with the nested data structure coming from the JSON."""
    return pd.DataFrame({
        'weather': [[{'id': 800, 'main': 'Clear', 'description': 'clear sky', 'icon': '01d'}]],
        'sys.type': [1],
        'name': ['Sao Paulo'],
        'main.temp': [25.0]
    })

def test_normalize_dataframe_columns(raw_df):
    # Validates if the list of dictionaries inside the 'weather' column was expanded
    result_df = normalize_dataframe_columns(raw_df)
    
    assert 'weather_id' in result_df.columns
    assert 'weather_main' in result_df.columns
    assert result_df['weather_main'].iloc[0] == 'Clear'

def test_drop_columns(raw_df):
    columns_to_drop = ['weather', 'sys.type']
    result_df = drop_columns(raw_df, columns_to_drop)
    
    assert 'weather' not in result_df.columns
    assert 'sys.type' not in result_df.columns
    assert 'name' in result_df.columns # Does not affect the rest

def test_rename_columns():
    # Using a simple DataFrame created on the fly
    simple_df = pd.DataFrame({'name': ['SP'], 'main.temp': [25]})
    mapping = {'name': 'city_name', 'main.temp': 'temperature'}
    
    result_df = rename_columns(simple_df, mapping)
    
    assert 'city_name' in result_df.columns
    assert 'temperature' in result_df.columns
    assert 'name' not in result_df.columns