import os
import datetime
import logging
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração do caminho do banco
db_dir = os.getenv("DB_PATH", r"D:\REDYSTORE\APP REDYSTORE")
db_path = os.path.join(db_dir, "erp.db")

# Cria a pasta se não existir
try:
    os.makedirs(db_dir, exist_ok=True)
    logger.info(f"Diretório do banco de dados verificado: {db_dir}")
except OSError as e:
    logger.error(f"Erro ao criar diretório: {e}")
    raise

# Configuração do banco SQLite
try:
    engine = create_engine(f"sqlite:///{db_path}")
    logger.info(f"Engine SQLAlchemy criado para: {db_path}")
except Exception as e:
    logger.error(f"Erro ao criar engine SQLAlchemy: {e}")
    raise

Base = declarative_base()

# Modelo da tabela Clientes
class Cliente(Base):
    """Modelo de Cliente para pessoa física e jurídica"""
    __tablename__ = "clientes"
    
    # Identificador
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Tipo de cliente
    tipo_pessoa = Column(String(20), nullable=False)  # 'Fisica' ou 'Juridica'
    
    # Dados pessoa física
    nome_completo = Column(String(255))
    cpf = Column(String(11), unique=True)
    rg = Column(String(20))
    sexo = Column(String(1))
    
    # Dados pessoa jurídica
    cnpj = Column(String(14), unique=True)
    nome_fantasia = Column(String(255))
    razao_social = Column(String(255))
    ramo_atividade = Column(String(100))
    
    # Endereço (comum a ambos)
    cep = Column(String(8))
    rua = Column(String(255))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))
    
    # Contato
    telefone = Column(String(20))
    email = Column(String(255))
    
    # Auditoria
    data_cadastro = Column(DateTime, default=datetime.datetime.now)
    
    def __repr__(self):
        return f"<Cliente(id={self.id}, tipo={self.tipo_pessoa}, nome={self.nome_completo or self.razao_social})>"

# Criação do banco e da tabela
def criar_banco_dados():
    """Cria o banco de dados e as tabelas necessárias"""
    try:
        Base.metadata.create_all(engine)
        logger.info(f"✅ Banco de dados criado com sucesso em: {db_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao criar banco de dados: {e}")
        return False

if __name__ == "__main__":
    criar_banco_dados()
