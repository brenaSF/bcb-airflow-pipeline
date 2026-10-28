from datetime import datetime, timedelta
from airflow.decorators import dag, task
from src.extract import Extract
from src.transform import Transform
from src.load import Load

@dag(
    dag_id="bcb_macro_pipeline",
    description='Pipeline ETL de indicadores macroeconômicos do Banco Central',
    schedule="@monthly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args={
        "owner": "brena",
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["bcb", "etl", "macroeconomia"],
)
def bcb_etl():

    @task
    def extrair_api() -> list[dict]:
        """Extrai dados da API do Banco Central."""
        extract = Extract()
        try:
            return extract.bcb()
        finally:
            extract.close()

    @task
    def carregar_postgres_raw(dados: list[dict]) -> list[dict]:
        """Carrega os dados brutos no PostgreSQL e os repassa no fluxo."""
        load = Load()
        try:
            load.load(dados)
        finally:
            load.close()
        return dados

    @task
    def transformar(data: list[dict]) -> str:
        """Transforma os dados brutos em DataFrame e serializa em JSON para o XCom."""
        transform = Transform()
        df = transform.transform_bnc(data)
        return df.to_json(orient="records", date_format="iso")

    # Fluxo de tarefas
    raw_data = extrair_api()
    dados_carregados = carregar_postgres_raw(raw_data)
    transformar(dados_carregados)

bcb_etl()