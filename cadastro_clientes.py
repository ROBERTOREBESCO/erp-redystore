"""
Modulo de cadastro e consulta de clientes no ERP.
"""

import datetime
<<<<<<< HEAD
from pathlib import Path

=======
import os
>>>>>>> 5bd92de35619f4828b7923a4236ca385056a4deb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from criar_banco_dados import Cliente

<<<<<<< HEAD
# Conexao com o banco
db_path = str(Path(__file__).with_name("erp.db"))
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
session = Session()
=======

# Configuração do banco de dados
def obter_caminho_bd():
    """
    Obtém o caminho do banco de dados.
    Prioriza variável de ambiente, senão usa caminho relativo.
    """
    return os.getenv("ERP_DB_PATH", "erp.db")


def inicializar_sessao():
    """
    Inicializa e retorna uma sessão com o banco de dados.
    """
    try:
        db_path = obter_caminho_bd()
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise


# Variável global da sessão
session = None
>>>>>>> 5bd92de35619f4828b7923a4236ca385056a4deb


<<<<<<< HEAD
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
=======

def cadastrar_cliente(cpf=None, nome_completo=None, dados_adicionais=None):
    """
    Cadastra um novo cliente no banco de dados.
    
    Args:
        cpf (str): CPF do cliente
        nome_completo (str): Nome completo do cliente
        dados_adicionais (dict): Dicionário com dados opcionais
    """
    if not session:
        print("Erro: Sessão não inicializada.")
        return
    
    # Usa valores padrão se não fornecidos (para testes)
    if cpf is None:
        cpf = os.getenv("CLIENTE_CPF", "12345678900")
    if nome_completo is None:
        nome_completo = os.getenv("CLIENTE_NOME", "Roberto Rebesco Vicente")
    
    try:
        # Verifica se cliente já existe
        existente = session.query(Cliente).filter_by(cpf=cpf).first()
        if existente:
            print(f"Cliente com CPF {cpf} já existe, não será cadastrado novamente.")
            return

        # Dados padrão do cliente
        cliente_dados = {
            "tipo_pessoa": "Fisica",
            "nome_completo": nome_completo,
            "cpf": cpf,
            "rg": "1234567",
            "sexo": "M",
            "cep": "91000000",
            "rua": "Rua Exemplo",
            "bairro": "Centro",
            "cidade": "Porto Alegre",
            "estado": "RS",
            "telefone": "51999999999",
            "email": "roberto@email.com",
            "data_cadastro": datetime.datetime.now(datetime.UTC)
        }
        
        # Sobrescreve com dados adicionais se fornecidos
        if dados_adicionais:
            cliente_dados.update(dados_adicionais)
        
        cliente = Cliente(**cliente_dados)
        session.add(cliente)
        session.commit()
        print(f"✓ Cliente '{nome_completo}' cadastrado com sucesso!")
        
    except Exception as e:
        session.rollback()
        print(f"Erro ao cadastrar cliente: {e}")


def consultar_por_cpf(cpf):
    """
    Consulta um cliente pelo CPF.
    
    Args:
        cpf (str): CPF do cliente a buscar
    """
    if not session:
        print("Erro: Sessão não inicializada.")
        return
    
    try:
        cliente = session.query(Cliente).filter_by(cpf=cpf).first()
        if cliente:
            print(
                f"✓ Cliente encontrado: {cliente.nome_completo} - "
                f"{cliente.cidade}/{cliente.estado}"
            )
        else:
            print(f"✗ Cliente com CPF {cpf} não encontrado.")
    except Exception as e:
        print(f"Erro ao consultar cliente: {e}")


def consultar_por_cidade(cidade):
    """
    Consulta todos os clientes de uma cidade específica.
    
    Args:
        cidade (str): Nome da cidade para filtrar
    """
    if not session:
        print("Erro: Sessão não inicializada.")
        return
    
    try:
        clientes = session.query(Cliente).filter_by(cidade=cidade).all()
        if clientes:
            print(f"✓ Clientes em {cidade}:")
            for c in clientes:
                print(f"  - {c.nome_completo} ({c.tipo_pessoa})")
        else:
            print(f"✗ Nenhum cliente encontrado na cidade de {cidade}.")
    except Exception as e:
        print(f"Erro ao consultar clientes: {e}")
>>>>>>> 5bd92de35619f4828b7923a4236ca385056a4deb


# ------------------ TESTES ------------------
if __name__ == "__main__":
<<<<<<< HEAD
    menu_clientes()
=======
    try:
        # Inicializa a sessão global
        session = inicializar_sessao()
        
        print("=" * 50)
        print("TESTES DO MÓDULO DE CADASTRO DE CLIENTES")
        print("=" * 50)
        
        # Executa testes
        cadastrar_cliente()
        consultar_por_cpf("12345678900")
        consultar_por_cidade("Porto Alegre")
        
        print("=" * 50)
        print("Testes concluídos!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Erro durante execução: {e}")
    finally:
        # Garante fechamento da sessão
        if session:
            session.close()
            print("Sessão fechada com sucesso.")
>>>>>>> 5bd92de35619f4828b7923a4236ca385056a4deb
