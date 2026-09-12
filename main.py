import importlib.util
from pathlib import Path
from types import ModuleType

from cadastro_clientes import menu_clientes
from pedidos import menu_pedidos


def carregar_modulo(caminho: Path, nome: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(nome, caminho)
    if spec is None or spec.loader is None:
        raise ImportError(f"Nao foi possivel carregar o modulo: {caminho}")

    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


produtos = carregar_modulo(
    Path(__file__).with_name("cadastro de produtos.py"),
    "cadastro_de_produtos",
)


def menu_principal() -> None:
    while True:
        print("\n=== ERP REDYSTORE ===")
        print("1 - Clientes")
        print("2 - Produtos")
        print("3 - Pedidos")
        print("4 - Sair")

        try:
            opcao = input("Escolha uma opcao: ")
        except EOFError:
            print("Entrada encerrada.")
            return

        if opcao == "1":
            menu_clientes()
        elif opcao == "2":
            produtos.menu()
        elif opcao == "3":
            menu_pedidos()
        elif opcao == "4":
            print("Saindo do ERP...")
            break
        else:
            print("Opcao invalida, tente novamente.")


if __name__ == "__main__":
    menu_principal()
