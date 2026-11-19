import re
import urllib.parse
from PyQt6.QtCore import QUrl, QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView

def normalizar_telefone(telefone):
    if not re.fullmatch(r"[+0-9 ()-]+", telefone.strip()):
        raise ValueError("Informe um telefone brasileiro válido.")
    numero = re.sub(r"[^0-9]", "", telefone)
    if len(numero) in (10, 11):
        numero = "55" + numero
    if not re.fullmatch(r"55[1-9][0-9][0-9]{8,9}", numero):
        raise ValueError("Use DDD e telefone de 8 ou 9 dígitos, com DDI 55 opcional.")
    return numero

class WhatsAppHandler:
    def __init__(self, parent_webview: QWebEngineView):
        self.webview = parent_webview
        self.perfil = QWebEngineProfile("whatsapp_profile", self.webview)
        data = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        self.perfil.setPersistentStoragePath(f"{data}/PedidosApp/whatsapp_data")
        self.perfil.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        self.webview.setPage(QWebEnginePage(self.perfil, self.webview))
        self.webview.setUrl(QUrl("https://web.whatsapp.com"))

    def send_whatsapp_message(self, telefone, mensagem_texto):
        numero = normalizar_telefone(telefone)
        query = urllib.parse.urlencode({"phone": numero, "text": mensagem_texto})
        self.webview.setUrl(QUrl("https://web.whatsapp.com/send?" + query))
        # Apenas abre uma mensagem. Envio e entrega não são comprovados.
