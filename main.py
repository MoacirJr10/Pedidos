import sys
from PyQt6.QtWidgets import QApplication
from main_window import SistemaPedidos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SistemaPedidos()
    window.show()
    sys.exit(app.exec())
