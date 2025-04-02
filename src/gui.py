import sys
import cv2
import time
import threading
import os
import random
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QCheckBox, QComboBox, QGroupBox, QMessageBox,
                             QTextEdit, QSplitter, QDialog, QFormLayout, 
                             QSpinBox, QTabWidget, QListWidget, QInputDialog,
                             QDoubleSpinBox, QStatusBar, QFrame, QToolButton,
                             QDialogButtonBox, QGridLayout, QListWidgetItem,
                             QFileDialog)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QSize

from src.scanner import QRScanner
from src.config import Config

# Pokemon Color Theme
POKEMON_COLORS = {
    # Primary colors
    'primary': '#FF3B30',         # Modern Pokémon red
    'secondary': '#007AFF',       # Vibrant blue
    'accent': '#FFCC00',          # Pokémon yellow
    
    # UI colors
    'background': '#121214',      # Dark background
    'card_bg': '#18181B',         # Slightly lighter card background
    'surface': '#232329',         # Surface elements
    'input_bg': '#27272C',        # Input field background
    
    # Border colors
    'border': '#323238',          # Border color
    'border_light': '#3C3C44',    # Lighter border for highlights
    'border_focus': '#4A4A55',    # Focus border color
    
    # Text colors
    'text': '#FFFFFF',            # Primary text
    'text_secondary': '#B0B0B8',  # Secondary text
    'text_disabled': '#6E6E76',   # Disabled text
    
    # Functional colors
    'success': '#34C759',         # Success green
    'warning': '#FF9500',         # Warning orange
    'error': '#FF453A',           # Error red
    
    # Button states
    'hover': '#2C2C35',           # Hover state color
    'active': '#343441',          # Active state color
    
    # Neutral colors
    'gray': '#8E8E93',
    'light_gray': '#F2F2F7',
    'black': '#000000',
}

