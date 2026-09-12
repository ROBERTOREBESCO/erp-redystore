import sqlite3
from pathlib import Path
from typing import Any


db_path = Path(__file__).with_name("erp.db")


def conectar() -> sqlite3.Connection:
    conexao = sqlite3.connect(db_path)
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_tabela_pedidos() -> None:
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS pedidos (
                cod_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                cod_produto INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                peso REAL NOT NULL,
                quantidade_caixa INTEGER NOT NULL CHECK (quantidade_caixa > 0),
                valor_caixa REAL NOT NULL,
                valor_unitario REAL GENERATED ALWAYS AS
                    (valor_caixa / quantidade_caixa) STORED,
                desconto_compra REAL DEFAULT 0,
                valor_caixa_com_desconto REAL GENERATED ALWAYS AS
                    (valor_caixa - (valor_caixa * desconto_compra / 100)) STORED,
                quantidade_caixas_pedido INTEGER NOT NULL
                    CHECK (quantidade_caixas_pedido > 0),
                valor_total_pedido REAL GENERATED ALWAYS AS
                    (valor_caixa_com_desconto * quantidade_caixas_pedido) STORED,
                FOREIGN KEY (cod_produto) REFERENCES produtos(cod_produto)
            )
            """
        )


def adicionar_pedido(
    cod_produto: int,
    descricao: str,
    peso: float,
    quantidade_caixa: int,
    valor_caixa: float,
    desconto_compra: float,
    quantidade_caixas_pedido: int,
) -> None:
    criar_tabela_pedidos()

    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            INSERT INTO pedidos (
                cod_produto,
                descricao,
                peso,
                quantidade_caixa,
                valor_caixa,
                desconto_compra,
                quantidade_caixas_pedido
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cod_produto,
                descricao,
                peso,
                quantidade_caixa,
                valor_caixa,
                desconto_compra,
                quantidade_caixas_pedido,
            ),
        )


def buscar_produto(cod_produto: int) -> tuple[Any, ...] | None:
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            SELECT
                cod_produto,
                descricao,
                peso,
                quantidade_caixa,
                valor_caixa,
                desconto_compra
            FROM produtos
            WHERE cod_produto = ?
            """,
            (cod_produto,),
        )
        return cursor.fetchone()


def listar_produtos_para_pedido() -> None:
    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute(
            """
            SELECT
                cod_produto,
                descricao,
                peso,
                quantidade_caixa,
                valor_caixa,
                valor_caixa_com_desconto
            FROM produtos
            ORDER BY descricao
            """
        )
        produtos: list[tuple[Any, ...]] = cursor.fetchall()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return

    for produto in produtos:
        print(
            f"{produto[0]} - {produto[1]} | "
            f"{produto[2]} kg | caixa: {produto[3]} | "
            f"R$ {produto[4]:.2f} | com desconto: R$ {produto[5]:.2f}"
        )


def cadastrar_pedido_interativo() -> None:
    criar_tabela_pedidos()
    listar_produtos_para_pedido()

    try:
        cod_produto = int(input("Codigo do produto: "))
        quantidade_caixas_pedido = int(input("Quantidade de caixas no pedido: "))
    except ValueError:
        print("Valor invalido. Tente novamente.")
        return

    produto = buscar_produto(cod_produto)
    if produto is None:
        print("Produto nao encontrado.")
        return

    adicionar_pedido(
        cod_produto=produto[0],
        descricao=produto[1],
        peso=produto[2],
        quantidade_caixa=produto[3],
        valor_caixa=produto[4],
        desconto_compra=produto[5],
        quantidade_caixas_pedido=quantidade_caixas_pedido,
    )
    print("Pedido cadastrado com sucesso!")


def listar_pedidos() -> None:
    criar_tabela_pedidos()

    with conectar() as conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM pedidos")
        pedidos: list[tuple[Any, ...]] = cursor.fetchall()

    if not pedidos:
        print("Nenhum pedido encontrado.")
        return

    for pedido in pedidos:
        print(
            f"""
Pedido No: {pedido[0]}
Codigo Produto: {pedido[1]}
Descricao: {pedido[2]}
Peso: {pedido[3]} kg
Quantidade por caixa: {pedido[4]}
Valor da caixa: R$ {pedido[5]:.2f}
Valor unitario: R$ {pedido[6]:.2f}
Desconto na compra: {pedido[7]}%
Valor da caixa com desconto: R$ {pedido[8]:.2f}
Quantidade de caixas no pedido: {pedido[9]}
Valor total do pedido: R$ {pedido[10]:.2f}
"""
        )


def menu_pedidos() -> None:
    while True:
        print("\n=== PEDIDOS ===")
        print("1 - Cadastrar pedido")
        print("2 - Listar pedidos")
        print("3 - Voltar")

        try:
            opcao = input("Escolha uma opcao: ")
        except EOFError:
            print("Entrada encerrada.")
            return

        if opcao == "1":
            cadastrar_pedido_interativo()
        elif opcao == "2":
            listar_pedidos()
        elif opcao == "3":
            break
        else:
            print("Opcao invalida, tente novamente.")


if __name__ == "__main__":
    menu_pedidos()
