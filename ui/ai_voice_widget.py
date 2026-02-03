from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView

class AiVoiceWidget(QWidget):
    def __init__(self, url="https://chatgpt.com/"):
        super().__init__()
        self.url = url
        self.setWindowTitle("Anywhere AI")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(320, 500) # Reduced compact size
        self.init_ui()
        self.load_url()

        # Center on screen
        self.center_on_screen()

    def center_on_screen(self):
         screen = self.screen().geometry()
         size = self.geometry()
         self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def get_bot_name(self):
        if "chatgpt" in self.url.lower():
            return "ChatGPT"
        elif "claude" in self.url.lower():
            return "Claude"
        elif "gemini" in self.url.lower():
            return "Gemini"
        elif "bard" in self.url.lower():
            return "Bard"
        else:
            return "AI Bot"

    def init_ui(self):
        # Main Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Main Container (Rounded, Glassmorphism style)
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 20px;
            }
        """)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(self.container)

        # Header / Toolbar
        self.header = QFrame()
        self.header.setStyleSheet("background: transparent; border: none;")
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(5, 5, 5, 10)

        # Bot Icon
        self.icon_label = QLabel()
        # Placeholder for dynamic icon, using a simple text or circle for now
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: #444;
                border-radius: 10px;
                padding: 5px 10px;
                color: white;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.icon_label.setText(self.get_bot_name())
        self.header_layout.addWidget(self.icon_label)

        self.header_layout.addStretch()

        # Play/Voice Button
        self.voice_btn = QPushButton("▸")
        self.voice_btn.setFixedSize(50, 40)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #888;
                color: black;
                border-radius: 10px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #aaa;
            }
        """)
        self.voice_btn.clicked.connect(self.toggle_voice_mode)
        self.header_layout.addWidget(self.voice_btn)

        # Chat Button
        self.chat_btn = QPushButton("Chat")
        self.chat_btn.setFixedSize(60, 40)
        self.chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #888;
                color: black;
                border-radius: 10px;
                font-weight: bold;
            }
             QPushButton:hover {
                background-color: #aaa;
            }
        """)
        self.chat_btn.clicked.connect(self.toggle_extensions)
        self.header_layout.addWidget(self.chat_btn)

        # Close Button (Small X)
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                 background-color: transparent;
                 color: white;
                 font-size: 18px;
            }
            QPushButton:hover {
                 background-color: rgba(255,0,0,0.5);
                 border-radius: 15px;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        self.header_layout.addWidget(self.close_btn)

        self.container_layout.addWidget(self.header)

        # Web View
        self.webview = QWebEngineView()
        self.webview.setStyleSheet("background: white; border-radius: 10px;")
        # Allow microphone permission automatically
        self.webview.page().featurePermissionRequested.connect(self.on_feature_permission)
        
        self.container_layout.addWidget(self.webview)

    def load_url(self):
        self.webview.setUrl(QUrl(self.url))

    def on_feature_permission(self, url, feature):
        # Auto-grant audio/video permissions
        if feature in (
            self.webview.page().Feature.MediaAudioCapture,
            self.webview.page().Feature.MediaVideoCapture,
            self.webview.page().Feature.MediaAudioVideoCapture
        ):
            self.webview.page().setFeaturePermission(
                url, feature, self.webview.page().PermissionPolicy.PermissionGrantedByUser
            )

    def toggle_voice_mode(self):
        # Attempt to click the microphone or voice icon on the page via JS
        # This is a heuristic. For ChatGPT, the voice mode is often a headphone icon.
        # This script logs for now, as selecting the exact element is site-specific and brittle.
        # Ideally, we inject a script to find aria-labels like "Start voice conversation"
        js_code = """
        (function() {
            // Heuristic for ChatGPT and others
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                 const label = btn.getAttribute('aria-label') || btn.innerText;
                 if (label && (label.toLowerCase().includes('voice') || label.toLowerCase().includes('listen') || label.toLowerCase().includes('speak'))) {
                     console.log("Clicking potential voice button:", label);
                     btn.click();
                     return;
                 }
            }
            alert("Could not auto-detect voice button. Please click it manually.");
        })();
        """
        self.webview.page().runJavaScript(js_code)
        
        # Visual feedback
        if self.voice_btn.text() == "▸":
            self.voice_btn.setText("⏸")
            self.voice_btn.setStyleSheet("background-color: #007acc; color: white; border-radius: 10px; font-size: 20px; font-weight: bold;")
        else:
             self.voice_btn.setText("▸")
             self.voice_btn.setStyleSheet("background-color: #888; color: black; border-radius: 10px; font-size: 20px; font-weight: bold;")


    def toggle_extensions(self):
        # Maybe resize window or similar?
        pass

    # Drag window support
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
             self.move(event.globalPosition().toPoint() - self.drag_pos)
             event.accept()
