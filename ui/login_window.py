import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QDesktopWidget
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from models.user import User
from ui.customer_window import CustomerWindow
from ui.driver_window import DriverWindow
from ui.admin_window import AdminWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ride Hailing App - Login")
        self.setMinimumSize(500, 700)
        self.center_and_resize_window()

        self.setup_ui()

    # ---------------------------------------------------
    # CENTER AND RESIZE WINDOW
    # ---------------------------------------------------
    def center_and_resize_window(self):
        """Center window and set to half screen size"""
        screen = QDesktopWidget().screenGeometry()
        width = screen.width() // 2
        height = screen.height() // 2
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    # ---------------------------------------------------
    # UI Layout
    # ---------------------------------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # -----------------------
        # Logo
        # -----------------------
        logo = QLabel()
        logo_path = "assets/icons/admin.svg"  # You can change to app_logo.svg
        if os.path.exists(logo_path):
            logo.setPixmap(QPixmap(logo_path).scaled(80, 80, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo)

        # -----------------------
        # Title
        # -----------------------
        title = QLabel("Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        main_layout.addWidget(title)

        # -----------------------
        # Email Input
        # -----------------------
        email_box = QHBoxLayout()
        email_icon = QLabel()
        email_icon.setPixmap(QPixmap("assets/icons/email.svg").scaled(22, 22, Qt.KeepAspectRatio))

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        email_box.addWidget(email_icon)
        email_box.addWidget(self.email_input)
        main_layout.addLayout(email_box)

        # -----------------------
        # Password Input
        # -----------------------
        pass_box = QHBoxLayout()
        pass_icon = QLabel()
        pass_icon.setPixmap(QPixmap("assets/icons/lock.svg").scaled(22, 22, Qt.KeepAspectRatio))

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)

        pass_box.addWidget(pass_icon)
        pass_box.addWidget(self.pass_input)
        main_layout.addLayout(pass_box)

        # -----------------------
        # Login Button
        # -----------------------
        login_btn = QPushButton("Login")
        login_btn.setIcon(QIcon("assets/icons/login.svg"))
        login_btn.clicked.connect(self.login_user)
        main_layout.addWidget(login_btn)

        # -----------------------
        # Signup Button
        # -----------------------
        signup_btn = QPushButton("Create Account")
        signup_btn.setIcon(QIcon("assets/icons/signup.svg"))
        signup_btn.clicked.connect(self.open_signup)
        main_layout.addWidget(signup_btn)

        # -----------------------
        # Footer
        # -----------------------
        footer = QLabel("© Ride Hailing App 2025")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    # ---------------------------------------------------
    # LOGIN HANDLER
    # ---------------------------------------------------
    def login_user(self):
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        # ------------------------------
        # ADMIN LOGIN (hard-coded)
        # ------------------------------
        if email == "admin@admin.com" and password == "admin":
            self.open_admin()
            return

        # ------------------------------
        # CUSTOMER / DRIVER LOGIN
        # ------------------------------
        user, msg = User.login(email, password)

        if user is None:
            QMessageBox.warning(self, "Error", msg)
            return

        if user.role == "customer":
            self.open_customer(user)
        else:
            self.open_driver(user)

    # ---------------------------------------------------
    # Window Navigations
    # ---------------------------------------------------
    def open_signup(self):
        from ui.signup_window import SignupWindow
        self.signup_window = SignupWindow()
        self.signup_window.show()
        self.close()

    def open_customer(self, user):
        self.customer_window = CustomerWindow(user)
        self.customer_window.show()
        self.close()

    def open_driver(self, user):
        self.driver_window = DriverWindow(user)
        self.driver_window.show()
        self.close()

    def open_admin(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()
        self.close()
