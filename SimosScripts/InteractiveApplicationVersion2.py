import sys
import hashlib
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGraphicsOpacityEffect,
    QHBoxLayout, QMessageBox, QLineEdit, QListWidget, QSizePolicy, QStackedWidget
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QTimer, QParallelAnimationGroup, QPoint, QEasingCurve, QSequentialAnimationGroup
)

# Parameters for the design and functionality
window_title = "CORE 2024"
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
hover_yes_button_color = "#99CCFF"
text_color = "#000000"
font_family = "Helvetica"
startup_background_color = "#FFFFFF"

# Titles for the startup screen
course_title = "C.O.R.E 2024"
project_title = "Robotic assembly of rigidity-preserving structures"

# Ensure user database file exists
if not os.path.exists(database_file):
    with open(database_file, 'w') as file:
        file.write('')  # Create an empty file if it doesn't exist

# List of registered robots
registered_robots = []


class PulsingButton(QPushButton):
    """A QPushButton that pulses and changes color when hovered."""
    def __init__(self, label, color, hover_color=None, is_negative=False):
        super().__init__(label)
        self.default_color = color
        self.hover_color = hover_color if hover_color else color
        self.is_negative = is_negative
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
        self.start_pulse()

    def leaveEvent(self, event):
        self.setStyleSheet(f"""
            background-color: {self.default_color};
            color: white;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)
        self.stop_pulse()

    def start_pulse(self):
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.pulse_effect)
        self.pulse_opacity = 1.0
        self.pulse_direction = -0.05
        self.pulse_timer.start(50)

    def stop_pulse(self):
        if hasattr(self, 'pulse_timer'):
            self.pulse_timer.stop()
            self.setGraphicsEffect(None)

    def pulse_effect(self):
        if self.pulse_opacity <= 0.5 or self.pulse_opacity >= 1.0:
            self.pulse_direction *= -1
        self.pulse_opacity += self.pulse_direction

        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(self.pulse_opacity)
        self.setGraphicsEffect(opacity_effect)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, window_width, window_height)
        self.setMinimumSize(480, 270)  # Minimum size to maintain aspect ratio

        # Set a consistent background color
        self.setStyleSheet(f"background-color: {startup_background_color};")

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet(f"background-color: {startup_background_color};")

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
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def create_startup_screen(self):
        """Create the startup screen with logo and animated titles."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {startup_background_color};")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setGraphicsEffect(QGraphicsOpacityEffect())
        self.logo_label.graphicsEffect().setOpacity(0)

        # Course Title Label
        self.course_title_label = QLabel(course_title)
        self.course_title_label.setFont(QFont(font_family, 24, QFont.Bold))
        self.course_title_label.setStyleSheet("color: #333333;")
        self.course_title_label.setAlignment(Qt.AlignCenter)
        self.course_title_label.setGraphicsEffect(QGraphicsOpacityEffect())
        self.course_title_label.graphicsEffect().setOpacity(0)

        # Project Title Label
        self.project_title_label = QLabel(project_title)
        self.project_title_label.setFont(QFont(font_family, 16))
        self.project_title_label.setStyleSheet("color: #555555;")
        self.project_title_label.setAlignment(Qt.AlignCenter)
        self.project_title_label.setWordWrap(True)
        self.project_title_label.setGraphicsEffect(QGraphicsOpacityEffect())
        self.project_title_label.graphicsEffect().setOpacity(0)

        # Fade-in animation for the logo
        self.logo_animation = QPropertyAnimation(self.logo_label.graphicsEffect(), b"opacity")
        self.logo_animation.setDuration(1000)  # 1 second
        self.logo_animation.setStartValue(0)
        self.logo_animation.setEndValue(1)

        # Fade-in animation for the course title
        self.course_title_animation = QPropertyAnimation(self.course_title_label.graphicsEffect(), b"opacity")
        self.course_title_animation.setDuration(1000)
        self.course_title_animation.setStartValue(0)
        self.course_title_animation.setEndValue(1)

        # Fade-in animation for the project title
        self.project_title_animation = QPropertyAnimation(self.project_title_label.graphicsEffect(), b"opacity")
        self.project_title_animation.setDuration(1000)
        self.project_title_animation.setStartValue(0)
        self.project_title_animation.setEndValue(1)

        # Sequential animation group
        self.title_animation_group = QSequentialAnimationGroup()
        self.title_animation_group.addAnimation(self.course_title_animation)
        self.title_animation_group.addAnimation(self.project_title_animation)

        # Start button
        self.start_button = PulsingButton("Proceed", "#E0E0E0", hover_color="#CCCCCC")
        self.start_button.setFixedSize(100, 40)
        self.start_button.clicked.connect(self.switch_to_main_menu)
        self.start_button.setVisible(False)
        self.start_button.setGraphicsEffect(QGraphicsOpacityEffect())
        self.start_button.graphicsEffect().setOpacity(0)

        # Animation for start button
        self.start_button_animation = QPropertyAnimation(self.start_button.graphicsEffect(), b"opacity")
        self.start_button_animation.setDuration(500)
        self.start_button_animation.setStartValue(0)
        self.start_button_animation.setEndValue(1)

        # Combine animations
        self.total_animation = QSequentialAnimationGroup()
        self.total_animation.addAnimation(self.logo_animation)
        self.total_animation.addPause(500)
        self.total_animation.addAnimation(self.title_animation_group)
        self.total_animation.addPause(500)
        self.total_animation.addAnimation(self.start_button_animation)
        self.total_animation.finished.connect(self.show_start_button)

        # Add widgets to layout
        layout.addStretch()
        layout.addWidget(self.logo_label)
        layout.addWidget(self.course_title_label)
        layout.addWidget(self.project_title_label)
        layout.addStretch()
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        widget.setLayout(layout)
        self.total_animation.start()

        return widget

    def show_start_button(self):
        """Make the start button visible after animations."""
        self.start_button.setVisible(True)

    def switch_to_main_menu(self):
        """Switch to the main menu with animation."""
        self.slide_to_widget(self.stacked_widget.indexOf(self.main_menu))

    def create_main_menu(self):
        """Create the main menu with Login, Register, and Exit buttons."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {startup_background_color};")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

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
        button_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        # Register Button
        self.register_button = PulsingButton("Register", yes_button_color, hover_color=hover_yes_button_color)
        self.register_button.clicked.connect(self.switch_to_register_screen)
        button_layout.addWidget(self.register_button, alignment=Qt.AlignCenter)

        # Exit Button
        self.exit_button = PulsingButton("Exit", no_button_color, hover_color=hover_pale_red, is_negative=True)
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)

        layout.addLayout(button_layout)
        widget.setLayout(layout)

        return widget

    def switch_to_login_screen(self):
        """Switch to the login screen with animation."""
        self.slide_to_widget(self.stacked_widget.indexOf(self.login_screen))

    def switch_to_register_screen(self):
        """Switch to the register screen with animation."""
        self.slide_to_widget(self.stacked_widget.indexOf(self.register_screen))

    def switch_to_robot_registration(self):
        """Switch to the robot registration screen with animation."""
        self.slide_to_widget(self.stacked_widget.indexOf(self.robot_registration_screen))

    def switch_to_robot_list(self):
        """Switch to the robot list screen with animation."""
        self.update_robot_list()
        self.slide_to_widget(self.stacked_widget.indexOf(self.robot_list_screen))

    def create_login_screen(self):
        """Create the login screen."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {startup_background_color};")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title and input layout
        input_layout = QVBoxLayout()
        input_layout.setAlignment(Qt.AlignCenter)
        input_layout.setSpacing(10)

        # Login Title
        self.label = QLabel("Login")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.label)

        # Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumWidth(300)
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.username_input, alignment=Qt.AlignCenter)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setMinimumWidth(300)
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        # Submit Button
        self.login_submit = PulsingButton("Login", yes_button_color, hover_color=hover_yes_button_color)
        self.login_submit.clicked.connect(self.login_user)
        input_layout.addWidget(self.login_submit, alignment=Qt.AlignCenter)

        # Add input_layout to main_layout
        main_layout.addLayout(input_layout)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red, is_negative=True)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(main_layout)
        return widget

    def create_register_screen(self):
        """Create the register screen."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {startup_background_color};")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title and input layout
        input_layout = QVBoxLayout()
        input_layout.setAlignment(Qt.AlignCenter)
        input_layout.setSpacing(10)

        # Register Title
        self.label = QLabel("Register")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        input_layout.addWidget(self.label)

        # New Username Input
        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("Enter new username")
        self.new_username_input.setMinimumWidth(300)
        self.new_username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.new_username_input, alignment=Qt.AlignCenter)

        # New Password Input
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Enter password")
        self.new_password_input.setMinimumWidth(300)
        self.new_password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.new_password_input, alignment=Qt.AlignCenter)

        # Confirm Password Input
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setMinimumWidth(300)
        self.confirm_password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.confirm_password_input, alignment=Qt.AlignCenter)

        # Submit Button
        self.register_submit = PulsingButton("Register", yes_button_color, hover_color=hover_yes_button_color)
        self.register_submit.clicked.connect(self.register_user)
        input_layout.addWidget(self.register_submit, alignment=Qt.AlignCenter)

        # Add input_layout to main_layout
        main_layout.addLayout(input_layout)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red, is_negative=True)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(main_layout)
        return widget

    def create_robot_registration_screen(self):
        """Create the robot registration screen after login or registration."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {startup_background_color};")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Robot Registration Title
        self.label = QLabel("Register a Robot")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label)

        # Robot Name Input
        self.robot_name_input = QLineEdit()
        self.robot_name_input.setPlaceholderText("Enter Robot Name")
        self.robot_name_input.setMinimumWidth(300)
        self.robot_name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(self.robot_name_input, alignment=Qt.AlignCenter)

        # Submit Button
        self.robot_submit = PulsingButton("Submit", yes_button_color, hover_color=hover_yes_button_color)
        self.robot_submit.clicked.connect(self.register_robot)
        main_layout.addWidget(self.robot_submit, alignment=Qt.AlignCenter)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red, is_negative=True)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(main_layout)
        return widget

    def create_robot_list_screen(self):
        """Create a screen to display the list of registered robots."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {startup_background_color};")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Registered Robots Title
        self.label = QLabel("Registered Robots")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label)

        # Robot List
        self.robot_list = QListWidget()
        self.robot_list.setMinimumWidth(300)
        self.robot_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.robot_list)

        # Back Button
        self.back_button = PulsingButton("Back", no_button_color, hover_color=hover_pale_red, is_negative=True)
        self.back_button.clicked.connect(self.switch_to_main_menu)
        main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        widget.setLayout(main_layout)
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
                if ',' in line:
                    saved_username, _ = line.strip().split(',', 1)
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
                if ',' in line:
                    saved_username, saved_hashed_password = line.strip().split(',', 1)
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

    def slide_to_widget(self, next_widget_index):
        """Slide transition to the specified widget."""
        current_index = self.stacked_widget.currentIndex()
        next_index = next_widget_index
        if current_index == next_index:
            return

        # Get current and next widget
        current_widget = self.stacked_widget.widget(current_index)
        next_widget = self.stacked_widget.widget(next_index)

        # Decide the direction based on index
        if next_index > current_index:
            # Slide left to right
            offset = self.stacked_widget.geometry().width()
        else:
            # Slide right to left
            offset = -self.stacked_widget.geometry().width()

        # Position next_widget
        next_widget.setGeometry(self.stacked_widget.geometry())
        next_widget.move(offset, 0)

        # Bring next_widget to front
        next_widget.raise_()

        # Animate current_widget
        self.animation_current = QPropertyAnimation(current_widget, b'pos')
        self.animation_current.setDuration(500)
        self.animation_current.setStartValue(current_widget.pos())
        self.animation_current.setEndValue(QPoint(-offset, current_widget.pos().y()))
        self.animation_current.setEasingCurve(QEasingCurve.OutCubic)

        # Animate next_widget
        self.animation_next = QPropertyAnimation(next_widget, b'pos')
        self.animation_next.setDuration(500)
        self.animation_next.setStartValue(next_widget.pos())
        self.animation_next.setEndValue(QPoint(0, next_widget.pos().y()))
        self.animation_next.setEasingCurve(QEasingCurve.OutCubic)

        # Create a group animation
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.animation_current)
        self.animation_group.addAnimation(self.animation_next)

        def on_animation_finished():
            self.stacked_widget.setCurrentIndex(next_index)
            # Reset positions
            current_widget.move(0, 0)
            next_widget.move(0, 0)

        self.animation_group.finished.connect(on_animation_finished)
        self.animation_group.start()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()









