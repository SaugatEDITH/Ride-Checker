import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Import UI Windows
from ui.login_window import LoginWindow


class RideHailingApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # ---------------------------
        # Global Application Styling
        # ---------------------------
        self.setApplicationName("Ride Hailing App")
        self.setApplicationVersion("1.0")
        self.setWindowIcon(QIcon("assets/icons/app_logo.svg"))

        # Dark modern theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QPushButton {
                background-color: #2d89ef;
                color: white;
                border-radius: 8px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #1b65c7;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
            QLineEdit, QComboBox, QDateTimeEdit {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                padding: 6px;
                border-radius: 6px;
            }
            QTableWidget {
                background-color: #2a2a2a;
                gridline-color: #444444;
            }
            QHeaderView::section {
                background-color: #333333;
                padding: 6px;
                border: none;
            }
        """)

        # ---------------------------
        # Launch Login Screen
        # ---------------------------
        self.window = LoginWindow()
        self.window.show()


def main():
    app = RideHailingApp(sys.argv)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
