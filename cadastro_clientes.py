"""
Modulo de cadastro e consulta de clientes no ERP.
"""

import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from criar_banco_dados import Cliente

# Conexao com o banco
db_path = str(Path(__file__).with_name("erp.db"))
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()


# ------------------ FUNCOES ------------------
def cadastrar_cliente() -> None:
    cpf = "12345678900"
    existente = session.query(Cliente).filter_by(cpf=cpf).first()
    if existente:
        print("Cliente ja existe, nao sera cadastrado novamente.")
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
        data_cadastro=datetime.datetime.now(datetime.UTC),
    )
    session.add(cliente)
    session.commit()
    print("Cliente cadastrado com sucesso!")


def cadastrar_cliente_interativo() -> None:
    cpf = input("CPF: ")
    existente = session.query(Cliente).filter_by(cpf=cpf).first()
    if existente:
        print("Cliente ja existe, nao sera cadastrado novamente.")
        return

    cliente = Cliente(
        tipo_pessoa=input("Tipo pessoa (Fisica/Juridica): ") or "Fisica",
        nome_completo=input("Nome completo: "),
        cpf=cpf,
        rg=input("RG: "),
        sexo=input("Sexo: "),
        cep=input("CEP: "),
        rua=input("Rua: "),
        bairro=input("Bairro: "),
        cidade=input("Cidade: "),
        estado=input("Estado: "),
        telefone=input("Telefone: "),
        email=input("Email: "),
        data_cadastro=datetime.datetime.now(datetime.UTC),
    )
    session.add(cliente)
    session.commit()
    print("Cliente cadastrado com sucesso!")


def consultar_por_cpf(cpf: str) -> None:
    cliente = session.query(Cliente).filter_by(cpf=cpf).first()
    if cliente:
        print(
            f"Cliente encontrado: {cliente.nome_completo} - "
            f"{cliente.cidade}/{cliente.estado}"
        )
    else:
        print("Cliente nao encontrado.")


def consultar_por_cidade(cidade: str) -> None:
    clientes = session.query(Cliente).filter_by(cidade=cidade).all()
    if not clientes:
        print("Nenhum cliente encontrado nessa cidade.")
        return

    print(f"Clientes em {cidade}:")
    for cliente in clientes:
        print(f"- {cliente.nome_completo} ({cliente.tipo_pessoa})")


def listar_clientes() -> None:
    clientes = session.query(Cliente).order_by(Cliente.nome_completo).all()
    if not clientes:
        print("Nenhum cliente encontrado.")
        return

    for cliente in clientes:
        print(
            f"{cliente.id} - {cliente.nome_completo} | "
            f"CPF: {cliente.cpf} | Cidade: {cliente.cidade}/{cliente.estado}"
        )


def menu_clientes() -> None:
    while True:
        print("\n=== CLIENTES ===")
        print("1 - Cadastrar cliente")
        print("2 - Consultar por CPF")
        print("3 - Consultar por cidade")
        print("4 - Listar clientes")
        print("5 - Voltar")

        try:
            opcao = input("Escolha uma opcao: ")
        except EOFError:
            print("Entrada encerrada.")
            return

        if opcao == "1":
            cadastrar_cliente_interativo()
        elif opcao == "2":
            consultar_por_cpf(input("CPF: "))
        elif opcao == "3":
            consultar_por_cidade(input("Cidade: "))
        elif opcao == "4":
            listar_clientes()
        elif opcao == "5":
            break
        else:
            print("Opcao invalida, tente novamente.")


# ------------------ TESTES ------------------
if __name__ == "__main__":
    menu_clientes()
