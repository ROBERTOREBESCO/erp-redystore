import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Caminho do banco de dados
db_path = r"D:\REDYSTORE\APP REDYSTORE\erp.db"

# Cria a pasta se não existir
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Configuração do banco SQLite
engine = create_engine(f"sqlite:///{db_path}")
Base = declarative_base()

# Modelo da tabela Clientes
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_pessoa = Column(String)  # Fisica ou Juridica
    nome_completo = Column(String)
    cpf = Column(String, unique=True)
    rg = Column(String)
    sexo = Column(String)
    cep = Column(String)
    rua = Column(String)
    bairro = Column(String)
    cidade = Column(String)
    estado = Column(String)
    cnpj = Column(String, unique=True)
    nome_fantasia = Column(String)
    razao_social = Column(String)
    ramo_atividade = Column(String)
    telefone = Column(String)
    email = Column(String)
    data_cadastro = Column(DateTime, default=datetime.datetime.utcnow)

# Criação do banco e da tabela
Base.metadata.create_all(engine)

print(f"Banco de dados criado em: {db_path}")
