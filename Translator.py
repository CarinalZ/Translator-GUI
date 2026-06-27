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
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy,
    QStackedWidget, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
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
        self.setFixedSize(460, 450)
        self.setMinimumSize(460, 450)
        
        self.is_active = False
        self.hotkey_thread = None

        self.current_theme = "dark"
        self.source_lang = "ru"
        self.target_lang = "en"
        self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)

        self.languages = {
            "ru": "Russian", "en": "English", "uk": "Ukrainian",
            "de": "German", "fr": "French", "es": "Spanish",
            "it": "Italian", "pl": "Polish", "ja": "Japanese",
            "zh-CN": "Chinese (Simplified)", "ko": "Korean"
        }

        self.script_dir = Path(resource_path(""))
        self.notification = None
        self.current_animation = None

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked = QStackedWidget()
        self.main_layout.addWidget(self.stacked)

        self.create_main_page()
        self.create_settings_page()

        self.stacked.addWidget(self.main_page)
        self.stacked.addWidget(self.settings_page)
        self.stacked.setCurrentWidget(self.main_page)

        self.stacked.currentChanged.connect(self.on_page_changed)

    def on_page_changed(self, index):
        if self.stacked.currentWidget() == self.settings_page:
            self.setFixedSize(460, 540)
        else:
            self.setFixedSize(460, 450)

    def create_main_page(self):
        self.main_page = QWidget()
        layout = QVBoxLayout(self.main_page)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 35)

        header = QHBoxLayout()
        title = QLabel("Translator")
        title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(44, 44)
        self.settings_btn.setFont(QFont("Segoe UI", 20))
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton { background-color: #2d2d2d; color: white; border: none; border-radius: 12px; }
            QPushButton:hover { background-color: #3d3d3d; }
        """)
        self.settings_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.settings_page))
        header.addWidget(self.settings_btn)

        layout.addLayout(header)

        self.toggle_button = QPushButton("Включить")
        self.toggle_button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.toggle_button.setMinimumHeight(75)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.clicked.connect(self.toggle_translation)
        layout.addWidget(self.toggle_button)

        self.status_label = QLabel("Статус: отключено")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #333333;")
        layout.addWidget(line)

        layout.addItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        social = QHBoxLayout()
        social.setAlignment(Qt.AlignmentFlag.AlignRight)
        social.setSpacing(12)

        social_buttons = [
            ("github", "https://github.com/CarinalZ", "github.png"),
            ("telegram", "https://t.me/carinalproject", "telegram.png")
        ]

        for name, url, filename in social_buttons:
            btn = QPushButton()
            btn.setFixedSize(42, 42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            icon_path = Path(resource_path(filename))
            found = False

            if icon_path.exists():
                btn.setIcon(QIcon(str(icon_path)))
                found = True
            else:
                alt_path = Path(__file__).parent / filename
                if alt_path.exists():
                    btn.setIcon(QIcon(str(alt_path)))
                    found = True

            if found:
                btn.setIconSize(btn.size())
            else:
                btn.setText("🐙" if name == "github" else "📱")
                btn.setFont(QFont("Segoe UI", 18))

            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #2d2d2d;
                }
            """)
            btn.clicked.connect(lambda checked, u=url: webbrowser.open(u))
            social.addWidget(btn)

        layout.addLayout(social)

    def create_settings_page(self):
        self.settings_page = QWidget()
        layout = QVBoxLayout(self.settings_page)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 25)

        header = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(44, 44)
        self.back_btn.setFont(QFont("Segoe UI", 20))
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet("""
            QPushButton { background-color: #2d2d2d; color: white; border: none; border-radius: 12px; }
            QPushButton:hover { background-color: #3d3d3d; }
        """)
        self.back_btn.clicked.connect(lambda: self.stacked.setCurrentWidget(self.main_page))
        header.addWidget(self.back_btn)
        header.addStretch()

        title = QLabel("Настройки")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        theme_group = QGroupBox("Тема приложения")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.setContentsMargins(15, 15, 15, 15)
        self.theme_btn = QPushButton("Переключить на светлую тему")
        self.theme_btn.setMinimumHeight(55)
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_btn)
        layout.addWidget(theme_group)

        lang_group = QGroupBox("Языки перевода")
        lang_layout = QVBoxLayout(lang_group)
        lang_layout.setSpacing(12)
        lang_layout.setContentsMargins(15, 15, 15, 15)

        def get_lang_items():
            return [f"{code} - {name}" for code, name in self.languages.items()]

        src_h = QHBoxLayout()
        src_h.addWidget(QLabel("С:"))
        self.src_combo = QComboBox()
        self.src_combo.addItems(get_lang_items())
        self.src_combo.setCurrentText(f"{self.source_lang} - {self.languages[self.source_lang]}")
        self.src_combo.currentTextChanged.connect(self.update_translator)
        src_h.addWidget(self.src_combo, 1)
        lang_layout.addLayout(src_h)

        tgt_h = QHBoxLayout()
        tgt_h.addWidget(QLabel("На:"))
        self.tgt_combo = QComboBox()
        self.tgt_combo.addItems(get_lang_items())
        self.tgt_combo.setCurrentText(f"{self.target_lang} - {self.languages[self.target_lang]}")
        self.tgt_combo.currentTextChanged.connect(self.update_translator)
        tgt_h.addWidget(self.tgt_combo, 1)
        lang_layout.addLayout(tgt_h)

        self.swap_btn = QPushButton("🔄 Поменять языки местами")
        self.swap_btn.setMinimumHeight(50)
        self.swap_btn.clicked.connect(self.swap_languages)
        lang_layout.addWidget(self.swap_btn)

        layout.addWidget(lang_group)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 32px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        bottom_layout.addWidget(self.save_btn)
        layout.addLayout(bottom_layout)

    def save_settings(self):
        self.show_saved_notification()

    def show_saved_notification(self):
        if self.notification and self.notification.isVisible():
            return

        if self.notification:
            self.notification.deleteLater()

        self.notification = QLabel("Сохранено ✓", self)
        self.notification.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.notification.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notification.setStyleSheet("""
            QLabel {
                background-color: #4caf50;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
            }
        """)
        self.notification.adjustSize()

        x = self.width() - self.notification.width() - 20
        y = 20
        self.notification.move(x, y)
        self.notification.show()

        self.current_animation = QPropertyAnimation(self.notification, b"windowOpacity")
        self.current_animation.setDuration(1600)
        self.current_animation.setStartValue(1.0)
        self.current_animation.setEndValue(0.0)
        self.current_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.current_animation.start()

        QTimer.singleShot(1900, self.clear_notification)

    def clear_notification(self):
        if self.notification:
            self.notification.deleteLater()
            self.notification = None

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.setStyleSheet("""
                QMainWindow, QWidget, QGroupBox { background-color: #f4f4f4; color: #1e1e1e; }
                QPushButton { background-color: #ffffff; border: 1px solid #bbbbbb; color: #1e1e1e; }
            """)
            self.theme_btn.setText("Переключить на тёмную тему")
        else:
            self.current_theme = "dark"
            self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
            self.theme_btn.setText("Переключить на светлую тему")

    def update_translator(self):
        src_text = self.src_combo.currentText().split(" - ")[0]
        tgt_text = self.tgt_combo.currentText().split(" - ")[0]
        self.source_lang = src_text
        self.target_lang = tgt_text
        self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)

    def swap_languages(self):
        src = self.src_combo.currentText()
        tgt = self.tgt_combo.currentText()
        self.src_combo.setCurrentText(tgt)
        self.tgt_combo.setCurrentText(src)
        self.update_translator()

    def toggle_translation(self):
        if not self.is_active:
            self.is_active = True
            self.toggle_button.setText("Выключить")
            self.toggle_button.setStyleSheet("""
                QPushButton { background-color: #d32f2f; color: white; border: none; border-radius: 10px; }
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
            print(f"✓ Переведено ({len(text)} симв.) | {self.source_lang} → {self.target_lang}")
        except Exception as e:
            print(f"Ошибка перевода: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec())