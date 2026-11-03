import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os
import json
load_dotenv()


class Load:

    def __init__(self):
        self.db_uri = os.getenv(
            "DATABASE_URL",
            "postgresql://airflow:airflow@postgres_db:5432/data_warehouse",
        )
        self.engine = create_engine(self.db_uri)

    def close(self) -> None:
        """Encerra o engine, se necessário (o SQLAlchemy gerencia o pool automaticamente)"""
        if self.engine:
            self.engine.dispose()

    def load(self, dados, if_exists="append") -> None:
        """Converte os dados recebidos em DataFrame e carrega no PostgreSQL com segurança."""
        if not dados:
            return

        if isinstance(dados, str):
            dados = json.loads(dados)

        df = pd.DataFrame(dados)

        df.to_sql(
            "tb_macro_indicadores",
            con=self.engine,
            if_exists=if_exists,
            index=False,
        )

