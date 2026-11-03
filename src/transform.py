import pandas as pd

class Transform:

    def __init__(self, df: pd.DataFrame | None = None):
        self.df = df

    def transform_indicador(self, data: list[dict], nome_coluna: str) -> pd.DataFrame:
        """Converte o resultado em um DataFrame e ajusta os tipos de dados."""
        if data is not None:
            self.df = pd.DataFrame(data)
            
        if self.df is None or self.df.empty:
            raise ValueError("Nenhum DataFrame ou dados informados para transformação.")

        if 'valor' in self.df.columns:
            self.df['valor'] = pd.to_numeric(self.df['valor'], errors='coerce')

        if 'data' in self.df.columns:
            self.df['data'] = pd.to_datetime(self.df['data'], format='%d/%m/%Y')
            self.df = self.df[self.df["data"] >= "2015-01-01"]

        if nome_coluna == "selic":
            self.df = self.df.set_index('data').resample('MS')['valor'].mean().reset_index()
            self.df = self.df.rename(columns={'valor': 'selic'})
            
        elif nome_coluna == "ipca":
            self.df['data'] = self.df['data'].dt.to_period('M').dt.to_timestamp()
            self.df = self.df.rename(columns={'valor': 'ipca'})

        if 'valor' in self.df.columns:
            self.df = self.df.drop(columns=['valor'])

        return self.df

    def transform_bnc(self, data: list[dict], nome_coluna: str) -> pd.DataFrame:
        """Alias para manter compatibilidade com a task do Airflow."""
        return self.transform_indicador(data, nome_coluna=nome_coluna)

    def save_to_csv(self, file_path: str) -> str:
        if self.df is not None:
            self.df.to_csv(file_path, index=False)
        return file_path