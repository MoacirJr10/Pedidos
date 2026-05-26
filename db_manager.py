import sqlite3
import os

class DBManager:
    def __init__(self, db_file="pedidos.db"):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        """Garante que a tabela no banco SQLite exista ao iniciar o sistema."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS pedidos (
                                                                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                  nome TEXT NOT NULL,
                                                                  telefone TEXT NOT NULL,
                                                                  detalhes TEXT NOT NULL,
                                                                  status TEXT NOT NULL,
                                                                  data_hora TEXT NOT NULL
                           )
                           """)
            conn.commit()

    def add_pedido(self, nome, telefone, detalhes, status, data_hora):
        """Adiciona um novo pedido ao banco de dados."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pedidos (nome, telefone, detalhes, status, data_hora) VALUES (?, ?, ?, ?, ?)",
                (nome, telefone, detalhes, status, data_hora)
            )
            conn.commit()
        return cursor.lastrowid

    def get_all_pedidos(self):
        """Retorna todos os pedidos do banco de dados, ordenados do mais recente para o mais antigo."""
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pedidos ORDER BY id DESC")
            return cursor.fetchall()

    def update_pedido_status(self, pedido_id, status):
        """Atualiza o status de um pedido."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
            conn.commit()

    def delete_concluidos(self):
        """Apaga todos os pedidos com status 'Pronto' do banco de dados."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pedidos WHERE status = 'Pronto'")
            conn.commit()
