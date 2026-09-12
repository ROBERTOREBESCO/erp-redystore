import sqlite3
from pathlib import Path
from typing import Any


db_path = Path(__file__).with_name("erp.db")


def conectar() -> sqlite3.Connection:
    return sqlite3.connect(db_path)


def criar_tabela_produtos() -> None:
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                cod_produto INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                peso REAL NOT NULL,
                quantidade_caixa INTEGER NOT NULL CHECK (quantidade_caixa > 0),
                valor_caixa REAL NOT NULL,
                valor_unitario REAL GENERATED ALWAYS AS
                    (valor_caixa / quantidade_caixa) STORED,
                desconto_compra REAL DEFAULT 0,
                valor_caixa_com_desconto REAL GENERATED ALWAYS AS
                    (valor_caixa - (valor_caixa * desconto_compra / 100)) STORED
            )
            """
        )


def adicionar_produto(
    descricao: str,
    peso: float,
    quantidade_caixa: int,
    valor_caixa: float,
    desconto_compra: float = 0.0,
) -> None:
    criar_tabela_produtos()

    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            INSERT INTO produtos (
                descricao,
                peso,
                quantidade_caixa,
                valor_caixa,
                desconto_compra
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (descricao, peso, quantidade_caixa, valor_caixa, desconto_compra),
        )


def listar_produtos() -> None:
    criar_tabela_produtos()

    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM produtos")
        produtos: list[tuple[Any, ...]] = cursor.fetchall()

    if not produtos:
        print("Nenhum produto encontrado.")
        return

    for produto in produtos:
        print(
            f"""
Codigo: {produto[0]}
Descricao: {produto[1]}
Peso: {produto[2]} kg
Quantidade por caixa: {produto[3]}
Valor da caixa: R$ {produto[4]:.2f}
Valor unitario: R$ {produto[5]:.2f}
Desconto na compra: {produto[6]}%
Valor da caixa com desconto: R$ {produto[7]:.2f}
"""
        )


def ler_float(mensagem: str) -> float:
    return float(input(mensagem).replace(",", "."))


def ler_int(mensagem: str) -> int:
    return int(input(mensagem))


def menu() -> None:
    criar_tabela_produtos()

    while True:
        print("\n=== MENU ERP ===")
        print("1 - Cadastrar produto")
        print("2 - Listar produtos")
        print("3 - Sair")

        try:
            opcao = input("Escolha uma opcao: ")
        except EOFError:
            print("Entrada encerrada.")
            return

        if opcao == "1":
            try:
                descricao = input("Descricao: ")
                peso = ler_float("Peso (kg): ")
                quantidade_caixa = ler_int("Quantidade por caixa: ")
                valor_caixa = ler_float("Valor da caixa: R$ ")
                desconto_compra = ler_float("Desconto na compra (%): ")
            except ValueError:
                print("Valor invalido. Tente novamente.")
                continue

            adicionar_produto(
                descricao,
                peso,
                quantidade_caixa,
                valor_caixa,
                desconto_compra,
            )
            print("Produto cadastrado com sucesso!")

        elif opcao == "2":
            listar_produtos()

        elif opcao == "3":
            print("Saindo do sistema...")
            break

        else:
            print("Opcao invalida, tente novamente.")


if __name__ == "__main__":
    menu()
