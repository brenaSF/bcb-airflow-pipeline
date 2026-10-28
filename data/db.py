import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")

class Database:
    def __init__(self):
        self.engine = self.create_engine()

    def create_engine(self):
        return create_engine(DATABASE_URL)

    def get_engine(self):
        return self.engine