from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QUrl, QSize, QTimer
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os
from ui.blur_effect import apply_acrylic_blur, GRADIENT_DEEP_BLUE

class AiVoiceWidget(QWidget):
    _shared_profile = None

    def __init__(self, url="https://chatgpt.com/"):
        super().__init__()
        self.url = url
        self.setWindowTitle("Anywhere AI")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.expanded_height = 500
        self.collapsed_height = 80 # Header height approx
        self.is_expanded = False

        self.resize(320, self.collapsed_height) # Start collapsed
        self.init_ui()
        self.load_url()

        # Position at bottom-center
        self.position_on_screen()
        
        # Initialize drag position
        self.drag_pos = None

    def showEvent(self, event):
        super().showEvent(event)
        try:
            apply_acrylic_blur(int(self.winId()), gradient_color=GRADIENT_DEEP_BLUE)
        except Exception:
            pass

    def position_on_screen(self):
         screen = self.screen().availableGeometry()
         # Center horizontally
         x = screen.x() + (screen.width() - self.width()) // 2
         # Bottom vertically with margin
         margin = 20
         y = screen.y() + screen.height() - self.height() - margin
         self.move(x, y)

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
                background-color: rgba(12, 14, 26, 0.28);
                border: none;
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
        self.header_layout.setContentsMargins(5, 5, 5, 5)

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
        self.chat_btn = QPushButton("Chat ▼")
        self.chat_btn.setFixedSize(80, 40)
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
        self.chat_btn.clicked.connect(self.toggle_expanded)
        self.header_layout.addWidget(self.chat_btn)

        # Close Button (was Expand/Collapse)
        self.close_btn = QPushButton("✕") 
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                 background-color: transparent;
                 color: white;
                 font-size: 16px;
            }
            QPushButton:hover {
                 background-color: rgba(255, 59, 48, 0.8); /* Red hover */
                 border-radius: 15px;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        self.header_layout.addWidget(self.close_btn)

        self.container_layout.addWidget(self.header)

        # Web View
        self.webview = QWebEngineView()
        
        # Configure Persistent Profile
        # Store data in "web_data" folder next to main script or in user data dir
        if AiVoiceWidget._shared_profile is None:
            storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web_data")
            if not os.path.exists(storage_path):
                os.makedirs(storage_path)

            profile = QWebEngineProfile("hotkey_ai_profile")
            profile.setPersistentStoragePath(storage_path)
            profile.setCachePath(storage_path)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
            AiVoiceWidget._shared_profile = profile

        page = QWebEnginePage(AiVoiceWidget._shared_profile, self.webview)
        self.webview.setPage(page)

        self.webview.setStyleSheet("background: white; border-radius: 10px;")
        # Allow microphone permission automatically
        page.featurePermissionRequested.connect(self.on_feature_permission)
        
        self.container_layout.addWidget(self.webview)
        self.webview.hide() # Initially hidden
        
        self.webview.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, ok):
        if ok:
            print("Page loaded. Scheduling auto-voice start...")
            # Wait 5 seconds for SPA rendering/hydration
            QTimer.singleShot(5000, lambda: self.toggle_voice_mode(auto=True))

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

    def toggle_expanded(self):
        screen = self.screen().availableGeometry()
        
        current_h = self.height()
        current_y = self.y()
        current_bottom = current_y + current_h
         
        if self.is_expanded:
            # COLLAPSING from 500 -> 80
            # Check if we are touching bottom edge (within threshold)
            # If so, we want to anchor to the bottom (header moves down)
            is_bottom_anchored = (current_bottom >= screen.bottom() - 10)
            
            self.webview.hide()
            self.resize(self.width(), self.collapsed_height)
            self.chat_btn.setText("Chat ▼")
            self.is_expanded = False

            if is_bottom_anchored:
                 # Move down to keep bottom fixed
                 # New Height is collapsed_height
                 new_y = current_bottom - self.collapsed_height
                 self.move(self.x(), new_y)
            # Else: Top stays fixed (default behavior of resize)
            
        else:
            # EXPANDING from 80 -> 500
            # Calculate needed shift to fit screen
            target_bottom = current_y + self.expanded_height
            overflow = target_bottom - screen.bottom()
            
            self.resize(self.width(), self.expanded_height)
            self.webview.show()
            self.chat_btn.setText("Chat ▲")
            self.is_expanded = True
            
            if overflow > 0:
                 # Shift up just enough to fit
                 new_y = current_y - overflow
                 # Clamp to top
                 if new_y < screen.top():
                     new_y = screen.top()
                 self.move(self.x(), new_y)
            # Else: Top stays fixed (default)


    def toggle_voice_mode(self, auto=False):
        # Attempt to click the microphone or voice icon on the page via JS
        # This is a heuristic. For ChatGPT, the voice mode is often a headphone icon.
        # ideally, we inject a script to find aria-labels like "Start voice conversation"
        js_code = """
        (function() {
            if (auto_trigger) {
                const texts = Array.from(document.querySelectorAll('a, button')).map(e => (e.innerText || "").toLowerCase().trim());
                if (texts.includes("log in") || texts.includes("sign up") || texts.includes("login")) {
                    console.log("Auto-start aborted: User not logged in.");
                    return "NOT_LOGGED_IN";
                }
                const url = window.location.href.toLowerCase();
                if (url.includes("login") || url.includes("auth")) {
                    console.log("Auto-start aborted: Auth page.");
                    return "NOT_LOGGED_IN";
                }
            }

            console.log("Attempting to find Voice Mode button...");
            
            // Strategy 1: Known data-testids
            const testIds = ['voice-mode-button', 'voice-input-button'];
            for (let id of testIds) {
                const btn = document.querySelector(`[data-testid="${id}"]`);
                if (btn) {
                    console.log(`Found by data-testid: ${id}`);
                    btn.click();
                    return "SUCCESS";
                }
            }

            // Strategy 2: Button with aria-label "Use Voice" or similar
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                 const label = (btn.getAttribute('aria-label') || btn.innerText || "").toLowerCase();
                 if (label.includes('use voice') || label.includes('start voice') || label.includes('listen')) {
                     console.log("Found by label:", label);
                     btn.click();
                     return "SUCCESS";
                 }
            }
            
            if (!auto_trigger) {
               console.log("Voice button not found. Dumping buttons for debug:");
               buttons.forEach(b => console.log(b.getAttribute('aria-label'), b.className));
            } else {
               console.log("Auto-start voice: Button not found.");
            }
            return "NOT_FOUND";
        })();
        """
        # Inject 'true' or 'false' for auto_trigger
        js_code = js_code.replace("auto_trigger", "true" if auto else "false")
        
        def handle_js_result(result):
            if result == "NOT_LOGGED_IN":
                return
            
            # Visual feedback
            if self.voice_btn.text() == "▸":
                self.voice_btn.setText("⏸")
                self.voice_btn.setStyleSheet("background-color: #007acc; color: white; border-radius: 10px; font-size: 20px; font-weight: bold;")
            else:
                 self.voice_btn.setText("▸")
                 self.voice_btn.setStyleSheet("background-color: #888; color: black; border-radius: 10px; font-size: 20px; font-weight: bold;")

        self.webview.page().runJavaScript(js_code, handle_js_result)




    # Drag window support
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
             self.move(event.globalPosition().toPoint() - self.drag_pos)
             event.accept()
