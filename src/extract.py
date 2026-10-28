import pandas as pd
import psycopg2

class Extract:

    VARIAVEIS_BCB = {
        11: "SELIC",
        433: "IPCA"
    }

    def __init__(self, series: str | None = None, agregado_bcb: int = 1, periodo_inicio_padrao: str | None = None, periodo_fim_padrao: str | None = None):
        self.series = series
        self.agregado_bcb = agregado_bcb
        self.periodo_inicio_padrao = periodo_inicio_padrao
        self.periodo_fim_padrao = periodo_fim_padrao
        self.base_selic_url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json'
        self.base_ipca_url = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json'
        self.client = psycopg2.connect(
            host="localhost",
            database="data_warehouse",
            user="airflow",
            password="airflow"
        )

    def close(self) -> None:
        """Encerra a conexão com o PostgreSQL, se necessário"""
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
        df = pd.read_json(url)
        return df.to_dict(orient="records")

    def bcb(
        self,
        variavel: int,
        estado: int,
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

    def close(self):
        """Método para fechar conexões caso necessário."""
        pass