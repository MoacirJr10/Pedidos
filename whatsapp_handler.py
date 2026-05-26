import urllib.parse
from PyQt6.QtCore import QUrl, QStandardPaths
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView

class WhatsAppHandler:
    def __init__(self, parent_webview: QWebEngineView):
        self.webview = parent_webview
        self.msg_pendente = ""
        self._setup_webview_profile()

    def _setup_webview_profile(self):
        """Configura o perfil do QWebEngineView para persistência do login do WhatsApp Web."""
        profile_name = "whatsapp_profile"
        perfil = QWebEngineProfile(profile_name, self.webview)

        data_location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        profile_path = f"{data_location}/PedidosApp/whatsapp_data"
        perfil.setPersistentStoragePath(profile_path)
        print(f"DEBUG: WhatsApp Web persistent storage path: {profile_path}")

        perfil.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
        perfil.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.webview.setPage(QWebEnginePage(perfil, self.webview))
        self.webview.loadFinished.connect(self._injetar_texto_whatsapp)
        self.webview.setUrl(QUrl("https://web.whatsapp.com"))

    def send_whatsapp_message(self, telefone, mensagem_texto):
        """
        Gera o link do WhatsApp e carrega no QWebEngineView.
        A mensagem será injetada automaticamente após o carregamento.
        """
        self.msg_pendente = mensagem_texto
        print(f"DEBUG: Mensagem pendente definida: {self.msg_pendente}")

        telefone_limpo = "".join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith("55") and len(telefone_limpo) >= 10:
            telefone_limpo = f"55{telefone_limpo}"
        print(f"DEBUG: Telefone limpo: {telefone_limpo}")

        texto_url = urllib.parse.quote(self.msg_pendente)
        link_wa = f"https://web.whatsapp.com/send?phone={telefone_limpo}&text={texto_url}"
        print(f"DEBUG: Link do WhatsApp gerado: {link_wa}")

        self.webview.setUrl(QUrl(link_wa))

    def _injetar_texto_whatsapp(self):
        """Código executado quando o chat carrega para forçar o texto a aparecer no campo de digitação."""
        print(f"DEBUG: _injetar_texto_whatsapp chamado. msg_pendente: '{self.msg_pendente}'")
        if self.msg_pendente:
            js_script = """
            function forcarEnvio() {
                var caixaTexto = document.querySelector('div[contenteditable="true"][data-tab="10"]');
                if (!caixaTexto) caixaTexto = document.querySelector('div[contenteditable="true"]');
                if (caixaTexto) {
                    caixaTexto.focus();
                    console.log('Caixa de texto do WhatsApp focada.');
                } else {
                    console.log('Caixa de texto do WhatsApp não encontrada.');
                }
            }
            setTimeout(forcarEnvio, 1500);
            """
            try:
                self.webview.page().runJavaScript(js_script, self._js_callback)
                print("DEBUG: JavaScript para focar caixa de texto injetado.")
            except Exception as e:
                print(f"ERRO: Falha ao injetar JavaScript: {e}")
                # Não usamos QMessageBox aqui, pois esta classe não deve ter dependência direta de QtWidgets
                # A janela principal (main_window) será responsável por exibir mensagens de erro da UI
        else:
            print("DEBUG: msg_pendente está vazia, não injetando JavaScript.")

    def _js_callback(self, result):
        print(f"DEBUG: Resultado do JavaScript: {result}")
        self.msg_pendente = ""
        print("DEBUG: msg_pendente limpa após callback do JS.")
