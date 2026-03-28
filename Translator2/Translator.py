import sys
import os
import keyboard
import pyperclip
import time
import threading
import webbrowser
from pathlib import Path
from deep_translator import GoogleTranslator

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy,
    QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon



def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class TranslatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translator")
        self.setFixedSize(460, 320)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        
        self.is_active = False
        self.translator = GoogleTranslator(source='ru', target='en')
        self.hotkey_thread = None

        
        self.script_dir = Path(resource_path(""))

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 35, 40, 30)

        
        title = QLabel("Translator")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        
        self.toggle_button = QPushButton("Включить")
        self.toggle_button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.toggle_button.setMinimumHeight(70)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.clicked.connect(self.toggle_translation)
        main_layout.addWidget(self.toggle_button)

        
        self.status_label = QLabel("Статус: отключено")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #333333;")
        main_layout.addWidget(line)

        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        
        social_layout = QHBoxLayout()
        social_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        social_layout.setSpacing(15)

        
        github_path = Path(resource_path("github.png"))
        self.github_btn = QPushButton()
        self.github_btn.setFixedSize(38, 38)
        if github_path.exists():
            self.github_btn.setIcon(QIcon(str(github_path)))
            self.github_btn.setIconSize(self.github_btn.size())
        else:
            self.github_btn.setText("GitHub")
        self.github_btn.setStyleSheet("border: none; background: transparent;")
        self.github_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.github_btn.clicked.connect(lambda: webbrowser.open("https://github.com/CarinalZ"))
        social_layout.addWidget(self.github_btn)

        
        tg_path = Path(resource_path("telegram.png"))
        self.tg_btn = QPushButton()
        self.tg_btn.setFixedSize(38, 38)
        if tg_path.exists():
            self.tg_btn.setIcon(QIcon(str(tg_path)))
            self.tg_btn.setIconSize(self.tg_btn.size())
        else:
            self.tg_btn.setText("TG")
        self.tg_btn.setStyleSheet("border: none; background: transparent;")
        self.tg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tg_btn.clicked.connect(lambda: webbrowser.open("https://t.me/carinalproject"))
        social_layout.addWidget(self.tg_btn)

        main_layout.addLayout(social_layout)

    def toggle_translation(self):
        if not self.is_active:
            self.is_active = True
            self.toggle_button.setText("Выключить")
            self.toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:hover { background-color: #b71c1c; }
            """)
            self.status_label.setText("Статус: активировано")
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")

            self.hotkey_thread = threading.Thread(target=self.start_hotkey_listener, daemon=True)
            self.hotkey_thread.start()
            print("✅ Перевод активирован (Ctrl + X)")

        else:
            self.is_active = False
            self.toggle_button.setText("Включить")
            self.toggle_button.setStyleSheet("")
            self.status_label.setText("Статус: отключено")
            self.status_label.setStyleSheet("color: #757575;")

            try:
                keyboard.remove_hotkey('ctrl+x')
            except:
                pass
            print("⛔ Перевод отключён")

    def start_hotkey_listener(self):
        try:
            keyboard.add_hotkey('ctrl+x', self.translate_clipboard, suppress=False)
            keyboard.wait()
        except Exception as e:
            print(f"Ошибка потока клавиатуры: {e}")

    def translate_clipboard(self):
        try:
            time.sleep(0.15)
            text = pyperclip.paste().strip()
            if not text:
                return

            translated = self.translator.translate(text)
            pyperclip.copy(translated)
            time.sleep(0.07)
            keyboard.press_and_release('ctrl+v')
            print(f"✓ Переведено ({len(text)} символов)")
        except Exception as e:
            print(f"Ошибка перевода: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())