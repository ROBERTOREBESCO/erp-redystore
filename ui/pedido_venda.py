import sys
import sqlite3
import urllib.request
import urllib.parse
import json

from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QDateEdit,
    QComboBox,
    QAbstractItemView,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
)


# ==============================================================
# CAMINHO DO BANCO
# ==============================================================

BANCO_DADOS = "erp.db"


# ==============================================================
# JANELA DE PESQUISA DE CLIENTES
# ==============================================================

class PesquisaClientes(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cliente_selecionado = None

        self.setWindowTitle("Pesquisar Cliente")
        self.setMinimumSize(700, 500)

        self.criar_interface()
        self.carregar_clientes()

    # ----------------------------------------------------------
    # INTERFACE
    # ----------------------------------------------------------

    def criar_interface(self):

        layout = QVBoxLayout(self)

        titulo = QLabel("Pesquisa de Clientes")
        titulo.setObjectName("tituloPesquisa")

        layout.addWidget(titulo)

        # Campo de pesquisa
        linha_pesquisa = QHBoxLayout()

        label = QLabel("Pesquisar:")
        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Digite o nome ou código do cliente...")

        self.pesquisa.textChanged.connect(self.filtrar_clientes)

        linha_pesquisa.addWidget(label)
        linha_pesquisa.addWidget(self.pesquisa)

        layout.addLayout(linha_pesquisa)

        # Lista
        self.lista = QListWidget()

        self.lista.itemDoubleClicked.connect(
            self.selecionar_cliente
        )

        layout.addWidget(self.lista)

        # Botões
        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
        )

        botao_selecionar = QPushButton("Selecionar Cliente")
        botao_selecionar.clicked.connect(
            self.selecionar_cliente
        )

        botoes.addButton(
            botao_selecionar,
            QDialogButtonBox.ButtonRole.AcceptRole
        )

        botoes.rejected.connect(self.reject)

        layout.addWidget(botoes)

    # ----------------------------------------------------------
    # CARREGAR CLIENTES
    # ----------------------------------------------------------

    def carregar_clientes(self):

        self.lista.clear()

        try:

            conexao = sqlite3.connect(BANCO_DADOS)

            cursor = conexao.cursor()

            # Primeiro tenta a tabela clientes
            cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='clientes'"
            )

            tabela = cursor.fetchone()

            if not tabela:

                conexao.close()

                item = QListWidgetItem(
                    "Nenhuma tabela 'clientes' encontrada no banco de dados."
                )

                self.lista.addItem(item)

                return

            cursor.execute(
                "PRAGMA table_info(clientes)"
            )

            colunas = cursor.fetchall()

            nomes_colunas = [
                coluna[1].lower()
                for coluna in colunas
            ]

            coluna_codigo = self.encontrar_coluna(
                nomes_colunas,
                [
                    "id",
                    "idcliente",
                    "codigo",
                    "codcliente",
                    "cod_cliente",
                ]
            )

            coluna_nome = self.encontrar_coluna(
                nomes_colunas,
                [
                    "nome",
                    "nomecliente",
                    "nome_cliente",
                    "razaosocial",
                    "razao_social",
                ]
            )

            if not coluna_codigo or not coluna_nome:

                conexao.close()

                item = QListWidgetItem(
                    "A tabela clientes existe, "
                    "mas as colunas de código/nome não foram identificadas."
                )

                self.lista.addItem(item)

                return

            cursor.execute(
                f"""
                SELECT "{coluna_codigo}", "{coluna_nome}"
                FROM clientes
                ORDER BY "{coluna_nome}"
                """
            )

            clientes = cursor.fetchall()

            conexao.close()

            for codigo, nome in clientes:

                item = QListWidgetItem(
                    f"{codigo}  -  {nome}"
                )

                item.setData(
                    Qt.ItemDataRole.UserRole,
                    {
                        "codigo": codigo,
                        "nome": nome,
                    }
                )

                self.lista.addItem(item)

        except Exception as erro:

            item = QListWidgetItem(
                f"Erro ao carregar clientes: {erro}"
            )

            self.lista.addItem(item)

    # ----------------------------------------------------------
    # ENCONTRAR COLUNA
    # ----------------------------------------------------------

    def encontrar_coluna(self, colunas, possibilidades):

        for possibilidade in possibilidades:

            if possibilidade.lower() in colunas:
                indice = colunas.index(
                    possibilidade.lower()
                )

                return colunas[indice]

        return None

    # ----------------------------------------------------------
    # FILTRAR
    # ----------------------------------------------------------

    def filtrar_clientes(self):

        texto = self.pesquisa.text().strip().lower()

        for indice in range(self.lista.count()):

            item = self.lista.item(indice)

            item.setHidden(
                texto not in item.text().lower()
            )

    # ----------------------------------------------------------
    # SELECIONAR
    # ----------------------------------------------------------

    def selecionar_cliente(self):

        item = self.lista.currentItem()

        if not item:
            return

        dados = item.data(
            Qt.ItemDataRole.UserRole
        )

        if dados:

            self.cliente_selecionado = dados

            self.accept()


