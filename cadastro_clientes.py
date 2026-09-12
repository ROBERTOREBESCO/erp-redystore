"""
Módulo de cadastro e consulta de clientes no ERP.
"""

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from criar_banco_dados import Cliente

# Conexão com o banco
db_path = r"D:\REDYSTORE\APP REDYSTORE\erp.db"
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()

# ------------------ FUNÇÕES ------------------

def cadastrar_cliente():
    cpf = "12345678900"
    existente = session.query(Cliente).filter_by(cpf=cpf).first()
    if existente:
        print("Cliente já existe, não será cadastrado novamente.")
        return

    cliente = Cliente(
        tipo_pessoa="Fisica",
        nome_completo="Roberto Rebesco Vicente",
        cpf=cpf,
        rg="1234567",
        sexo="M",
        cep="91000000",
        rua="Rua Exemplo",
        bairro="Centro",
        cidade="Porto Alegre",
        estado="RS",
        telefone="51999999999",
        email="roberto@email.com",
        data_cadastro=datetime.datetime.now(datetime.UTC)
    )
    session.add(cliente)
    session.commit()
    print("Cliente cadastrado com sucesso!")


def consultar_por_cpf(cpf):
    cliente = session.query(Cliente).filter_by(cpf=cpf).first()
    if cliente:
      print(
    f"Cliente encontrado: {cliente.nome_completo} - "
    f"{cliente.cidade}/{cliente.estado}"
)
    else:
         print("Cliente não encontrado.")


def consultar_por_cidade(cidade):
    clientes = session.query(Cliente).filter_by(cidade=cidade).all()
    if clientes:
        print(f"Clientes em {cidade}:")
        for c in clientes:
            print(f"- {c.nome_completo} ({c.tipo_pessoa})")
    else:
        print("Nenhum cliente encontrado nessa cidade.")


# ------------------ TESTES ------------------
if __name__ == "__main__":
    cadastrar_cliente()
    consultar_por_cpf("12345678900")
    consultar_por_cidade("Porto Alegre")
