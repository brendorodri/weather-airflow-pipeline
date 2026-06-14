import pytest
import requests
from src.extract_data import extract_weather_data

def test_extract_weather_data_success(mocker):
    # 1. Clean patches using pytest-mock
    mock_get = mocker.patch('src.extract_data.requests.get')
    mock_json_dump = mocker.patch('src.extract_data.json.dump')
    mock_open_file = mocker.patch('src.extract_data.open')
    mock_mkdir = mocker.patch('src.extract_data.Path.mkdir')

    # 2. Mocking the API response
    api_data = {
        "weather": [{"description": "clear sky"}],
        "name": "Sao Paulo",
        "main": {"temp": 25}
    }
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = api_data
    mock_response.raise_for_status = mocker.MagicMock()
    mock_get.return_value = mock_response

    test_url = 'https://api.fake-weather.com/data'
    
    # 3. Execution
    result = extract_weather_data(test_url)

    # 4. Assertions
    assert result == api_data
    mock_get.assert_called_once_with(test_url, timeout=30)
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_open_file.assert_called_once_with('data/weather_data.json', 'w')
    mock_json_dump.assert_called_once_with(
        api_data, 
        mock_open_file.return_value.__enter__.return_value, 
        indent=4
    )

def test_extract_weather_data_failure(mocker):
    mock_get = mocker.patch('src.extract_data.requests.get')
    # Use o erro específico que seu código tenta capturar
    mock_get.side_effect = requests.exceptions.RequestException("Connection Error")

    result = extract_weather_data('https://url-failure.com')
    
    assert result == []