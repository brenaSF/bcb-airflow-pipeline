import pandas as pd
import psycopg2
import os 
from dotenv import load_dotenv
import requests


load_dotenv()


class Extract:

    VARIAVEIS_BCB = {
        11: "SELIC",
        433: "IPCA"
    }

    def __init__(self, series: str | None = None, agregado_bcb: int = 1, periodo_inicio_padrao: str | None = "01/01/2025", periodo_fim_padrao: str | None = "01/01/2026"):
        self.series = series
        self.agregado_bcb = agregado_bcb
        self.periodo_inicio_padrao = periodo_inicio_padrao
        self.periodo_fim_padrao = periodo_fim_padrao
        self.base_selic_url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json'
        self.base_ipca_url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json'
        self.client = psycopg2.connect(
            host=os.getenv("DB_HOST", default="postgres_db"),
            database=os.getenv("DB_NAME", default="data_warehouse"),
            user=os.getenv("DB_USER",default="airflow"),
            password=os.getenv("DB_PASSWORD",default="airflow"),
            port=os.getenv("DB_PORT", default=5432)
        )

    def close(self) -> None:
        """Encerra a conexão com o PostgreSQL, se necessário"""
        if self.client:
            self.client.close()

    def extract(self) -> list[dict]:
        """Extrai dados das séries padrão e retorna uma lista de dicionários."""
        data = {
            'selic': pd.read_json(self.base_selic_url),
            'ipca': pd.read_json(self.base_ipca_url)
        }
        
        dfs = []
        for indicator, df in data.items():
            df['indicador'] = indicator
            dfs.append(df)
            
        df_final = pd.concat(dfs, ignore_index=True)
        return df_final.to_dict(orient="records")

    def agregado(self, agregado_id, variavel, estado, periodo_inicio, periodo_fim):
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{variavel}/dados?formato=json"
        
        params = {}
        if periodo_inicio:
            params['dataInicial'] = periodo_inicio
        if periodo_fim:
            params['dataFinal'] = periodo_fim

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        dados_json = response.json()
        df = pd.DataFrame(dados_json)
        return df.to_dict(orient="records")
    
    def bcb(
        self,
        variavel: int,
        estado: str | int = "SP" ,
        periodo_inicio: str | None = None,
        periodo_fim: str | None = None,
    ) -> list[dict]:
        """Busca na API do Banco Central os dados de uma variável econômica."""
        if variavel not in self.VARIAVEIS_BCB:
            raise ValueError("Variável inválida. Use 11 para SELIC ou 433 para IPCA.")
             

        return self.agregado(
            agregado_id=self.agregado_bcb,
            variavel=variavel,
            estado=estado,
            periodo_inicio=periodo_inicio or self.periodo_inicio_padrao,
            periodo_fim=periodo_fim or self.periodo_fim_padrao,
        )