class StatusIndicator(QWidget):
    """Custom widget for showing connection/login status."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = False
        self.label_text = "Not Connected"
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Create indicator container for better styling and alignment
        indicator_container = QFrame()
        indicator_container.setFixedSize(12, 12)
        indicator_container.setStyleSheet(f"""
            background-color: transparent;
            border-radius: 6px;
            margin: 0;
            padding: 0;
        """)
        indicator_layout = QVBoxLayout(indicator_container)
        indicator_layout.setContentsMargins(0, 0, 0, 0)
        indicator_layout.setAlignment(Qt.AlignCenter)
        
        # Create indicator light
        self.indicator = QFrame()
        self.indicator.setFixedSize(6, 6)
        self.indicator.setStyleSheet(f"""
            background-color: {POKEMON_COLORS['error']};
            border-radius: 3px;
            margin: 0;
        """)
        indicator_layout.addWidget(self.indicator, 0, Qt.AlignCenter)
        
        # Create label
        self.label = QLabel(self.label_text)
        self.label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.label.setStyleSheet(f"""
            font-weight: 500;
            color: {POKEMON_COLORS['text_secondary']};
            font-size: 12px;
            padding: 0;
            margin: 0;
        """)
        
        layout.addWidget(indicator_container)
        layout.addWidget(self.label)
        
        self.setLayout(layout)
        
    def set_status(self, status, text=None):
        """Update the status indicator."""
        self.status = status
        
        if status:
            self.indicator.setStyleSheet(f"""
                background-color: {POKEMON_COLORS['success']};
                border-radius: 3px;
                margin: 0;
            """)
            self.label.setStyleSheet(f"""
                font-weight: 500;
                color: {POKEMON_COLORS['success']};
                font-size: 12px;
                padding: 0;
                margin: 0;
            """)
        else:
            self.indicator.setStyleSheet(f"""
                background-color: {POKEMON_COLORS['error']};
                border-radius: 3px;
                margin: 0;
            """)
            self.label.setStyleSheet(f"""
                font-weight: 500;
                color: {POKEMON_COLORS['text_secondary']};
                font-size: 12px;
                padding: 0;
                margin: 0;
            """)
            
        if text:
            self.label.setText(text)
        else:
            self.label.setText("Connected" if status else "Not Connected")

class LoginDialog(QDialog):
    """Dialog for entering Pokemon Trainer Club credentials."""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config or Config()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Pokemon Trainer Club Login")
        self.setMinimumWidth(400)
        
        # Set Pokemon-themed style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {POKEMON_COLORS['background']};
            }}
            QLabel {{
                font-weight: bold;
                color: {POKEMON_COLORS['text']};
                padding: 4px;
            }}
            QPushButton {{
                background-color: {POKEMON_COLORS['primary']};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                margin: 4px;
            }}
            QPushButton:hover {{
                background-color: #FF3333;
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {POKEMON_COLORS['gray']};
                border-radius: 4px;
                color: {POKEMON_COLORS['black']};
                background-color: {POKEMON_COLORS['light_gray']};
                margin: 4px;
                font-size: 14px;
            }}
            QCheckBox {{
                color: {POKEMON_COLORS['text']};
                padding: 4px;
                margin: 8px 0;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)  # Increase spacing between elements
        layout.setContentsMargins(20, 20, 20, 20)  # Add margin around the entire form
        
        # Add Pokemon logo
        logo_label = QLabel()
        # Load logo if available
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "pokemon_logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # Add title
        title_label = QLabel("Trainer Club Login")
        title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {POKEMON_COLORS['accent']}; margin: 15px 0; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Create a form widget with spacing
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)  # Increase spacing between form rows
        form_layout.setContentsMargins(10, 10, 10, 10)  # Add padding inside the form
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align labels to the right
        
        # Username field
        username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setText(self.config.username)
        self.username_edit.setPlaceholderText("Enter your Trainer Club username")
        self.username_edit.setMinimumHeight(30)  # Increase height for better touch targets
        form_layout.addRow(username_label, self.username_edit)
        
        # Password field
        password_label = QLabel("Password:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setText(self.config.password)
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setMinimumHeight(30)  # Increase height for better touch targets
        form_layout.addRow(password_label, self.password_edit)
        
        # Save credentials checkbox with better positioning
        checkbox_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 5, 0, 5)
        
        # Add spacer to align checkbox with input fields
        checkbox_layout.addSpacing(10)
        
        self.save_checkbox = QCheckBox("Save credentials")
        self.save_checkbox.setChecked(True)
        checkbox_layout.addWidget(self.save_checkbox)
        checkbox_layout.addStretch()
        
        form_layout.addRow("", checkbox_container)
        
        layout.addWidget(form_widget)
        
        # Buttons with better spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # Increase spacing between buttons
        button_layout.setContentsMargins(0, 10, 0, 0)  # Add top margin for buttons
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.accept)
        self.login_button.setMinimumHeight(36)  # Taller buttons
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(f"""
            background-color: #9E9E9E;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
        """)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setMinimumHeight(36)  # Taller buttons
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_credentials(self):
        """Get the entered credentials."""
        return {
            'username': self.username_edit.text(),
            'password': self.password_edit.text(),
            'save': self.save_checkbox.isChecked()
        }

class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config or Config()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("CodeDex Pro Settings")
        self.setMinimumWidth(350)
        
        layout = QFormLayout()
        
        # Set Pokemon-themed style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {POKEMON_COLORS['background']};
            }}
            QLabel {{
                font-weight: bold;
                color: {POKEMON_COLORS['text']};
                padding: 4px;
            }}
            QPushButton {{
                background-color: {POKEMON_COLORS['primary']};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                margin: 4px;
            }}
            QPushButton:hover {{
                background-color: #FF3333;
            }}
            QSpinBox, QDoubleSpinBox {{
                padding: 6px;
                border: 1px solid {POKEMON_COLORS['gray']};
                border-radius: 4px;
                background-color: {POKEMON_COLORS['light_gray']};
                color: {POKEMON_COLORS['black']};
                margin: 4px;
            }}
            QCheckBox {{
                color: {POKEMON_COLORS['text']};
                padding: 4px;
            }}
            QTabWidget::pane {{
                border: 1px solid {POKEMON_COLORS['gray']};
                background-color: {POKEMON_COLORS['card_bg']};
            }}
            QTabBar::tab {{
                background-color: {POKEMON_COLORS['background']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['gray']};
                padding: 8px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {POKEMON_COLORS['card_bg']};
                border-bottom-color: {POKEMON_COLORS['card_bg']};
            }}
            QComboBox {{
                background-color: {POKEMON_COLORS['input_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['border']};
                border-radius: 8px;
                padding: 10px 16px;
                min-width: 180px;
                margin-right: 14px;
                font-size: 13px;
                font-weight: 500;
                selection-background-color: {POKEMON_COLORS['surface']};
                selection-color: {POKEMON_COLORS['text']};
            }}
            QComboBox:hover {{
                border-color: {POKEMON_COLORS['accent']};
                background-color: {POKEMON_COLORS['surface']};
            }}
            QComboBox:on {{
                border-color: {POKEMON_COLORS['accent']};
                background-color: {POKEMON_COLORS['surface']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 28px;
                background-color: transparent;
            }}
            QComboBox QAbstractItemView {{
                background-color: {POKEMON_COLORS['card_bg']};
                color: {POKEMON_COLORS['text']};
                border: 2px solid {POKEMON_COLORS['accent']};
                border-radius: 8px;
                selection-background-color: {POKEMON_COLORS['secondary']};
                selection-color: white;
                padding: 6px;
                outline: 0px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px 12px;
                min-height: 24px;
                border-radius: 6px;
                margin: 2px 4px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {POKEMON_COLORS['secondary']};
            }}
            QComboBox QAbstractItemView::item:hover:!selected {{
                background-color: {POKEMON_COLORS['hover']};
            }}
        """)
        
        # Create tab widget for organizing settings
        tab_widget = QTabWidget()
        
        # Camera settings tab
        camera_tab = QWidget()
        camera_layout = QFormLayout()
        
        # Camera selection
        self.camera_spinbox = QSpinBox()
        self.camera_spinbox.setMinimum(0)
        self.camera_spinbox.setMaximum(10)
        self.camera_spinbox.setValue(self.config.camera_index)
        camera_layout.addRow("Camera index:", self.camera_spinbox)
        
        camera_tab.setLayout(camera_layout)
        tab_widget.addTab(camera_tab, "Camera")
        
        # Detection settings tab
        detection_tab = QWidget()
        detection_layout = QFormLayout()
        
        # Auto-detect QR codes
        self.auto_detect_checkbox = QCheckBox()
        self.auto_detect_checkbox.setChecked(self.config.auto_detect)
        detection_layout.addRow("Auto-detect QR codes:", self.auto_detect_checkbox)
        
        # Scan interval
        self.scan_interval_spinbox = QSpinBox()
        self.scan_interval_spinbox.setMinimum(100)
        self.scan_interval_spinbox.setMaximum(2000)
        self.scan_interval_spinbox.setSingleStep(50)
        self.scan_interval_spinbox.setValue(self.config.scan_interval)
        self.scan_interval_spinbox.setSuffix(" ms")
        detection_layout.addRow("Scan interval:", self.scan_interval_spinbox)
        
        # Scan cooldown
        self.scan_cooldown_spinbox = QDoubleSpinBox()
        self.scan_cooldown_spinbox.setMinimum(0.5)
        self.scan_cooldown_spinbox.setMaximum(10.0)
        self.scan_cooldown_spinbox.setSingleStep(0.5)
        self.scan_cooldown_spinbox.setValue(self.config.scan_cooldown)
        self.scan_cooldown_spinbox.setSuffix(" sec")
        detection_layout.addRow("Scan cooldown:", self.scan_cooldown_spinbox)
        
        detection_tab.setLayout(detection_layout)
        tab_widget.addTab(detection_tab, "Detection")
        
        # Advanced settings tab
        advanced_tab = QWidget()
        advanced_layout = QFormLayout()
        
        # Debug mode
        self.debug_checkbox = QCheckBox()
        self.debug_checkbox.setChecked(self.config.debug_mode)
        advanced_layout.addRow("Debug mode:", self.debug_checkbox)
        
        advanced_tab.setLayout(advanced_layout)
        tab_widget.addTab(advanced_tab, "Advanced")
        
        layout.addRow(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow("", button_layout)
        
        self.setLayout(layout)
        
    def get_settings(self):
        """Get the configured settings."""
        return {
            'camera_index': self.camera_spinbox.value(),
            'debug_mode': self.debug_checkbox.isChecked(),
            'auto_detect': self.auto_detect_checkbox.isChecked(),
            'scan_interval': self.scan_interval_spinbox.value(),
            'scan_cooldown': self.scan_cooldown_spinbox.value()
        }

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("CodeDex Pro - Pokémon TCG Code Scanner")
        self.setMinimumSize(1000, 650)
        
        # Initialize configuration and scanner
        self.config = Config()
        self.scanner = QRScanner()
        
        # Initialize variables
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.update_frame)
        
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.auto_scan_qr_code)
        
        # Add cooldown to prevent duplicate scans of the same code
        self.last_scan_time = 0
        self.scan_cooldown = self.config.scan_cooldown  # Use value from config
        
        # List to track recently seen codes to prevent duplicates
        self.recently_scanned_codes = []
        self.max_recent_codes = 5
        
        self.codes_found = []
        
        # Define constants
        self.all_codes_option = "All Codes (Complete Export)"
        
        # Setup directory for camera_placeholder
        app_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(app_dir), "assets")
        self.camera_placeholder_path = os.path.join(assets_dir, "camera_off.png")
        
        # Configure main window
        self.setup_window()
        
        # Setup status bar with better styling
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {POKEMON_COLORS['card_bg']};
                color: {POKEMON_COLORS['text_secondary']};
                padding: 8px 20px;
                font-size: 13px;
                border-top: 1px solid {POKEMON_COLORS['border']};
            }}
        """)
        self.statusBar().showMessage("Ready to scan Pokémon TCG codes")
        
        # Update the UI state initially
        self.update_ui()
        
    def setup_window(self):
        """Setup the main window layout and components."""
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Add header with app title and settings
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 16)
        header_layout.setSpacing(12)
        
        # App title
        app_title = QLabel("CodeDex Pro")
        app_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 700;
            color: {POKEMON_COLORS['primary']};
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(app_title)
        
        header_layout.addStretch()
        
        app_description = QLabel("Professional TCG Code Scanner")
        app_description.setStyleSheet(f"""
            font-size: 14px;
            color: {POKEMON_COLORS['text_secondary']};
            font-weight: 500;
        """)
        header_layout.addWidget(app_description)
        
        header_layout.addStretch()
        
        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {POKEMON_COLORS['primary']};
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 12px;
                min-height: 14px;
            }}
            QPushButton:hover {{
                background-color: #FF4F45;
            }}
            QPushButton:pressed {{
                background-color: #E6352B;
            }}
        """)
        self.settings_button.clicked.connect(self.show_settings_dialog)
        header_layout.addWidget(self.settings_button)
        
        main_layout.addLayout(header_layout)
        
        # Create main content layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left side - Camera and scanner controls
        scanner_card = QFrame()
        scanner_card.setObjectName("scanner_card")
        scanner_card.setStyleSheet(f"""
            #scanner_card {{
                background-color: {POKEMON_COLORS['card_bg']};
                border-radius: 12px;
                border: 1px solid {POKEMON_COLORS['border']};
            }}
        """)
        scanner_layout = QVBoxLayout(scanner_card)
        scanner_layout.setContentsMargins(16, 16, 16, 16)
        scanner_layout.setSpacing(12)
        
        # Section title
        scanner_header = QHBoxLayout()
        scanner_header.setContentsMargins(0, 0, 0, 8)
        scanner_header.setSpacing(10)
        
        scanner_title = QLabel("Scanner")
        scanner_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {POKEMON_COLORS['accent']};
            letter-spacing: 0.5px;
        """)
        scanner_header.addWidget(scanner_title)
        scanner_header.addStretch(1)
        
        # Add camera status indicator with zero right margin
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(0)
        
        self.camera_status = StatusIndicator()
        self.camera_status.set_status(False, "Camera Off")
        status_layout.addWidget(self.camera_status)
        
        scanner_header.addWidget(status_container, 0, Qt.AlignRight)
        
        scanner_layout.addLayout(scanner_header)
        
        # Camera view container
        camera_container = QFrame()
        camera_container.setStyleSheet(f"""
            background-color: {POKEMON_COLORS['background']};
            border-radius: 10px;
            border: 1px solid {POKEMON_COLORS['border']};
            padding: 0;
        """)
        camera_layout = QVBoxLayout(camera_container)
        camera_layout.setContentsMargins(0, 0, 0, 0)
        
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(480, 360)
        self.camera_label.setStyleSheet(f"""
            background-color: {POKEMON_COLORS['background']};
            border-radius: 9px;
            padding: 0;
            margin: 0;
        """)
        camera_layout.addWidget(self.camera_label)
        
        # If no placeholder image, create a blank dark background
        self.camera_label.setText("")
        
        # Create camera off center indicator
        self.camera_off_indicator = QLabel("Camera Off")
        self.camera_off_indicator.setAlignment(Qt.AlignCenter)
        self.camera_off_indicator.setFixedSize(150, 40)
        self.camera_off_indicator.setStyleSheet(f"""
            color: {POKEMON_COLORS['text_secondary']};
            font-size: 14px;
            font-weight: 600;
            background-color: rgba(18, 18, 20, 0.8);
            border-radius: 6px;
            padding: 8px 16px;
            border: 1px solid {POKEMON_COLORS['border']};
        """)
        self.camera_off_indicator.setParent(self.camera_label)
        
        # Position in center initially
        self.center_camera_off_indicator()
        self.camera_off_indicator.show()
            
        # Update indicator position when camera view is resized
        self.camera_label.resizeEvent = lambda event: self.on_camera_resize(event)
        
        scanner_layout.addWidget(camera_container)
        
        # Scanner controls in a row
        scanner_controls = QHBoxLayout()
        scanner_controls.setContentsMargins(0, 8, 0, 0)
        scanner_controls.setSpacing(8)
        
        # Start Camera button (primary action)
        self.start_button = QPushButton("Start Camera")
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {POKEMON_COLORS['secondary']};
                color: white;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 600;
                min-width: 100px;
                min-height: 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #0A84FF;
            }}
            QPushButton:pressed {{
                background-color: #0070EB;
            }}
            QPushButton:disabled {{
                background-color: {POKEMON_COLORS['surface']};
                color: {POKEMON_COLORS['text_disabled']};
            }}
        """)
        self.start_button.clicked.connect(self.toggle_camera)
        scanner_controls.addWidget(self.start_button)
        
        # Scan QR Code button (secondary action with more subtle styling)
        self.scan_button = QPushButton("Scan QR Code")
        self.scan_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {POKEMON_COLORS['card_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['border']};
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 600;
                min-width: 100px;
                min-height: 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {POKEMON_COLORS['surface']};
                border-color: {POKEMON_COLORS['border_light']};
            }}
            QPushButton:pressed {{
                background-color: {POKEMON_COLORS['surface']};
                border-color: {POKEMON_COLORS['border_focus']};
            }}
            QPushButton:disabled {{
                background-color: {POKEMON_COLORS['card_bg']};
                color: {POKEMON_COLORS['text_disabled']};
                border-color: {POKEMON_COLORS['border']};
            }}
        """)
        self.scan_button.clicked.connect(self.scan_qr_code)
        self.scan_button.setEnabled(False)
        scanner_controls.addWidget(self.scan_button)
        
        scanner_layout.addLayout(scanner_controls)
        content_layout.addWidget(scanner_card, 1)
        
        # Right side - Codes list and controls
        codes_card = QFrame()
        codes_card.setObjectName("codes_card")
        codes_card.setStyleSheet(f"""
            #codes_card {{
                background-color: {POKEMON_COLORS['card_bg']};
                border-radius: 12px;
                border: 1px solid {POKEMON_COLORS['border']};
            }}
        """)
        codes_layout = QVBoxLayout(codes_card)
        codes_layout.setContentsMargins(16, 16, 16, 16)
        codes_layout.setSpacing(12)
        
        # Section title
        codes_header = QHBoxLayout()
        codes_header.setContentsMargins(0, 0, 0, 8)
        codes_header.setSpacing(10)
        
        codes_title = QLabel("Pokémon Codes")
        codes_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {POKEMON_COLORS['accent']};
            letter-spacing: 0.5px;
        """)
        codes_header.addWidget(codes_title)
        codes_header.addStretch()
        
        codes_layout.addLayout(codes_header)
        
        # Create tab widget for different code views
        self.code_tabs = QTabWidget()
        self.code_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
                top: 0px;
            }}
            QTabBar {{
                background-color: transparent;
                alignment: center;
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {POKEMON_COLORS['text_secondary']};
                padding: 10px 16px;
                margin-right: 4px;
                font-weight: 600;
                font-size: 14px;
                min-height: 20px;
                min-width: 110px;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {POKEMON_COLORS['accent']};
                border-bottom: 2px solid {POKEMON_COLORS['accent']};
            }}
            QTabBar::tab:!selected:hover {{
                color: {POKEMON_COLORS['text']};
                border-bottom: 2px solid {POKEMON_COLORS['border_light']};
            }}
        """)
        
        # Tab 1: All codes list
        self.all_codes_widget = QWidget()
        all_codes_layout = QVBoxLayout(self.all_codes_widget)
        all_codes_layout.setContentsMargins(0, 16, 0, 0)
        all_codes_layout.setSpacing(16)
        
        # Codes list with improved styling
        self.codes_list = QListWidget()
        self.codes_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.codes_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {POKEMON_COLORS['input_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid rgba(50, 50, 56, 0.4);
                border-radius: 8px;
                padding: 4px;
                font-family: 'SF Mono', 'Menlo', 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.4;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid rgba(50, 50, 56, 0.4);
                margin: 0;
                border-radius: 0;
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 122, 255, 0.15);
                color: {POKEMON_COLORS['text']};
                border-left: 2px solid {POKEMON_COLORS['secondary']};
            }}
        """)
        all_codes_layout.addWidget(self.codes_list)
        
        # Buttons row
        all_codes_buttons = QHBoxLayout()
        all_codes_buttons.setSpacing(6)
        all_codes_buttons.setContentsMargins(0, 8, 0, 0)
        
        # Button styling helper function
        def style_button(button, bg_color, hover_color, pressed_color, text_color="#FFFFFF", is_primary=False):
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg_color};
                    color: {text_color};
                    border-radius: 4px;
                    padding: {6 if not is_primary else 8}px {8 if not is_primary else 12}px;
                    font-weight: 600;
                    min-width: {60 if not is_primary else 80}px;
                    min-height: 14px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """)
        
        # Create left side buttons
        left_buttons = QHBoxLayout()
        left_buttons.setSpacing(6)
        
        self.add_manual_button = QPushButton("Add Code")
        style_button(self.add_manual_button, POKEMON_COLORS['primary'], "#FF4F45", "#E6352B", is_primary=True)
        self.add_manual_button.clicked.connect(self.add_code_manually)
        left_buttons.addWidget(self.add_manual_button)
        
        # Add left buttons to main button row
        all_codes_buttons.addLayout(left_buttons)
        
        # Add spacer to push the next button group to the right
        all_codes_buttons.addStretch(1)
        
        # Create right side buttons with tight spacing
        right_buttons = QHBoxLayout()
        right_buttons.setSpacing(6)
        
        self.clear_button = QPushButton("Clear All")
        style_button(self.clear_button, POKEMON_COLORS['surface'], POKEMON_COLORS['hover'], POKEMON_COLORS['active'], POKEMON_COLORS['text'])
        self.clear_button.clicked.connect(self.clear_codes)
        right_buttons.addWidget(self.clear_button)
        
        self.copy_all_button = QPushButton("Copy All")
        style_button(self.copy_all_button, POKEMON_COLORS['surface'], POKEMON_COLORS['hover'], POKEMON_COLORS['active'], POKEMON_COLORS['text'])
        self.copy_all_button.clicked.connect(self.copy_all_codes)
        right_buttons.addWidget(self.copy_all_button)
        
        # Create export buttons with minimal spacing
        self.export_txt_button = QPushButton("Export TXT")
        style_button(self.export_txt_button, POKEMON_COLORS['secondary'], "#0A84FF", "#0070EB", POKEMON_COLORS['text'])
        self.export_txt_button.clicked.connect(self.export_to_txt)
        right_buttons.addWidget(self.export_txt_button)
        
        self.export_md_button = QPushButton("Export MD")
        style_button(self.export_md_button, POKEMON_COLORS['secondary'], "#0A84FF", "#0070EB", POKEMON_COLORS['text'])
        self.export_md_button.clicked.connect(self.export_to_md)
        right_buttons.addWidget(self.export_md_button)
        
        # Add right buttons to main button row
        all_codes_buttons.addLayout(right_buttons)
        
        all_codes_layout.addLayout(all_codes_buttons)
        self.code_tabs.addTab(self.all_codes_widget, "All Codes")
        
        # Tab 2: Code blocks
        self.blocks_widget = QWidget()
        blocks_layout = QVBoxLayout(self.blocks_widget)
        blocks_layout.setContentsMargins(0, 16, 0, 0)
        blocks_layout.setSpacing(16)
        
        # Controls row - optimize for initial viewport
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(20)  # Wider spacing between components
        controls_layout.setContentsMargins(0, 0, 0, 14)
        
        # Create a standardized layout for each combo box
        # First combo - block selector
        block_combo_container = QVBoxLayout()
        block_combo_container.setSpacing(6)
        block_combo_container.setContentsMargins(0, 0, 0, 0)
        
        block_label = QLabel("Select Block:")
        block_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {POKEMON_COLORS['text_secondary']};
        """)
        block_combo_container.addWidget(block_label)
        
        # Initialize block selector with proper sizing
        self.block_selector = QComboBox()
        self.block_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {POKEMON_COLORS['input_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                selection-background-color: {POKEMON_COLORS['surface']};
                selection-color: {POKEMON_COLORS['text']};
            }}
            QComboBox:hover {{
                border-color: {POKEMON_COLORS['accent']};
                background-color: {POKEMON_COLORS['surface']};
            }}
            QComboBox:on {{
                border-color: {POKEMON_COLORS['accent']};
                background-color: {POKEMON_COLORS['surface']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                background-color: transparent;
            }}
            QComboBox QAbstractItemView {{
                background-color: {POKEMON_COLORS['card_bg']};
                color: {POKEMON_COLORS['text']};
                border: 2px solid {POKEMON_COLORS['accent']};
                border-radius: 6px;
                selection-background-color: {POKEMON_COLORS['secondary']};
                selection-color: white;
                padding: 6px;
                outline: 0px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 10px;
                min-height: 22px;
                border-radius: 4px;
                margin: 2px 4px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {POKEMON_COLORS['secondary']};
            }}
            QComboBox QAbstractItemView::item:hover:!selected {{
                background-color: {POKEMON_COLORS['hover']};
            }}
        """)
        self.block_selector.currentIndexChanged.connect(self.format_selector_changed)
        self.block_selector.setFixedHeight(34)  # Fixed height for consistent sizing
        block_combo_container.addWidget(self.block_selector)
        
        # Second combo - format selector
        format_combo_container = QVBoxLayout()
        format_combo_container.setSpacing(6)
        format_combo_container.setContentsMargins(0, 0, 0, 0)
        
        format_label = QLabel("Format:")
        format_label.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {POKEMON_COLORS['text_secondary']};
        """)
        format_combo_container.addWidget(format_label)
        
        # Initialize format selector with matching sizing
        self.format_selector = QComboBox()
        self.format_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {POKEMON_COLORS['input_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 500;
                selection-background-color: {POKEMON_COLORS['surface']};
                selection-color: {POKEMON_COLORS['text']};
            }}
            QComboBox:hover {{
                border-color: {POKEMON_COLORS['accent']};
                background-color: {POKEMON_COLORS['surface']};
            }}
            QComboBox:on {{
                border-color: {POKEMON_COLORS['accent']};
                background-color: {POKEMON_COLORS['surface']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                background-color: transparent;
            }}
            QComboBox QAbstractItemView {{
                background-color: {POKEMON_COLORS['card_bg']};
                color: {POKEMON_COLORS['text']};
                border: 2px solid {POKEMON_COLORS['accent']};
                border-radius: 6px;
                selection-background-color: {POKEMON_COLORS['secondary']};
                selection-color: white;
                padding: 6px;
                outline: 0px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 10px;
                min-height: 22px;
                border-radius: 4px;
                margin: 2px 4px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {POKEMON_COLORS['secondary']};
            }}
            QComboBox QAbstractItemView::item:hover:!selected {{
                background-color: {POKEMON_COLORS['hover']};
            }}
        """)
        self.format_selector.addItems([
            "Numbered List",
            "Raw Codes (One per line)",
            "Space-Separated",
            "Comma-Separated"
        ])
        self.format_selector.currentIndexChanged.connect(self.format_selector_changed)
        self.format_selector.setFixedHeight(34)  # Fixed height for consistent sizing
        format_combo_container.addWidget(self.format_selector)
        
        # Add each combo layout to the main control layout with equal sizing
        controls_layout.addLayout(block_combo_container, 1)
        controls_layout.addLayout(format_combo_container, 1)
        
        blocks_layout.addLayout(controls_layout)
        
        # Block display with improved styling
        self.block_display = QTextEdit()
        self.block_display.setReadOnly(True)
        self.block_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {POKEMON_COLORS['input_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Menlo', 'SF Mono', 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }}
        """)
        blocks_layout.addWidget(self.block_display)
        
        # Copy and export buttons
        copy_layout = QHBoxLayout()
        copy_layout.setContentsMargins(0, 8, 0, 0)
        copy_layout.setSpacing(6)
        copy_layout.addStretch(1)
        
        # Group buttons for better organization
        button_group = QHBoxLayout()
        button_group.setSpacing(6)
        
        self.copy_block_button = QPushButton("Copy Block")
        style_button(self.copy_block_button, POKEMON_COLORS['surface'], POKEMON_COLORS['hover'], POKEMON_COLORS['active'], POKEMON_COLORS['text'])
        self.copy_block_button.clicked.connect(self.copy_current_block)
        button_group.addWidget(self.copy_block_button)
        
        # Add export buttons
        self.export_block_txt_button = QPushButton("Export TXT")
        style_button(self.export_block_txt_button, POKEMON_COLORS['secondary'], "#0A84FF", "#0070EB", POKEMON_COLORS['text'])
        self.export_block_txt_button.clicked.connect(self.export_to_txt)
        button_group.addWidget(self.export_block_txt_button)
        
        self.export_block_md_button = QPushButton("Export MD")
        style_button(self.export_block_md_button, POKEMON_COLORS['secondary'], "#0A84FF", "#0070EB", POKEMON_COLORS['text'])
        self.export_block_md_button.clicked.connect(self.export_to_md)
        button_group.addWidget(self.export_block_md_button)
        
        copy_layout.addLayout(button_group)
        
        blocks_layout.addLayout(copy_layout)
        
        # Initialize the tab with correct count (0 if no codes yet)
        self.code_tabs.addTab(self.blocks_widget, "Code Blocks (0)")
        
        # Add the code_tabs to the codes_layout
        codes_layout.addWidget(self.code_tabs)
        
        # Add to main layout
        content_layout.addWidget(codes_card, 1)
        
        main_layout.addLayout(content_layout)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
        
    def toggle_camera(self):
        """Start or stop the camera."""
        if self.capture_timer.isActive():
            self.capture_timer.stop()
            self.scan_timer.stop()  # Also stop the auto-scan timer
            self.scanner.stop_camera()
            
            # Update UI with camera stopped state
            self.start_button.setText("Start Camera")
            self.start_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {POKEMON_COLORS['secondary']};
                    color: white;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: 600;
                    min-width: 100px;
                    min-height: 14px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: #0A84FF;
                }}
                QPushButton:pressed {{
                    background-color: #0070EB;
                }}
                QPushButton:disabled {{
                    background-color: {POKEMON_COLORS['surface']};
                    color: {POKEMON_COLORS['text_disabled']};
                }}
            """)
            
            self.scan_button.setEnabled(False)
            self.camera_status.set_status(False, "Camera Off")
            
            # Show the camera off indicator in the center
            if hasattr(self, 'camera_off_indicator'):
                self.camera_off_indicator.setParent(self.camera_label)
                self.center_camera_off_indicator()
                self.camera_off_indicator.show()
            
            # No need to set placeholder image if we're using the indicator overlay
            self.statusBar().showMessage("Camera stopped")
        else:
            try:
                # Hide the camera off indicator
                if hasattr(self, 'camera_off_indicator'):
                    self.camera_off_indicator.hide()
                
                if self.scanner.start_camera(self.config.camera_index):
                    self.capture_timer.start(30)  # 30ms refresh rate (approximately 33 FPS)
                    
                    # Only start auto-scan if enabled in settings
                    if self.config.auto_detect:
                        self.scan_timer.start(self.config.scan_interval)
                    
                    # Update UI with camera active state    
                    self.start_button.setText("Stop Camera")
                    self.start_button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {POKEMON_COLORS['error']};
                            color: white;
                            border-radius: 4px;
                            padding: 8px 12px;
                            font-weight: 600;
                            min-width: 100px;
                            min-height: 14px;
                            font-size: 12px;
                        }}
                        QPushButton:hover {{
                            background-color: #FF5F54;
                        }}
                        QPushButton:pressed {{
                            background-color: #E63C34;
                        }}
                    """)
                    
                    self.scan_button.setEnabled(True)
                    self.camera_status.set_status(True, "Camera Active")
                    self.statusBar().showMessage("Camera active - scanning for QR codes")
            except Exception as e:
                QMessageBox.critical(self, "Camera Error", f"Failed to start camera: {str(e)}")
    
    def update_frame(self):
        """Update the camera frame."""
        frame = self.scanner.get_frame()
        if frame is not None:
            # Convert to RGB for Qt
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to QImage and then QPixmap
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Scale to fit while maintaining aspect ratio
            pixmap = pixmap.scaled(self.camera_label.width(), self.camera_label.height(), 
                                  Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Display the image
            self.camera_label.setPixmap(pixmap)
    
    def auto_scan_qr_code(self):
        """Automatically scan for QR codes in the current frame."""
        # Check cooldown to prevent rapid duplicate scans
        current_time = time.time()
        if current_time - self.last_scan_time < self.scan_cooldown:
            return
            
        frame = self.scanner.get_frame()
        if frame is not None:
            qr_codes = self.scanner.scan_qr_code(frame)
            
            if qr_codes:
                code = qr_codes[0]['data']
                
                # Check if we've recently seen this code
                if code in self.recently_scanned_codes:
                    return
                
                # Update last scan time and recently scanned codes list
                self.last_scan_time = current_time
                self.recently_scanned_codes.append(code)
                
                # Keep the list to a maximum size
                if len(self.recently_scanned_codes) > self.max_recent_codes:
                    self.recently_scanned_codes.pop(0)
                
                self.statusBar().showMessage(f"QR code detected: {code}")
                self.add_code(code)
    
    def scan_qr_code(self):
        """Manually scan for QR codes in the current frame."""
        frame = self.scanner.get_frame()
        if frame is not None:
            qr_codes = self.scanner.scan_qr_code(frame)
            
            if qr_codes:
                code = qr_codes[0]['data']
                self.statusBar().showMessage(f"QR code detected: {code}")
                self.add_code(code)
            else:
                self.statusBar().showMessage("No QR code detected in current frame")
    
    def add_code_manually(self):
        """Add a code manually via dialog box."""
        code, ok = QInputDialog.getText(self, "Add Code Manually", "Enter Pokémon TCG code:")
        if ok and code:
            self.add_code(code)
            self.statusBar().showMessage(f"Code added manually: {code}")
    
    def add_code(self, code):
        """Add a code to the list."""
        if code and code not in self.codes_found:
            self.codes_found.append(code)
            self.codes_list.addItem(code)
            self.statusBar().showMessage(f"Found {len(self.codes_found)} codes")
            
            # Enable buttons if we have codes
            self.update_ui()
            
            # Update the blocks tab
            self.update_blocks()
    
    def clear_codes(self):
        """Clear the list of found codes."""
        self.codes_found = []
        self.codes_list.clear()
        self.statusBar().showMessage("All codes cleared")
        self.update_blocks()
        self.update_ui()
        
    def update_blocks(self):
        """Update the code blocks."""
        # Clear the current block selector
        self.block_selector.clear()
        
        if not self.codes_found:
            self.block_display.setText("No codes found")
            self.copy_block_button.setEnabled(False)
            self.code_tabs.setTabText(1, "Code Blocks (0)")
            return
            
        # Add "All Codes" option first
        self.block_selector.addItem(self.all_codes_option)
            
        # Split codes into blocks of 10
        num_blocks = (len(self.codes_found) + 9) // 10
        
        for i in range(num_blocks):
            start_idx = i * 10 + 1
            end_idx = min((i + 1) * 10, len(self.codes_found))
            self.block_selector.addItem(f"Block {i+1} (Codes {start_idx}-{end_idx})")
        
        # Display the first block
        self.update_block_display(0)
        self.copy_block_button.setEnabled(True)
        
        # Update the tab title with count
        self.code_tabs.setTabText(1, f"Code Blocks ({len(self.codes_found)})")
    
    def update_block_display(self, index=0):
        """Update the displayed block of codes."""
        if index < 0 or not self.codes_found:
            self.block_display.setText("No codes in this block")
            return
            
        # Initialize start_idx to 0 as default
        start_idx = 0
            
        # Check if the "All Codes" option is selected
        if index == 0 and self.block_selector.currentText() == self.all_codes_option:
            block_codes = self.codes_found
            # start_idx is already 0 for All Codes
        else:
            # Calculate the actual block index (offset by 1 if All Codes option exists)
            actual_index = index - 1 if self.block_selector.itemText(0) == self.all_codes_option else index
            start_idx = actual_index * 10
            end_idx = min(start_idx + 10, len(self.codes_found))
            block_codes = self.codes_found[start_idx:end_idx]
        
        if not block_codes:
            self.block_display.setText("No codes in this block")
            return
            
        # Get the selected format
        format_type = self.format_selector.currentText()
        
        # Format the codes based on selected format
        if format_type == "Numbered List":
            text = "--- Pokémon TCG Codes (copy this block) ---\n\n"
            for i, code in enumerate(block_codes):
                text += f"{start_idx + i + 1}. {code}\n"
                
        elif format_type == "Raw Codes (One per line)":
            text = "\n".join(block_codes)
            
        elif format_type == "Space-Separated":
            text = " ".join(block_codes)
            
        elif format_type == "Comma-Separated":
            text = ",".join(block_codes)
            
        self.block_display.setText(text)
    
    def copy_all_codes(self):
        """Copy all codes to clipboard."""
        if not self.codes_found:
            QMessageBox.information(self, "No Codes", "No codes available to copy.")
            return
            
        # Format all codes for clipboard
        text = "\n".join(self.codes_found)
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        self.statusBar().showMessage(f"Copied {len(self.codes_found)} codes to clipboard")
    
    def copy_current_block(self):
        """Copy the current block of codes to clipboard."""
        current_index = self.block_selector.currentIndex()
        if current_index < 0 or not self.codes_found:
            QMessageBox.information(self, "No Codes", "No codes available to copy.")
            return
            
        # Check if the "All Codes" option is selected
        if current_index == 0 and self.block_selector.currentText() == self.all_codes_option:
            block_codes = self.codes_found
            current_block_name = "All Codes"
        else:
            # Calculate the actual block index (offset by 1 if All Codes option exists)
            actual_index = current_index - 1 if self.block_selector.itemText(0) == self.all_codes_option else current_index
            start_idx = actual_index * 10
            end_idx = min(start_idx + 10, len(self.codes_found))
            block_codes = self.codes_found[start_idx:end_idx]
            current_block_name = f"Block {actual_index+1}"
        
        if not block_codes:
            QMessageBox.information(self, "No Codes", "No codes in this block.")
            return
            
        # Format the codes based on selected format
        format_type = self.format_selector.currentText()
        
        if format_type == "Numbered List":
            text = ""
            for i, code in enumerate(block_codes):
                if current_block_name == "All Codes":
                    text += f"{i + 1}. {code}\n"
                else:
                    start_idx = actual_index * 10
                    text += f"{start_idx + i + 1}. {code}\n"
        elif format_type == "Raw Codes (One per line)":
            text = "\n".join(block_codes)
        elif format_type == "Space-Separated":
            text = " ".join(block_codes)
        else:  # Comma-Separated
            text = ",".join(block_codes)
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        self.statusBar().showMessage(f"Copied {len(block_codes)} codes to clipboard")
        
        QMessageBox.information(self, "Block Copied", 
                              f"{current_block_name} ({len(block_codes)} codes) copied to clipboard in {format_type} format")
    
    def show_settings_dialog(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self, self.config)
        
        if dialog.exec_():
            settings = dialog.get_settings()
            
            # Update settings
            for key, value in settings.items():
                self.config.update_setting(key, value)
            
            # Update local instance variables based on new settings
            self.scan_cooldown = self.config.scan_cooldown
            
            # Update timers if active
            if self.scan_timer.isActive():
                self.scan_timer.stop()
                if self.config.auto_detect:
                    self.scan_timer.start(self.config.scan_interval)
            
            # Restart camera if necessary
            if self.capture_timer.isActive():
                self.toggle_camera()  # Stop
                self.toggle_camera()  # Start
                
            self.statusBar().showMessage("Settings updated")
            self.update_ui()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop the camera and clean up
        self.scanner.stop_camera()
        event.accept()

    def update_ui(self):
        """Update the UI with current state information."""
        # Update the found codes count in UI
        self.statusBar().showMessage(f"Found {len(self.codes_found)} codes")
        
        # Clear existing items
        self.codes_list.clear()
        self.block_selector.clear()
        
        if not self.codes_found:
            # Show helpful empty state message in code list
            empty_item = QListWidgetItem("No codes scanned yet. Start camera and scan QR codes to see them here.")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            self.codes_list.addItem(empty_item)
            
            # Style the empty state
            self.codes_list.setStyleSheet(f"""
                QListWidget {{
                    background-color: {POKEMON_COLORS['input_bg']};
                    color: {POKEMON_COLORS['text']};
                    border: 1px solid {POKEMON_COLORS['border']};
                    border-radius: 8px;
                    padding: 4px;
                    font-family: 'Menlo', 'SF Mono', 'Consolas', 'Courier New', monospace;
                    font-size: 13px;
                }}
                QListWidget::item {{
                    padding: 16px 12px;
                    border-bottom: 1px solid {POKEMON_COLORS['border']};
                    margin: 0;
                    border-radius: 0;
                    color: {POKEMON_COLORS['text_secondary']};
                    font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                    font-style: italic;
                }}
            """)
            
            # Set empty state text for block display
            self.block_display.setText("No codes to display. Scan QR codes to see them formatted here.")
            self.block_display.setAlignment(Qt.AlignCenter)
            self.block_display.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {POKEMON_COLORS['input_bg']};
                    color: {POKEMON_COLORS['text_secondary']};
                    border: 1px solid {POKEMON_COLORS['border']};
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-family: 'SF Pro Display', 'Segoe UI', 'Arial', sans-serif;
                    font-size: 13px;
                    font-style: italic;
                }}
            """)
            
            # Update the tab title with count
            self.code_tabs.setTabText(1, "Code Blocks (0)")
            
            # Disable copy buttons when no codes
            self.copy_block_button.setEnabled(False)
            self.copy_all_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            
            # Disable export buttons
            self.export_txt_button.setEnabled(False)
            self.export_md_button.setEnabled(False)
            self.export_block_txt_button.setEnabled(False)
            self.export_block_md_button.setEnabled(False)
            return
        
        # Reset styling for non-empty state
        self.codes_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {POKEMON_COLORS['input_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['border']};
                border-radius: 8px;
                padding: 4px;
                font-family: 'Menlo', 'SF Mono', 'Consolas', 'Courier New', monospace;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid {POKEMON_COLORS['border']};
                margin: 0;
                border-radius: 0;
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 122, 255, 0.15);
                color: {POKEMON_COLORS['text']};
                border-left: 2px solid {POKEMON_COLORS['secondary']};
            }}
        """)
        
        self.block_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {POKEMON_COLORS['input_bg']};
                color: {POKEMON_COLORS['text']};
                border: 1px solid {POKEMON_COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Menlo', 'SF Mono', 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                line-height: 1.5;
            }}
        """)
        
        # Enable copy buttons when codes exist
        self.copy_block_button.setEnabled(True)
        self.copy_all_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        
        # Enable export buttons
        self.export_txt_button.setEnabled(True)
        self.export_md_button.setEnabled(True)
        self.export_block_txt_button.setEnabled(True)
        self.export_block_md_button.setEnabled(True)
                
        # Add all codes to the list
        for code in self.codes_found:
            item = QListWidgetItem(code)
            self.codes_list.addItem(item)
            
        # Add all blocks to the selector
        self.block_selector.addItem(self.all_codes_option)
        
        # Add appropriate blocks based on code count
        total_codes = len(self.codes_found)
        if total_codes > 10:
            # Add blocks of 10, 50, 100
            if total_codes > 10:
                self.block_selector.addItem("Last 10 Codes")
            if total_codes > 50:
                self.block_selector.addItem("Last 50 Codes")
            if total_codes > 100:
                self.block_selector.addItem("Last 100 Codes")
        
        # Update the tab title with count
        self.code_tabs.setTabText(1, f"Code Blocks ({total_codes})")
        
        # Update the block display
        self.update_block_display()

    def center_camera_off_indicator(self):
        """Center the camera off indicator in the camera view."""
        if hasattr(self, 'camera_off_indicator'):
            # Calculate the new position based on current camera label dimensions
            new_width = self.camera_label.width()
            new_height = self.camera_label.height()
            
            # Position in center
            self.camera_off_indicator.move(
                new_width // 2 - self.camera_off_indicator.width() // 2,
                new_height // 2 - self.camera_off_indicator.height() // 2
            )

    def on_camera_resize(self, event):
        """Update the camera off indicator position when the camera view is resized."""
        self.center_camera_off_indicator() 

    def format_selector_changed(self):
        """Handle format selection changes and update the block display."""
        current_index = self.block_selector.currentIndex()
        self.update_block_display(current_index) 

    def export_to_file(self, file_format):
        """Export all codes to a file in the specified format."""
        if not self.codes_found:
            QMessageBox.information(self, "No Codes", "No codes available to export.")
            return
            
        # Default filename with format
        default_name = f"pokemon_tcg_codes.{file_format}"
            
        # Open file dialog to get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Codes", 
            default_name, 
            f"{file_format.upper()} Files (*.{file_format})"
        )
        
        if not file_path:
            return  # User canceled
            
        try:
            with open(file_path, 'w') as f:
                if file_format == 'md':
                    # Export as markdown
                    f.write("# Pokémon TCG Codes\n\n")
                    f.write(f"*Exported from CodeDex Pro - {len(self.codes_found)} codes*\n\n")
                    
                    # Get current format from the selector
                    format_type = self.format_selector.currentText()
                    
                    if format_type == "Numbered List":
                        f.write("## Numbered List\n\n")
                        for i, code in enumerate(self.codes_found):
                            f.write(f"{i + 1}. `{code}`\n")
                    elif format_type == "Raw Codes (One per line)":
                        f.write("## Raw Codes\n\n")
                        f.write("```\n")
                        for code in self.codes_found:
                            f.write(f"{code}\n")
                        f.write("```\n")
                    elif format_type == "Space-Separated":
                        f.write("## Space-Separated\n\n")
                        f.write("```\n")
                        f.write(" ".join(self.codes_found))
                        f.write("\n```\n")
                    else:  # Comma-Separated
                        f.write("## Comma-Separated\n\n")
                        f.write("```\n")
                        f.write(",".join(self.codes_found))
                        f.write("\n```\n")
                else:
                    # Export as plain text
                    for code in self.codes_found:
                        f.write(f"{code}\n")
                        
            self.statusBar().showMessage(f"Exported {len(self.codes_found)} codes to {file_path}")
            QMessageBox.information(self, "Export Successful", f"Successfully exported {len(self.codes_found)} codes to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export codes: {str(e)}")
    
    def export_to_txt(self):
        """Export all codes to a TXT file."""
        self.export_to_file('txt')
        
    def export_to_md(self):
        """Export all codes to a Markdown file."""
        self.export_to_file('md') 