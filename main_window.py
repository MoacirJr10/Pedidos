import sys
from datetime import datetime
from PyQt6.QtCore import Qt, QUrl, QStandardPaths
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QMessageBox, QHeaderView, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from db_manager import DBManager
from whatsapp_handler import WhatsAppHandler

DB_FILE = "pedidos.db"

class SistemaPedidos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Pedidos - Alta Velocidade Balcão")
        self.setGeometry(100, 50, 1100, 700)

        self.db_manager = DBManager(DB_FILE)
        self.whatsapp_webview = QWebEngineView() # Criar o QWebEngineView aqui
        self.whatsapp_handler = WhatsAppHandler(self.whatsapp_webview)

        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # ---- ABA 1: PAINEL DE PEDIDOS ----
        self.aba_pedidos = QWidget()
        layout_principal = QVBoxLayout()

        # Layout para o formulário de novo pedido
        layout_form = QHBoxLayout()
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome do Cliente")
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("WhatsApp (DDD+Número)")
        self.input_detalhes = QLineEdit()
        self.input_detalhes.setPlaceholderText("O que ele pediu?")

        btn_salvar = QPushButton("Salvar Pedido")
        btn_salvar.setStyleSheet("background-color: #00a884; color: white; font-weight: bold; padding: 10px 15px; min-height: 25px; font-size: 13px;")
        btn_salvar.clicked.connect(self.salvar_pedido)

        layout_form.addWidget(self.input_nome)
        layout_form.addWidget(self.input_telefone)
        layout_form.addWidget(self.input_detalhes)
        layout_form.addWidget(btn_salvar)
        layout_principal.addLayout(layout_form)

        # Botão para limpar pedidos concluídos
        btn_limpar_concluidos = QPushButton("Limpar Pedidos Concluidos")
        btn_limpar_concluidos.setStyleSheet("background-color: #dc3545; color: white; font-weight: bold; padding: 10px 15px; min-height: 25px; font-size: 13px;")
        btn_limpar_concluidos.clicked.connect(self.limpar_pedidos_concluidos)
        layout_principal.addWidget(btn_limpar_concluidos)


        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["Nº", "Horário", "Cliente", "WhatsApp", "Pedido", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setColumnWidth(5, 220) # Largura fixa para a coluna "Ações"
        self.tabela.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout_principal.addWidget(self.tabela)

        self.aba_pedidos.setLayout(layout_principal)
        self.tabs.addTab(self.aba_pedidos, "📋 Painel de Pedidos")

        # ---- ABA 2: WHATSAPP WEB EMBUTIDO ----
        self.tabs.addTab(self.whatsapp_webview, "💬 WhatsApp Web") # Adicionar o QWebEngineView já configurado

        self.atualizar_tabela()

    def salvar_pedido(self):
        nome = self.input_nome.text()
        telefone = self.input_telefone.text()
        detalhes = self.input_detalhes.text()

        if not nome or not telefone or not detalhes:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos!")
            return

        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        try:
            self.db_manager.add_pedido(nome, telefone, detalhes, 'Em preparação', data_hora)
            self.input_nome.clear()
            self.input_telefone.clear()
            self.input_detalhes.clear()
            self.atualizar_tabela()
        except Exception as e:
            QMessageBox.critical(self, "Erro no Banco de Dados", f"Não foi possível salvar o pedido: {e}")

    def atualizar_tabela(self):
        self.tabela.setRowCount(0)
        try:
            pedidos = self.db_manager.get_all_pedidos()
        except Exception as e:
            QMessageBox.critical(self, "Erro no Banco de Dados", f"Não foi possível carregar os pedidos: {e}")
            return

        for row_number, pedido in enumerate(pedidos):
            self.tabela.insertRow(row_number)
            self.tabela.setItem(row_number, 0, QTableWidgetItem(f"#{pedido['id']}"))
            self.tabela.setItem(row_number, 1, QTableWidgetItem(pedido['data_hora']))
            self.tabela.setItem(row_number, 2, QTableWidgetItem(pedido['nome']))
            self.tabela.setItem(row_number, 3, QTableWidgetItem(pedido['telefone']))
            self.tabela.setItem(row_number, 4, QTableWidgetItem(pedido['detalhes']))

            status = pedido['status']
            action_layout = QHBoxLayout()
            action_widget = QWidget()

            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

            if status == "Em preparação":
                btn_acao = QPushButton("Mudar p/ Pronto ⚡")
                btn_acao.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 6px 10px; min-width: 120px; min-height: 20px; font-size: 11px;")
                btn_acao.clicked.connect(lambda checked, p_id=pedido['id'], p_nome=pedido['nome'], p_tel=pedido['telefone']: self.marcar_pronto(p_id, p_nome, p_tel))
                action_layout.addWidget(btn_acao)
            else: # status == "Pronto"
                lbl_notificado = QLabel("Notificado ✓")
                lbl_notificado.setStyleSheet("color: #155724; font-weight: bold; padding: 6px 0px; min-height: 20px; font-size: 11px;")
                btn_reenviar = QPushButton("Reenviar 📢")
                btn_reenviar.setStyleSheet("background-color: #00a884; color: white; font-weight: bold; padding: 6px 10px; min-width: 80px; min-height: 20px; font-size: 11px;")
                btn_reenviar.clicked.connect(lambda checked, p_id=pedido['id'], p_nome=pedido['nome'], p_tel=pedido['telefone']: self.reenviar_aviso(p_id, p_nome, p_tel))
                action_layout.addWidget(lbl_notificado)
                action_layout.addWidget(btn_reenviar)
            
            action_layout.addStretch(1)

            action_widget.setLayout(action_layout)
            self.tabela.setCellWidget(row_number, 5, action_widget)

    def marcar_pronto(self, pedido_id, nome, telefone):
        print(f"DEBUG: Chamado marcar_pronto para pedido_id={pedido_id}")
        try:
            self.db_manager.update_pedido_status(pedido_id, 'Pronto')
            print(f"DEBUG: Pedido {pedido_id} marcado como 'Pronto' no DB.")
        except Exception as e:
            QMessageBox.critical(self, "Erro no Banco de Dados", f"Não foi possível atualizar o status do pedido: {e}")
            return

        mensagem = f"Ei, {nome}! Seu pedido #{pedido_id} ficou pronto! 🎉 Pode vir retirar no balcão."
        self.whatsapp_handler.send_whatsapp_message(telefone, mensagem)
        self.tabs.setCurrentIndex(1) # Vai direto para a aba do WhatsApp
        self.atualizar_tabela() # Atualiza a tabela após marcar como pronto

    def reenviar_aviso(self, pedido_id, nome, telefone):
        print(f"DEBUG: Chamado reenviar_aviso para pedido_id={pedido_id}")
        mensagem = f"Ei, {nome}! Seu pedido #{pedido_id} ficou pronto! 🎉 Pode vir retirar no balcão."
        self.whatsapp_handler.send_whatsapp_message(telefone, mensagem)
        self.tabs.setCurrentIndex(1) # Vai direto para a aba do WhatsApp

    def limpar_pedidos_concluidos(self):
        print("DEBUG: Chamado limpar_pedidos_concluidos.")
        reply = QMessageBox.question(self, 'Confirmar Limpeza',
                                     "Tem certeza que deseja apagar TODOS os pedidos com status 'Pronto'? Esta ação é irreversível.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.delete_concluidos()
                QMessageBox.information(self, "Sucesso", "Pedidos concluídos foram apagados.")
                print("DEBUG: Pedidos com status 'Pronto' apagados do DB.")
                self.atualizar_tabela()
            except Exception as e:
                QMessageBox.critical(self, "Erro no Banco de Dados", f"Não foi possível apagar os pedidos: {e}")
