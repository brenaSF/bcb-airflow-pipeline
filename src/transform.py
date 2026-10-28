import pandas as pd

class Transform:

    def __init__(self, df: pd.DataFrame | None = None):
        self.df = df

    def tratamento_tipos(self, data: list[dict] | None = None) -> pd.DataFrame:
        """Converte o resultado em um DataFrame e ajusta os tipos de dados."""
        if data is not None:
            self.df = pd.DataFrame(data)
            
        if self.df is None or self.df.empty:
            raise ValueError("Nenhum DataFrame ou dados informados para transformação.")

        if 'data' in self.df.columns:
            self.df['data'] = pd.to_datetime(self.df['data'], format='%d/%m/%Y')
        if 'valor' in self.df.columns:
            self.df['valor'] = self.df['valor'].astype(float)
            
        return self.df

    def transform_bnc(self, data: list[dict]) -> pd.DataFrame:
        """Alias para manter compatibilidade com a task do Airflow."""
        return self.tratamento_tipos(data)

    def save_to_csv(self, file_path: str) -> str:
        if self.df is not None:
            self.df.to_csv(file_path, index=False)
        return file_path