import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from models.user import User


class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ride Hailing App - Signup")
        self.setMaximumSize(420, 520)
        self.showFullScreen()

        self.setup_ui()

    # ---------------------------------------------------
    # UI Setup
    # ---------------------------------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # ---------------------
        # Logo / Icon
        # ---------------------
        logo = QLabel()
        logo_path = "assets/icons/signup.svg"
        if os.path.exists(logo_path):
            logo.setPixmap(QPixmap(logo_path).scaled(80, 80, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo)

        # ---------------------
        # Title
        # ---------------------
        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # ---------------------------------------------------
        # Email Field
        # ---------------------------------------------------
        email_box = QHBoxLayout()
        email_icon = QLabel()
        email_icon.setPixmap(QPixmap("assets/icons/email.svg").scaled(22, 22))

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        email_box.addWidget(email_icon)
        email_box.addWidget(self.email_input)
        main_layout.addLayout(email_box)

        # ---------------------------------------------------
        # Username Field
        # ---------------------------------------------------
        username_box = QHBoxLayout()
        username_icon = QLabel()
        username_icon.setPixmap(QPixmap("assets/icons/user.svg").scaled(22, 22))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        username_box.addWidget(username_icon)
        username_box.addWidget(self.username_input)
        main_layout.addLayout(username_box)

        # ---------------------------------------------------
        # Password Field
        # ---------------------------------------------------
        pass_box = QHBoxLayout()
        pass_icon = QLabel()
        pass_icon.setPixmap(QPixmap("assets/icons/lock.svg").scaled(22, 22))

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        pass_box.addWidget(pass_icon)
        pass_box.addWidget(self.password_input)
        main_layout.addLayout(pass_box)

        # ---------------------------------------------------
        # Role Selection
        # ---------------------------------------------------
        role_box = QHBoxLayout()
        role_icon = QLabel()
        role_icon.setPixmap(QPixmap("assets/icons/role.svg").scaled(22, 22))

        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["customer", "driver"])

        role_box.addWidget(role_icon)
        role_box.addWidget(self.role_dropdown)
        main_layout.addLayout(role_box)

        # ---------------------------------------------------
        # Signup Button
        # ---------------------------------------------------
        signup_btn = QPushButton("Create Account")
        signup_btn.setIcon(QIcon("assets/icons/signup.svg"))
        signup_btn.clicked.connect(self.signup_user)
        main_layout.addWidget(signup_btn)

        # ---------------------------------------------------
        # Back to Login
        # ---------------------------------------------------
        back_btn = QPushButton("Back to Login")
        back_btn.setIcon(QIcon("assets/icons/back.svg"))
        back_btn.clicked.connect(self.back_to_login)
        main_layout.addWidget(back_btn)

        self.setLayout(main_layout)

    # ---------------------------------------------------
    # SIGNUP HANDLER
    # ---------------------------------------------------
    def signup_user(self):
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_dropdown.currentText()

        if not email or not username or not password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        ok, msg = User.signup(email, username, password, role)

        if not ok:
            QMessageBox.warning(self, "Error", msg)
            return

        QMessageBox.information(self, "Success", msg)
        self.back_to_login()

    # ---------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------
    def back_to_login(self):
        from ui.login_window import LoginWindow  
        self.login_win = LoginWindow()
        self.login_win.show()
        self.close()
