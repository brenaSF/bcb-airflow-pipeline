from datetime import datetime, timedelta
from airflow.decorators import dag, task
from src.extract import Extract
from src.transform import Transform
from src.load import Load
import pandas as pd

@dag(
    dag_id="bcb_macro_pipeline",
    description='Pipeline ETL para Selic e IPCA via API do Banco Central',
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "brena",
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=['financeiro', 'bcb', 'etl'],
)
def bcb_etl():

    @task
    def extrair_api(variavel: int) -> list[dict]:
        """Extrai dados da API do Banco Central."""
        extract = Extract()
        try:
            return extract.bcb(variavel=variavel)
        finally:
            extract.close()

    
    @task
    def transformar_dados(dados_selic: list[dict], dados_ipca: list[dict]) -> str:
        """Transforma e faz o merge de Selic e IPCA em uma única base unificada por data."""
        transform = Transform()
        
        df_selic = transform.transform_indicador(dados_selic, nome_coluna="selic")
        
        transform_ipca = Transform()
        df_ipca = transform_ipca.transform_indicador(dados_ipca, nome_coluna="ipca")
        
        df_merged = pd.merge(df_selic, df_ipca, on='data', how='outer')
        
        df_merged = df_merged.sort_values('data').reset_index(drop=True)
        
        return df_merged.to_json(orient="records", date_format="iso")
    
    @task
    def carregar_postgres_raw(dados):
        """Carrega os dados consolidados no PostgreSQL."""
        load = Load()
        try:
            load.load(dados)
        finally:
            load.close()
        return dados


   # 1. Selic (Variável 11)
    raw_selic = extrair_api(variavel=11)
    #load_selic = carregar_postgres_raw(raw_selic)

    # 2. IPCA (Variável 433)
    raw_ipca = extrair_api(variavel=433)

    dados_consolidados = transformar_dados(raw_selic, raw_ipca)

    carregar_postgres_raw(dados_consolidados)


bcb_etl()