import datetime
<<<<<<< HEAD
import os
from pathlib import Path

from sqlalchemy import DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Caminho do banco de dados
db_path = str(Path(__file__).with_name("erp.db"))

# Cria a pasta se nao existir
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Configuracao do banco SQLite
engine = create_engine(f"sqlite:///{db_path}")


class Base(DeclarativeBase):
    pass

=======
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
>>>>>>> 5bd92de35619f4828b7923a4236ca385056a4deb

# Modelo da tabela Clientes
class Cliente(Base):
    """Modelo de Cliente para pessoa física e jurídica"""
    __tablename__ = "clientes"
<<<<<<< HEAD

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo_pessoa: Mapped[str | None] = mapped_column(String)  # Fisica ou Juridica
    nome_completo: Mapped[str | None] = mapped_column(String)
    cpf: Mapped[str | None] = mapped_column(String, unique=True)
    rg: Mapped[str | None] = mapped_column(String)
    sexo: Mapped[str | None] = mapped_column(String)
    cep: Mapped[str | None] = mapped_column(String)
    rua: Mapped[str | None] = mapped_column(String)
    bairro: Mapped[str | None] = mapped_column(String)
    cidade: Mapped[str | None] = mapped_column(String)
    estado: Mapped[str | None] = mapped_column(String)
    cnpj: Mapped[str | None] = mapped_column(String, unique=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String)
    razao_social: Mapped[str | None] = mapped_column(String)
    ramo_atividade: Mapped[str | None] = mapped_column(String)
    telefone: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    data_cadastro: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
    )


# Criacao do banco e da tabela
Base.metadata.create_all(engine)

if __name__ == "__main__":
    print(f"Banco de dados criado em: {db_path}")
=======
    
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
>>>>>>> 5bd92de35619f4828b7923a4236ca385056a4deb
