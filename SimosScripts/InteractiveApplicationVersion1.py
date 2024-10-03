import sys
import hashlib
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QStackedWidget, QHBoxLayout, QMessageBox, QLineEdit, QListWidget
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation

# Parameters for the design and functionality
window_title = "User Management"
login_button_label = "Login"
register_button_label = "Register"
exit_button_label = "Exit"

# Image path for startup logo
logo_path = r"D:\.CORE\LocalRepo\self-supported-assembly\self-supported-assembly\SimosScripts\InteractiveScript\images\0.png"
# Database file path for storing user data
database_file = r"D:\.CORE\LocalRepo\self-supported-assembly\self-supported-assembly\SimosScripts\InteractiveScript\users.txt"

# Aspect Ratio 16:9
window_width = 960
window_height = 540

# Colors and fonts
yes_button_color = "#007AFF"
no_button_color = "#D3D3D3"
hover_pale_red = "#FFA07A"
hover_yes_button_color = "#005EC9"
text_color = "#000000"
font_family = "Helvetica"
startup_background_color = "#000000"

# Ensure user database file exists
if not os.path.exists(database_file):
    with open(database_file, 'w') as file:
        file.write('')  # Create an empty file if it doesn't exist

# List of registered robots
registered_robots = []


class PulsingButton(QPushButton):
    """A QPushButton that pulses and changes color when hovered."""
    def __init__(self, label, color, hover_color=None):
        super().__init__(label)
        self.default_color = color
        self.hover_color = hover_color if hover_color else color
        self.setFixedSize(200, 50)
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)
        self.setFont(QFont(font_family, 12))

    def enterEvent(self, event):
        self.setStyleSheet(f"""
            background-color: {self.hover_color};
            color: white;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)

    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            background-color: {self.default_color};
            color: white;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, window_width, window_height)

        self.stacked_widget = QStackedWidget()

        # Create the different screens
        self.startup_screen = self.create_startup_screen()
        self.main_menu = self.create_main_menu()
        self.login_screen = self.create_login_screen()
        self.register_screen = self.create_register_screen()
        self.robot_registration_screen = self.create_robot_registration_screen()
        self.robot_list_screen = self.create_robot_list_screen()

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.startup_screen)
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.register_screen)
        self.stacked_widget.addWidget(self.robot_registration_screen)
        self.stacked_widget.addWidget(self.robot_list_screen)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def create_startup_screen(self):
        """Create the startup screen with logo and circular button that appears after fade-in."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {startup_background_color};")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        self.logo_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(300, 300)

        # Opacity effect for fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.logo_label.setGraphicsEffect(self.opacity_effect)

        # Fade-in animation
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(5000)  # 5 seconds
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.finished.connect(self.show_button)

        # Circular button under the logo
        self.start_button = PulsingButton("Proceed", "#E0E0E0", hover_color="#CCCCCC")
        self.start_button.setFixedSize(100, 40)
        self.start_button.clicked.connect(self.switch_to_main_menu)
        self.start_button.setVisible(False)

        # Small italic label under the button
        self.click_here_label = QLabel("Click to proceed")
        self.click_here_label.setFont(QFont(font_family, 10, QFont.StyleItalic))
        self.click_here_label.setStyleSheet("color: white;")
        self.click_here_label.setAlignment(Qt.AlignCenter)
        self.click_here_label.setVisible(False)

        layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        layout.addSpacing(5)
        layout.addWidget(self.click_here_label, alignment=Qt.AlignCenter)

        widget.setLayout(layout)
        self.fade_in_animation.start()

        return widget

    def show_button(self):
        """Make the button and 'Click to proceed' label visible after fade-in."""
        self.start_button.setVisible(True)
        self.click_here_label.setVisible(True)

    def switch_to_main_menu(self):
        """Switch to the main menu."""
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def create_main_menu(self):
        """Create the main menu with Login, Register, and Exit buttons."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Main Menu Title
        self.label = QLabel("Main Menu")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Button Layout
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)

        # Login Button
        self.login_button = PulsingButton("Login", yes_button_color, hover_color=hover_yes_button_color)
        self.login_button.clicked.connect(self.switch_to_login_screen)
        button_layout.addWidget(self.login_button)

        # Register Button
        self.register_button = PulsingButton("Register", yes_button_color, hover_color=hover_yes_button_color)
        self.register_button.clicked.connect(self.switch_to_register_screen)
        button_layout.addWidget(self.register_button)

        # Exit Button
        self.exit_button = PulsingButton("Exit", no_button_color, hover_color=hover_pale_red)
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

        return widget

    def switch_to_login_screen(self):
        """Switch to the login screen."""
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def switch_to_register_screen(self):
        """Switch to the register screen."""
        self.stacked_widget.setCurrentWidget(self.register_screen)

    def switch_to_robot_registration(self):
        """Switch to the robot registration screen."""
        self.stacked_widget.setCurrentWidget(self.robot_registration_screen)

    def switch_to_robot_list(self):
        """Switch to the robot list screen."""
        self.stacked_widget.setCurrentWidget(self.robot_list_screen)
        self.update_robot_list()

    def create_login_screen(self):
        """Create the login screen."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Login Fields
        self.label = QLabel("Login")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        layout.addWidget(self.label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedWidth(300)
        layout.addWidget(self.username_input, alignment=Qt.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFixedWidth(300)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        # Submit Button
        self.login_submit = PulsingButton("Login", yes_button_color, hover_color=hover_yes_button_color)
        self.login_submit.clicked.connect(self.login_user)
        layout.addWidget(self.login_submit, alignment=Qt.AlignCenter)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(layout)
        return widget

    def create_register_screen(self):
        """Create the register screen."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Register Fields
        self.label = QLabel("Register")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        layout.addWidget(self.label)

        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("Enter new username")
        self.new_username_input.setFixedWidth(300)
        layout.addWidget(self.new_username_input, alignment=Qt.AlignCenter)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Enter password")
        self.new_password_input.setFixedWidth(300)
        layout.addWidget(self.new_password_input, alignment=Qt.AlignCenter)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setFixedWidth(300)
        layout.addWidget(self.confirm_password_input, alignment=Qt.AlignCenter)

        # Submit Button
        self.register_submit = PulsingButton("Register", yes_button_color, hover_color=hover_yes_button_color)
        self.register_submit.clicked.connect(self.register_user)
        layout.addWidget(self.register_submit, alignment=Qt.AlignCenter)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(layout)
        return widget

    def create_robot_registration_screen(self):
        """Create the robot registration screen after login or registration."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Robot Registration Title
        self.label = QLabel("Register a Robot")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Robot Name Input
        self.robot_name_input = QLineEdit()
        self.robot_name_input.setPlaceholderText("Enter Robot Name")
        self.robot_name_input.setFixedWidth(300)
        layout.addWidget(self.robot_name_input, alignment=Qt.AlignCenter)

        # Submit Button
        self.robot_submit = PulsingButton("Submit", yes_button_color, hover_color=hover_yes_button_color)
        self.robot_submit.clicked.connect(self.register_robot)
        layout.addWidget(self.robot_submit, alignment=Qt.AlignCenter)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(layout)
        return widget

    def create_robot_list_screen(self):
        """Create a screen to display the list of registered robots."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Registered Robots Title
        self.label = QLabel("Registered Robots")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Robot List
        self.robot_list = QListWidget()
        layout.addWidget(self.robot_list)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(layout)
        return widget

    def update_robot_list(self):
        """Update the list of registered robots."""
        self.robot_list.clear()
        self.robot_list.addItems(registered_robots)

    def login_user(self):
        """Handle user login."""
        username = self.username_input.text()
        password = self.password_input.text()

        # Hash the password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if self.verify_user(username, hashed_password):
            QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
            self.switch_to_robot_registration()  # Switch to robot registration
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def register_user(self):
        """Handle user registration."""
        username = self.new_username_input.text()
        password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if self.user_exists(username):
            QMessageBox.warning(self, "Registration Failed", "Username already exists.")
        elif password != confirm_password:
            QMessageBox.warning(self, "Registration Failed", "Passwords do not match.")
        elif len(password) < 6:
            QMessageBox.warning(self, "Registration Failed", "Password must be at least 6 characters.")
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.save_user(username, hashed_password)
            QMessageBox.information(self, "Registration Successful", f"User {username} registered successfully!")
            self.switch_to_robot_registration()  # Switch to robot registration

    def user_exists(self, username):
        """Check if a user already exists in the database."""
        with open(database_file, 'r') as file:
            for line in file:
                saved_username, _ = line.strip().split(',')
                if saved_username == username:
                    return True
        return False

    def save_user(self, username, hashed_password):
        """Save a new user to the database."""
        with open(database_file, 'a') as file:
            file.write(f"{username},{hashed_password}\n")

    def verify_user(self, username, hashed_password):
        """Verify if the username and password match the database."""
        with open(database_file, 'r') as file:
            for line in file:
                saved_username, saved_hashed_password = line.strip().split(',')
                if saved_username == username and saved_hashed_password == hashed_password:
                    return True
        return False

    def register_robot(self):
        """Handle robot registration."""
        robot_name = self.robot_name_input.text()
        if robot_name:
            registered_robots.append(robot_name)
            QMessageBox.information(self, "Robot Registered", f"Robot '{robot_name}' registered successfully!")
            self.switch_to_robot_list()  # Switch to the robot list screen
        else:
            QMessageBox.warning(self, "Registration Failed", "Please enter a robot name.")


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()



