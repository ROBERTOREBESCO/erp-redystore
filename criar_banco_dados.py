import datetime
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


# Modelo da tabela Clientes
class Cliente(Base):
    __tablename__ = "clientes"

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
