![Python](https://img.shields.io/badge/Python-3.10-blue) ![Airflow](https://img.shields.io/badge/Airflow-2.7-red) ![Postgres](https://img.shields.io/badge/PostgreSQL-15-blue)

# Visão Geral 
Este projeto consiste em uma pipeline de dados ETL (Extract, Transform, Load) orquestrada pelo Apache Airflow. O objetivo principal é extrair automaticamente os dados históricos e diários da Taxa Selic e do IPCA a partir das APIs do Sistema Gerenciador de Séries Temporais (SGS) do Banco Central do Brasil, transformá-los e armazená-los em um Data Warehouse PostgreSQL. Por fim, os dados são disponibilizados visualmente por meio de um dashboard interativo construído em Streamlit.

## 🌐 Origem dos Dados
Os dados são consumidos publicamente via API REST do Banco Central do Brasil (SGS):

Taxa Selic Diária (Série 11):

[https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json](https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json)

IPCA Mensal (Série 433):

[https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json](https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json)

## Arquitetura 

Arquitetura
O fluxo usa um banco PostgreSQL:

API do Banco do Brasil -> Airflow (Extract/Transform) -> PostgreSQL (Data Warehouse)

| Etapa | Classe | Arquivo | Responsabilidade |
|-------|--------|---------|------------------|
| Extract | `Extract` | `src/extract.py` | . |
| Transform | `Transformer` | `src/transform.py` | . |
| Load | `Loader` | `src/load.py` | . |



## ⚙️ Funcionalidades e Estrutura das Ferramentas

### 🐘 PostgreSQL (Data Warehouse)
A armazena os indicadores consolidados na tabela tb_macro_indicadores:

data (DATE): Data de referência do indicador.

valor (NUMERIC/FLOAT): Valor percentual da taxa/índice.

indicador (VARCHAR): Nome do indicador (SELIC ou IPCA).

### 🌀 Apache Airflow (Orquestração)
DAG agendada para execução periódica contendo as seguintes tasks:

extract_task: Coleta os dados mais recentes das APIs de Selic e IPCA.

transform_task: Trata nulos, ajusta fuso horário/datas e valida os esquemas dos dados.

load_task: Insere/atualiza os registros na tabela do PostgreSQL.

### 🎈 Streamlit (Visualização)
Aplicação web interativa para visualização de gráficos de evolução temporal da Taxa Selic e do IPCA, comparações anuais e tabelas resumidas.

## Como executar 


```sh

docker compose run --rm airflow-webserver airflow db init

docker compose run --rm airflow-webserver airflow users create \
    --username admin \
    --firstname Brena \
    --lastname Freitas \
    --role Admin \
    --email admin@example.com \
    --password admin

    
docker compose up -d

```

# Acessar 

Airflow UI: http://localhost:8080 (Usuário: admin | Senha: admin)

Streamlit Dashboard: http://localhost:8501

PostgreSQL: Conexão disponível na porta 5432