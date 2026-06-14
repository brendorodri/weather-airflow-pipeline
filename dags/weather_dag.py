from datetime import datetime, timedelta
from airflow.sdk import dag, task
from soda.scan import Scan
from pathlib import Path
import sys
import os

from yaml import scan

sys.path.insert(0, '/opt/airflow/')

from src.extract_data import extract_weather_data
from src.load_data import load_weather_data
from src.transform_data import data_transformations
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / 'config' / '.env'
load_dotenv(env_path)

API_KEY = os.getenv('API_KEY')
url = f'https://api.openweathermap.org/data/2.5/weather?q=Sao Paulo,BR&units=metric&appid={API_KEY}'

@dag(
    dag_id='weather_pipeline',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5)
    },
    description='ETL Pipeline for extracting, transforming, and loading weather data from OpenWeatherMap API',
    schedule='0 8 * * *',
    start_date=datetime(2026, 5, 30),
    catchup=False,
    tags=['weather', 'etl', 'openweathermap', 'airflow']
)
def weather_pipeline():
    
    @task
    def extract():
        extract_weather_data(url)
        
    @task
    def transform():
        df = data_transformations()
        df.to_parquet('/opt/airflow/data/temp_data.parquet', index=False)
        
    @task 
    def load():
        import pandas as pd
        df = pd.read_parquet('/opt/airflow/data/temp_data.parquet')
        load_weather_data('sp_weather', df)
        
    @task
    def data_quality_check():
        import logging
        
        logging.info("Initializing Soda Data Quality Check... 🚀")
        
        # Inicializa o scanner do Soda
        scan = Scan()
        scan.set_data_source_name("weather_db")
        
        # Aponta para os arquivos que criamos na pasta config
        # Use o caminho absoluto dentro do container do Airflow
        scan.add_configuration_yaml_file("/opt/airflow/config/configuration.yml")
        scan.add_sodacl_yaml_file("/opt/airflow/config/checks.yml")
        
        # Executa a varredura contra o banco de dados
        scan.execute()
        
        # Loga os resultados no Airflow para você visualizar
        logging.info(scan.get_logs_text())
        
        # Se houver falhas ou avisos, levanta um erro para que o Airflow marque a tarefa como falhada
        if scan.has_check_warns_or_fails():
            raise ValueError("Data Quality Check Failed! Please review the logs for details. ❌")
        
        logging.info("✅ Data Quality Check Passed! All checks are good. 🎉")
        
    extract() >> transform() >> load() >> data_quality_check()

weather_pipeline()