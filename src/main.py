import sys
from PyQt5.QtWidgets import QApplication
from src.gui import MainWindow

def main():
    """Main entry point for the CodeDex Pro application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 