# ==============================================================
# PEDIDO DE VENDA
# ==============================================================

class PedidoVenda(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "RedyStore - Pedido de Venda"
        )

        self.setMinimumSize(
            1250,
            780
        )

        self.numero_pedido_atual = 1

        self.criar_interface()

        self.aplicar_estilo()

        self.atualizar_data_hora()

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.atualizar_data_hora
        )

        self.timer.start(1000)

    # ==========================================================
    # INTERFACE PRINCIPAL
    # ==========================================================

    def criar_interface(self):

        central = QWidget()

        self.setCentralWidget(central)

        layout_principal = QHBoxLayout(
            central
        )

        layout_principal.setContentsMargins(
            8, 8, 8, 8
        )

        layout_principal.setSpacing(8)

        # ------------------------------------------------------
        # BARRA LATERAL
        # ------------------------------------------------------

        self.criar_barra_lateral(
            layout_principal
        )

        # ------------------------------------------------------
        # AREA PRINCIPAL
        # ------------------------------------------------------

        area = QWidget()

        layout_area = QVBoxLayout(area)

        layout_area.setContentsMargins(
            0, 0, 0, 0
        )

        layout_area.setSpacing(6)

        layout_principal.addWidget(
            area,
            1
        )

        # ------------------------------------------------------
        # IDENTIFICACAO DO PEDIDO
        # ------------------------------------------------------

        layout_area.addWidget(
            self.criar_identificacao_pedido()
        )

        # ------------------------------------------------------
        # ABAS
        # ------------------------------------------------------

        self.criar_abas()

        layout_area.addWidget(
            self.abas,
            1
        )

    # ==========================================================
    # IDENTIFICACAO DO PEDIDO
    # ==========================================================

    def criar_identificacao_pedido(self):

        painel = QFrame()

        painel.setObjectName(
            "painelIdentificacao"
        )

        layout = QGridLayout(
            painel
        )

        layout.setContentsMargins(
            10, 8, 10, 8
        )

        layout.setHorizontalSpacing(7)
        layout.setVerticalSpacing(7)

        # ------------------------------------------------------
        # LINHA 1
        # ------------------------------------------------------

        label = QLabel("Nº Pedido")

        self.pedido = QLineEdit()

        self.pedido.setReadOnly(True)

        self.pedido.setText(
            self.gerar_numero_pedido()
        )

        layout.addWidget(
            label,
            0,
            0
        )

        layout.addWidget(
            self.pedido,
            0,
            1
        )

        # DATA/HORA

        label = QLabel(
            "Data/Hora do Pedido"
        )

        self.data_emissao = QLineEdit()

        self.data_emissao.setReadOnly(
            True
        )

        layout.addWidget(
            label,
            0,
            2
        )

        layout.addWidget(
            self.data_emissao,
            0,
            3
        )

        # PREVISAO

        label = QLabel(
            "Previsão de Entrega"
        )

        self.data_entrega = QDateEdit()

        self.data_entrega.setDate(
            QDate.currentDate()
        )

        self.data_entrega.setCalendarPopup(
            True
        )

        self.data_entrega.setDisplayFormat(
            "dd/MM/yyyy"
        )

        layout.addWidget(
            label,
            0,
            4
        )

        layout.addWidget(
            self.data_entrega,
            0,
            5
        )

        # CONDICAO

        label = QLabel(
            "Venda"
        )

        self.condicao_venda = QComboBox()

        self.condicao_venda.addItems(
            [
                "À Vista",
                "A Prazo",
            ]
        )

        layout.addWidget(
            label,
            0,
            6
        )

        layout.addWidget(
            self.condicao_venda,
            0,
            7
        )

        # ------------------------------------------------------
        # LINHA 2 - CLIENTE
        # ------------------------------------------------------

        label = QLabel(
            "Código Cliente"
        )

        self.codigo_cliente = QLineEdit()

        self.codigo_cliente.setMaximumWidth(
            120
        )

        self.codigo_cliente.returnPressed.connect(
            self.buscar_cliente_codigo
        )

        layout.addWidget(
            label,
            1,
            0
        )

        layout.addWidget(
            self.codigo_cliente,
            1,
            1
        )

        botao_pesquisa = QPushButton(
            "🔎"
        )

        botao_pesquisa.setObjectName(
            "botaoPesquisa"
        )

        botao_pesquisa.setFixedWidth(
            42
        )

        botao_pesquisa.clicked.connect(
            self.pesquisar_cliente
        )

        layout.addWidget(
            botao_pesquisa,
            1,
            2
        )

        # NOME

        label = QLabel(
            "Nome do Cliente"
        )

        self.nome_cliente = QLineEdit()

        layout.addWidget(
            label,
            1,
            3
        )

        layout.addWidget(
            self.nome_cliente,
            1,
            4,
            1,
            4
        )

        # ------------------------------------------------------
        # LINHA 3 - CEP E ENDERECO
        # ------------------------------------------------------

        label = QLabel(
            "CEP"
        )

        self.cep = QLineEdit()

        self.cep.setMaximumWidth(
            110
        )

        self.cep.setPlaceholderText(
            "00000-000"
        )

        self.cep.editingFinished.connect(
            self.consultar_cep
        )

        layout.addWidget(
            label,
            2,
            0
        )

        layout.addWidget(
            self.cep,
            2,
            1
        )

        # ENDERECO

        label = QLabel(
            "Endereço"
        )

        self.endereco = QLineEdit()

        layout.addWidget(
            label,
            2,
            2
        )

        layout.addWidget(
            self.endereco,
            2,
            3,
            1,
            3
        )

        # NUMERO

        label = QLabel(
            "Número"
        )

        self.numero = QLineEdit()

        self.numero.setMaximumWidth(
            80
        )

        layout.addWidget(
            label,
            2,
            6
        )

        layout.addWidget(
            self.numero,
            2,
            7
        )

        # ------------------------------------------------------
        # LINHA 4
        # ------------------------------------------------------

        label = QLabel(
            "Bairro"
        )

        self.bairro = QLineEdit()

        layout.addWidget(
            label,
            3,
            0
        )

        layout.addWidget(
            self.bairro,
            3,
            1,
            1,
            3
        )

        label = QLabel(
            "Cidade"
        )

        self.cidade = QLineEdit()

        layout.addWidget(
            label,
            3,
            4
        )

        layout.addWidget(
            self.cidade,
            3,
            5
        )

        label = QLabel(
            "UF"
        )

        self.uf = QLineEdit()

        self.uf.setMaximumWidth(
            55
        )

        layout.addWidget(
            label,
            3,
            6
        )

        layout.addWidget(
            self.uf,
            3,
            7
        )

        return painel

    # ==========================================================
    # NUMERO DO PEDIDO
    # ==========================================================

    def gerar_numero_pedido(self):

        try:

            conexao = sqlite3.connect(
                BANCO_DADOS
            )

            cursor = conexao.cursor()

            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                """
            )

            tabelas = [
                linha[0]
                for linha in cursor.fetchall()
            ]

            conexao.close()

        except Exception:

            tabelas = []

        # Por enquanto começa em 000001.
        # Depois vamos ligar ao cadastro definitivo
        # dos pedidos.

        return "000001"

    # ==========================================================
    # BARRA LATERAL
    # ==========================================================

    def criar_barra_lateral(
        self,
        layout_principal
    ):

        painel = QFrame()

        painel.setObjectName(
            "barraLateral"
        )

        painel.setFixedWidth(
            78
        )

        layout = QVBoxLayout(
            painel
        )

        layout.setContentsMargins(
            3, 3, 3, 3
        )

        layout.setSpacing(5)

        botoes = [
            ("✚", "Novo", "F3"),
            ("✓", "Grava", "F4"),
            ("✕", "Cancela", "F8"),
            ("−", "Deleta", "F7"),
            ("⌕", "Procura", "F5"),
            ("▣", "Imprime", "F6"),
            ("✉", "E-Mail", ""),
            ("?", "Ajuda", "F1"),
            ("⇥", "Sair", "F12"),
        ]

        for simbolo, texto, tecla in botoes:

            botao = QPushButton()

            botao.setObjectName(
                "botaoLateral"
            )

            botao.setFixedHeight(
                58
            )

            if tecla:

                botao.setText(
                    f"{simbolo}\n{texto}\n{tecla}"
                )

            else:

                botao.setText(
                    f"{simbolo}\n{texto}"
                )

            if texto == "Novo":

                botao.clicked.connect(
                    self.novo_pedido
                )

            elif texto == "Grava":

                botao.clicked.connect(
                    self.gravar_pedido
                )

            elif texto == "Cancela":

                botao.clicked.connect(
                    self.cancelar_pedido
                )

            elif texto == "Sair":

                botao.clicked.connect(
                    self.close
                )

            layout.addWidget(
                botao
            )

        layout.addStretch()

        botao_gerar = QPushButton(
            "▣\nGerar\nPedido"
        )

        botao_gerar.setObjectName(
            "botaoGerar"
        )

        botao_gerar.setFixedHeight(
            70
        )

        layout.addWidget(
            botao_gerar
        )

        botao_copiar = QPushButton(
            "▤\nCopiar\nP.V."
        )

        botao_copiar.setObjectName(
            "botaoLateral"
        )

        botao_copiar.setFixedHeight(
            65
        )

        layout.addWidget(
            botao_copiar
        )

        botao_enviar = QPushButton(
            "➤\nEnviar\nPedido"
        )

        botao_enviar.setObjectName(
            "botaoEnviar"
        )

        botao_enviar.setFixedHeight(
            65
        )

        layout.addWidget(
            botao_enviar
        )

        layout_principal.addWidget(
            painel
        )

    # ==========================================================
    # ABAS
    # ==========================================================

    def criar_abas(self):

        self.abas = QTabWidget()

        self.abas.setObjectName(
            "abas"
        )

        self.criar_aba_itens()

        self.criar_aba_simples(
            "Transporte"
        )

        self.criar_aba_totais()

        self.criar_aba_simples(
            "Fiscal"
        )

        self.criar_aba_financeiro()

        self.criar_aba_simples(
            "Comercial"
        )

        self.criar_aba_simples(
            "Observações"
        )

    # ==========================================================
    # ABA ITENS
    # ==========================================================

    def criar_aba_itens(self):

        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        layout.setContentsMargins(
            4, 4, 4, 4
        )

        barra = QHBoxLayout()

        botao_adicionar = QPushButton(
            "＋"
        )

        botao_adicionar.setObjectName(
            "botaoAdicionar"
        )

        botao_adicionar.setFixedSize(
            40,
            40
        )

        botao_adicionar.clicked.connect(
            self.adicionar_item
        )

        botao_excluir = QPushButton(
            "×"
        )

        botao_excluir.setObjectName(
            "botaoExcluir"
        )

        botao_excluir.setFixedSize(
            40,
            40
        )

        botao_excluir.clicked.connect(
            self.excluir_item
        )

        barra.addWidget(
            botao_adicionar
        )

        barra.addWidget(
            botao_excluir
        )

        barra.addStretch()

        layout.addLayout(
            barra
        )

        # ------------------------------------------------------
        # TABELA
        # ------------------------------------------------------

        self.tabela_itens = QTableWidget()

        colunas = [
            "Código",
            "Produto",
            "Descrição",
            "Tabela",
            "Quantidade",
            "Unidade",
            "Valor Unitário",
            "Desc. Promocional",
            "Desc. Comercial",
            "Acr./Desc.",
            "Valor Total",
            "IPI",
            "ICMS ST",
            "ICMS",
            "Valor Total",
        ]

        self.tabela_itens.setColumnCount(
            len(colunas)
        )

        self.tabela_itens.setHorizontalHeaderLabels(
            colunas
        )

        self.tabela_itens.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.tabela_itens.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.tabela_itens.setAlternatingRowColors(
            True
        )

        header = (
            self.tabela_itens.horizontalHeader()
        )

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        for coluna in range(
            3,
            len(colunas)
        ):

            header.setSectionResizeMode(
                coluna,
                QHeaderView.ResizeMode.ResizeToContents
            )

        produtos = [
            (
                "9",
                "Biscoito Broa de Amendoim 250g",
                "250g",
                "175",
                "10,0000",
                "CX 15 Und",
                "67,8000"
            ),
            (
                "45",
                "Biscoito Fofinho de Amendoim",
                "250g",
                "175",
                "2,0000",
                "CX 15 Und",
                "99,9000"
            ),
            (
                "71",
                "Biscoito de Amendoim com Chocolate",
                "250g",
                "175",
                "3,0000",
                "CX 15 Und",
                "78,4500"
            ),
            (
                "70",
                "Biscoito de Amendoim com Chocolate",
                "250g",
                "175",
                "1,0000",
                "CX 15 Und",
                "78,4500"
            ),
            (
                "30",
                "Biscoito Amanteigado 240g",
                "240g",
                "175",
                "2,0000",
                "CX 15 Und",
                "58,5000"
            ),
            (
                "17",
                "Pão de Mel com Chocolate",
                "250g",
                "175",
                "2,0000",
                "CX 15 Und",
                "78,0000"
            ),
            (
                "47",
                "Pão de Mel com Chocolate Branco",
                "250g",
                "175",
                "1,0000",
                "CX 15 Und",
                "78,0000"
            ),
            (
                "1222",
                "Biscoito de Maracujá 240g",
                "240g",
                "175",
                "1,0000",
                "CX 15 Und",
                "58,5000"
            ),
            (
                "1214",
                "Biscoito de Limão 240g",
                "240g",
                "175",
                "1,0000",
                "CX 15 Und",
                "58,5000"
            ),
            (
                "104",
                "Pé de Moça - Pote 960g",
                "960g",
                "175",
                "1,0000",
                "Pote 32 Unid.",
                "49,9200"
            ),
        ]

        for produto in produtos:

            self.adicionar_linha_produto(
                produto
            )

        layout.addWidget(
            self.tabela_itens,
            1
        )

        # ------------------------------------------------------
        # DADOS DO PRODUTO
        # ------------------------------------------------------

        painel_produto = QFrame()

        painel_produto.setObjectName(
            "painelProduto"
        )

        grid = QGridLayout(
            painel_produto
        )

        grid.setContentsMargins(
            5, 4, 5, 4
        )

        grid.addWidget(
            QLabel("Descrição do Produto"),
            0,
            0
        )

        grid.addWidget(
            QLabel("Referência do Produto"),
            0,
            1
        )

        grid.addWidget(
            QLabel("Característica do Produto"),
            0,
            2
        )

        self.descricao_produto = QLineEdit(
            "Pão de Mel com Chocolate Branco 250g"
        )

        self.referencia_produto = QLineEdit(
            "KLAIN"
        )

        self.caracteristica_produto = QLineEdit(
            "Forno Contínuo"
        )

        grid.addWidget(
            self.descricao_produto,
            1,
            0
        )

        grid.addWidget(
            self.referencia_produto,
            1,
            1
        )

        grid.addWidget(
            self.caracteristica_produto,
            1,
            2
        )

        grid.setColumnStretch(
            0,
            5
        )

        grid.setColumnStretch(
            1,
            3
        )

        grid.setColumnStretch(
            2,
            3
        )

        layout.addWidget(
            painel_produto
        )

        layout.addWidget(
            self.criar_painel_totais()
        )

        self.abas.addTab(
            aba,
            "Itens"
        )

    # ==========================================================
    # LINHA DE PRODUTO
    # ==========================================================

    def adicionar_linha_produto(
        self,
        produto
    ):

        linha = (
            self.tabela_itens.rowCount()
        )

        self.tabela_itens.insertRow(
            linha
        )

        (
            codigo,
            nome,
            descricao,
            tabela,
            qtd,
            unidade,
            valor
        ) = produto

        valor_float = float(
            valor.replace(",", ".")
        )

        qtd_float = float(
            qtd.replace(",", ".")
        )

        total = (
            qtd_float *
            valor_float
        )

        valores = [
            codigo,
            nome,
            descricao,
            tabela,
            qtd,
            unidade,
            f"{valor_float:.4f}".replace(".", ","),
            "0,0000",
            "0,0000",
            "0,0000",
            f"{total:.2f}".replace(".", ","),
            "0,00",
            "0,00",
            "0,00",
            f"{total:.2f}".replace(".", ","),
        ]

        for coluna, valor_celula in enumerate(
            valores
        ):

            item = QTableWidgetItem(
                str(valor_celula)
            )

            if coluna in [
                0,
                3,
                4,
                6,
                7,
                8,
                9,
                10,
                11,
                12,
                13,
                14,
            ]:

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight |
                    Qt.AlignmentFlag.AlignVCenter
                )

            self.tabela_itens.setItem(
                linha,
                coluna,
                item
            )

    # ==========================================================
    # ABAS SIMPLES
    # ==========================================================

    def criar_aba_simples(
        self,
        nome
    ):

        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        texto = QLabel(
            f"Informações de {nome}\n\n"
            "Esta área será configurada na próxima etapa."
        )

        texto.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        layout.addWidget(
            texto
        )

        layout.addStretch()

        self.abas.addTab(
            aba,
            nome
        )

    # ==========================================================
    # ABA TOTAIS
    # ==========================================================

    def criar_aba_totais(self):

        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        titulo = QLabel(
            "Totais do Pedido"
        )

        titulo.setObjectName(
            "tituloAba"
        )

        layout.addWidget(
            titulo
        )

        grid = QGridLayout()

        campos = [
            ("Produtos", "1.709,52"),
            ("Desconto", "0,00"),
            ("Financeiro", "0,00"),
            ("Frete", "0,00"),
            ("Seguro", "0,00"),
            ("IPI", "0,00"),
            ("ICMS ST", "0,00"),
            ("Retenção", "0,00"),
            ("Valor Total", "1.709,52"),
        ]

        for linha, (nome, valor) in enumerate(
            campos
        ):

            label = QLabel(nome)

            campo = QLineEdit(valor)

            campo.setReadOnly(
                True
            )

            grid.addWidget(
                label,
                linha,
                0
            )

            grid.addWidget(
                campo,
                linha,
                1
            )

        layout.addLayout(
            grid
        )

        layout.addStretch()

        self.abas.addTab(
            aba,
            "Totais"
        )

    # ==========================================================
    # ABA FINANCEIRO
    # ==========================================================

    def criar_aba_financeiro(self):

        aba = QWidget()

        layout = QVBoxLayout(
            aba
        )

        titulo = QLabel(
            "Financeiro do Pedido"
        )

        titulo.setObjectName(
            "tituloAba"
        )

        layout.addWidget(
            titulo
        )

        grid = QGridLayout()

        campos = [
            (
                "Forma de Pagamento",
                "Carteira - Dinheiro"
            ),
            (
                "Condição",
                "49 - Apresentação"
            ),
            (
                "Parcelas",
                "1"
            ),
            (
                "Valor Entrada",
                "0,00"
            ),
            (
                "Valor Financiado",
                "1.709,52"
            ),
        ]

        for linha, (nome, valor) in enumerate(
            campos
        ):

            label = QLabel(nome)

            campo = QLineEdit(valor)

            grid.addWidget(
                label,
                linha,
                0
            )

            grid.addWidget(
                campo,
                linha,
                1
            )

        layout.addLayout(
            grid
        )

        layout.addStretch()

        self.abas.addTab(
            aba,
            "Financeiro"
        )

    # ==========================================================
    # PAINEL DE TOTAIS
    # ==========================================================

    def criar_painel_totais(self):

        painel = QFrame()

        painel.setObjectName(
            "painelTotais"
        )

        layout = QHBoxLayout(
            painel
        )

        campos = [
            ("Qtd Itens", "10"),
            ("Total Bruto", "1.709,52"),
            ("Desconto", "0,00"),
            ("Financeiro", "0,00"),
            ("Frete+Seg+ODA", "0,00"),
            ("IPI", "0,00"),
            ("ICMS ST", "0,00"),
            ("Retenção", "0,00"),
            ("Valor Total(=)", "1.709,52"),
        ]

        self.campos_totais = {}

        for nome, valor in campos:

            bloco = QVBoxLayout()

            label = QLabel(nome)

            label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            campo = QLineEdit(valor)

            campo.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

            self.campos_totais[nome] = campo

            bloco.addWidget(
                label
            )

            bloco.addWidget(
                campo
            )

            layout.addLayout(
                bloco
            )

        return painel

    # ==========================================================
    # PESQUISAR CLIENTE
    # ==========================================================

    def pesquisar_cliente(self):

        janela = PesquisaClientes(
            self
        )

        resultado = janela.exec()

        if resultado == QDialog.DialogCode.Accepted:

            dados = (
                janela.cliente_selecionado
            )

            if dados:

                self.codigo_cliente.setText(
                    str(dados["codigo"])
                )

                self.nome_cliente.setText(
                    str(dados["nome"])
                )

                self.buscar_dados_cliente(
                    dados["codigo"]
                )

    # ==========================================================
    # BUSCAR CLIENTE PELO CODIGO
    # ==========================================================

    def buscar_cliente_codigo(self):

        codigo = (
            self.codigo_cliente.text()
            .strip()
        )

        if not codigo:

            return

        self.buscar_dados_cliente(
            codigo
        )

    # ==========================================================
    # BUSCAR DADOS DO CLIENTE
    # ==========================================================

    def buscar_dados_cliente(
        self,
        codigo
    ):

        try:

            conexao = sqlite3.connect(
                BANCO_DADOS
            )

            cursor = conexao.cursor()

            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name='clientes'
                """
            )

            if not cursor.fetchone():

                conexao.close()

                QMessageBox.warning(
                    self,
                    "Cliente",
                    "A tabela 'clientes' não foi encontrada no banco."
                )

                return

            cursor.execute(
                "PRAGMA table_info(clientes)"
            )

            colunas_info = cursor.fetchall()

            colunas = [
                linha[1]
                for linha in colunas_info
            ]

            mapa = {
                coluna.lower(): coluna
                for coluna in colunas
            }

            codigo_coluna = self.localizar_coluna(
                mapa,
                [
                    "id",
                    "idcliente",
                    "codigo",
                    "codcliente",
                    "cod_cliente",
                ]
            )

            nome_coluna = self.localizar_coluna(
                mapa,
                [
                    "nome",
                    "nomecliente",
                    "nome_cliente",
                    "razaosocial",
                    "razao_social",
                ]
            )

            if not codigo_coluna:

                conexao.close()

                QMessageBox.warning(
                    self,
                    "Cliente",
                    "Não foi possível identificar o código do cliente."
                )

                return

            colunas_buscar = [
                nome_coluna,
                self.localizar_coluna(
                    mapa,
                    ["cep"]
                ),
                self.localizar_coluna(
                    mapa,
                    ["endereco", "logradouro"]
                ),
                self.localizar_coluna(
                    mapa,
                    ["numero", "numero_endereco"]
                ),
                self.localizar_coluna(
                    mapa,
                    ["bairro"]
                ),
                self.localizar_coluna(
                    mapa,
                    ["cidade"]
                ),
                self.localizar_coluna(
                    mapa,
                    ["uf", "estado"]
                ),
            ]

            colunas_validas = [
                coluna
                for coluna in colunas_buscar
                if coluna
            ]

            if not nome_coluna:

                conexao.close()

                return

            select_sql = ", ".join(
                f'"{coluna}"'
                for coluna in colunas_validas
            )

            cursor.execute(
                f"""
                SELECT {select_sql}
                FROM clientes
                WHERE "{codigo_coluna}" = ?
                LIMIT 1
                """,
                (codigo,)
            )

            cliente = cursor.fetchone()

            conexao.close()

            if not cliente:

                QMessageBox.information(
                    self,
                    "Cliente",
                    "Cliente não encontrado."
                )

                return

            dados = dict(
                zip(
                    colunas_validas,
                    cliente
                )
            )

            self.preencher_dados_cliente(
                dados
            )

        except Exception as erro:

            QMessageBox.critical(
                self,
                "Erro",
                f"Erro ao buscar cliente:\n\n{erro}"
            )

    # ==========================================================
    # LOCALIZAR COLUNA
    # ==========================================================

    def localizar_coluna(
        self,
        mapa,
        possibilidades
    ):

        for nome in possibilidades:

            if nome.lower() in mapa:

                return mapa[
                    nome.lower()
                ]

        return None

    # ==========================================================
    # PREENCHER CLIENTE
    # ==========================================================

    def preencher_dados_cliente(
        self,
        dados
    ):

        def obter(
            possibilidades
        ):

            for nome in possibilidades:

                for chave in dados:

                    if chave.lower() == nome.lower():

                        valor = dados[chave]

                        if valor is None:

                            return ""

                        return str(valor)

            return ""

        self.nome_cliente.setText(
            obter(
                [
                    "nome",
                    "nomecliente",
                    "nome_cliente",
                    "razaosocial",
                    "razao_social",
                ]
            )
        )

        self.cep.setText(
            obter(
                ["cep"]
            )
        )

        self.endereco.setText(
            obter(
                [
                    "endereco",
                    "logradouro",
                ]
            )
        )

        self.numero.setText(
            obter(
                [
                    "numero",
                    "numero_endereco",
                ]
            )
        )

        self.bairro.setText(
            obter(
                ["bairro"]
            )
        )

        self.cidade.setText(
            obter(
                ["cidade"]
            )
        )

        self.uf.setText(
            obter(
                [
                    "uf",
                    "estado",
                ]
            )
        )

    # ==========================================================
    # CONSULTAR CEP
    # ==========================================================

    def consultar_cep(self):

        cep = (
            self.cep.text()
            .strip()
        )

        cep = (
            cep.replace("-", "")
            .replace(".", "")
            .replace(" ", "")
        )

        if len(cep) != 8:

            return

        try:

            url = (
                "https://viacep.com.br/ws/"
                + cep
                + "/json/"
            )

            requisicao = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                    "RedyStore/1.0"
                }
            )

            with urllib.request.urlopen(
                requisicao,
                timeout=8
            ) as resposta:

                dados = json.loads(
                    resposta.read().decode(
                        "utf-8"
                    )
                )

            if dados.get("erro"):

                QMessageBox.warning(
                    self,
                    "CEP",
                    "CEP não encontrado."
                )

                return

            self.cep.setText(
                f"{cep[:5]}-{cep[5:]}"
            )

            self.endereco.setText(
                dados.get(
                    "logradouro",
                    ""
                )
            )

            self.bairro.setText(
                dados.get(
                    "bairro",
                    ""
                )
            )

            self.cidade.setText(
                dados.get(
                    "localidade",
                    ""
                )
            )

            self.uf.setText(
                dados.get(
                    "uf",
                    ""
                )
            )

            self.numero.setFocus()

        except Exception as erro:

            QMessageBox.warning(
                self,
                "CEP",
                "Não foi possível consultar o CEP.\n\n"
                "Verifique sua conexão com a internet."
            )

            print(
                "Erro consulta CEP:",
                erro
            )

    # ==========================================================
    # ADICIONAR ITEM
    # ==========================================================

    def adicionar_item(self):

        produto = (
            "0",
            "Novo Produto",
            "",
            "175",
            "1,0000",
            "UN",
            "0,0000",
        )

        self.adicionar_linha_produto(
            produto
        )

        linha = (
            self.tabela_itens.rowCount()
            - 1
        )

        self.tabela_itens.selectRow(
            linha
        )

    # ==========================================================
    # EXCLUIR ITEM
    # ==========================================================

    def excluir_item(self):

        linha = (
            self.tabela_itens.currentRow()
        )

        if linha >= 0:

            self.tabela_itens.removeRow(
                linha
            )

    # ==========================================================
    # NOVO PEDIDO
    # ==========================================================

    def novo_pedido(self):

        self.numero_pedido_atual += 1

        self.pedido.setText(
            f"{self.numero_pedido_atual:06d}"
        )

        self.data_emissao.setText(
            datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        )

        self.codigo_cliente.clear()
        self.nome_cliente.clear()
        self.cep.clear()
        self.endereco.clear()
        self.numero.clear()
        self.bairro.clear()
        self.cidade.clear()
        self.uf.clear()

        self.data_entrega.setDate(
            QDate.currentDate()
        )

        self.tabela_itens.setRowCount(
            0
        )

        self.codigo_cliente.setFocus()

    # ==========================================================
    # GRAVAR
    # ==========================================================

    def gravar_pedido(self):

        print(
            "Pedido preparado para gravacao."
        )

        QMessageBox.information(
            self,
            "Pedido de Venda",
            "Pedido preparado para gravação."
        )

    # ==========================================================
    # CANCELAR
    # ==========================================================

    def cancelar_pedido(self):

        resposta = QMessageBox.question(
            self,
            "Cancelar Pedido",
            "Deseja cancelar o pedido atual?"
        )

        if resposta == QMessageBox.StandardButton.Yes:

            self.novo_pedido()

    # ==========================================================
    # DATA E HORA
    # ==========================================================

    def atualizar_data_hora(self):

        if hasattr(
            self,
            "data_emissao"
        ):

            self.data_emissao.setText(
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            )

    # ==========================================================
    # ESTILO
    # ==========================================================

    def aplicar_estilo(self):

        self.setStyleSheet("""

        QMainWindow {
            background: #dceeff;
            color: #173b5c;
        }

        QWidget {
            font-family: "Montserrat", "Segoe UI", Arial;
            font-size: 11px;
            color: #173b5c;
        }

        QFrame#barraLateral {
            background: #eaf5ff;
            border: 1px solid #8fb8d8;
            border-radius: 6px;
        }

        QFrame#painelIdentificacao {
            background: #eaf5ff;
            border: 1px solid #82afd0;
            border-radius: 6px;
        }

        QFrame#painelProduto {
            background: #f8fcff;
            border: 1px solid #a7c6df;
            border-radius: 4px;
        }

        QFrame#painelTotais {
            background: #eaf5ff;
            border: 1px solid #8fb8d8;
            border-radius: 4px;
        }

        QLabel {
            color: #173b5c;
            font-weight: bold;
        }

        QLineEdit,
        QComboBox,
        QDateEdit {
            background: #ffffff;
            color: #172b3d;
            border: 1px solid #8fb8d8;
            border-radius: 4px;
            padding: 4px;
            min-height: 22px;
        }

        QLineEdit:hover,
        QComboBox:hover,
        QDateEdit:hover {
            background: #f0f8ff;
            border: 1px solid #438bc2;
            color: #102a40;
            font-weight: bold;
        }

        QLineEdit:focus,
        QComboBox:focus,
        QDateEdit:focus {
            background: #f4fbff;
            border: 2px solid #438bc2;
            color: #102a40;
        }

        QPushButton {
            background: #dceeff;
            color: #173b5c;
            border: 1px solid #82afd0;
            border-radius: 4px;
            padding: 4px;
            font-weight: bold;
        }

        QPushButton:hover {
            background: #c7e5fb;
            color: #0b3557;
            border: 1px solid #438bc2;
        }

        QPushButton:pressed {
            background: #afd8f5;
        }

        QPushButton#botaoLateral {
            font-size: 9px;
            color: #173b5c;
        }

        QPushButton#botaoGerar {
            background: #c8e7fb;
            color: #174d70;
            border: 1px solid #5d9fca;
        }

        QPushButton#botaoEnviar {
            background: #d8f1e0;
            color: #205a35;
            border: 1px solid #75ad86;
        }

        QPushButton#botaoPesquisa {
            font-size: 17px;
            color: #174d70;
            background: #cce8fb;
        }

        QPushButton#botaoAdicionar {
            background: #cceaff;
            color: #1769a8;
            font-size: 24px;
            font-weight: bold;
        }

        QPushButton#botaoExcluir {
            background: #ffe1e1;
            color: #a82020;
            font-size: 24px;
            font-weight: bold;
        }

        QTabWidget::pane {
            border: 1px solid #8fb8d8;
            background: #ffffff;
        }

        QTabBar::tab {
            background: #cfe7f8;
            color: #173b5c;
            border: 1px solid #8fb8d8;
            padding: 7px 14px;
            margin-right: 2px;
            font-weight: bold;
        }

        QTabBar::tab:selected {
            background: #ffffff;
            color: #173b5c;
            border-bottom-color: #ffffff;
        }

        QTableWidget {
            background: #ffffff;
            color: #172b3d;
            alternate-background-color: #edf7ff;
            gridline-color: #b9cfdf;
            border: 1px solid #8fb8d8;
            selection-background-color: #c9e6fa;
            selection-color: #102a40;
        }

        QHeaderView::section {
            background: #d5eaf8;
            color: #173b5c;
            border: 1px solid #a8c3d7;
            padding: 4px;
            font-weight: bold;
        }

        QLabel#tituloAba {
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            color: #173b5c;
        }

        QLabel#tituloPesquisa {
            font-size: 18px;
            font-weight: bold;
            color: #173b5c;
            padding: 5px;
        }

        QListWidget {
            background: #ffffff;
            color: #172b3d;
            border: 1px solid #8fb8d8;
        }

        QListWidget::item {
            padding: 7px;
        }

        QListWidget::item:selected {
            background: #c9e6fa;
            color: #102a40;
        }

        """)


# ==============================================================
# PROGRAMA
# ==============================================================

def main():

    app = QApplication(
        sys.argv
    )

    janela = PedidoVenda()

    janela.showMaximized()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()