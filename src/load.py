import pandas as pd
from data.db import Database
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()


class Load:

    def __init__(self):
        self.db_uri = os.getenv("DATABASE_URL")
        self.client = psycopg2.connect(self.db_uri)

    
    def close(self) -> None:
        """Encerra a conexão com o PostgreSQL, se necessário"""
        self.client.close()
        

    def load(self, dados: list[dict]):
        """Converte a lista de dicionários em DataFrame e carrega no PostgreSQL."""
        if not dados:
            return
            
        df = pd.DataFrame(dados)
        
        db = Database()
        engine = db.get_engine()
        
        df.to_sql('tb_macro_indicadores', con=engine, if_exists='replace', index=False)

