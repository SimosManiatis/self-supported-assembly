import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGraphicsOpacityEffect, QStackedWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation  # QPropertyAnimation must be imported from QtCore

# Parameters for the design and functionality
window_title = "Robot Registration"
yes_button_label = "Add Robot"
no_button_label = "Cancel"
submit_button_label = "Submit"
default_robot_name = "Robot A"

# Image path for startup logo
logo_path = r"D:\.CORE\LocalRepo\self-supported-assembly\self-supported-assembly\SimosScripts\InteractiveScript\images\0.png"

# Aspect Ratio 16:9
window_width = 960
window_height = 540

# Colors and fonts
window_background_color = "#F9F9F9"
yes_button_color = "#007AFF"
no_button_color = "#D3D3D3"
hover_pale_red = "#FFA07A"
hover_yes_button_color = "#005EC9"
text_color = "#000000"
font_family = "Helvetica"
startup_background_color = "#000000"

# Registered robots list
registered_robots = []


class PulsingButton(QPushButton):
    """A QPushButton that pulses and changes color when hovered."""
    def __init__(self, label, color, hover_color=None):
        super().__init__(label)
        self.default_color = color
        self.hover_color = hover_color if hover_color else color
        self.setFixedSize(200, 50)  # Fixed size for the button
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
        """Change color on hover without resizing the button."""
        self.setStyleSheet(f"""
            background-color: {self.hover_color};
            color: white;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)

    def leaveEvent(self, event):
        """Reset color when hover ends."""
        self.setStyleSheet(f"""
            background-color: {self.default_color};
            color: white;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)


class CircularButton(QPushButton):
    """A QPushButton styled as a circular button."""
    def __init__(self, color, hover_color=None):
        super().__init__()
        self.default_color = color
        self.hover_color = hover_color if hover_color else color
        self.setFixedSize(50, 50)  # Circular button size
        self.setStyleSheet(f"""
            background-color: {color};
            border: none;
            border-radius: 25px;
        """)

    def enterEvent(self, event):
        """Change color on hover."""
        self.setStyleSheet(f"""
            background-color: {self.hover_color};
            border: none;
            border-radius: 25px;
        """)

    def leaveEvent(self, event):
        """Reset color when hover ends."""
        self.setStyleSheet(f"""
            background-color: {self.default_color};
            border: none;
            border-radius: 25px;
        """)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.robot_name = default_robot_name
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, window_width, window_height)

        self.stacked_widget = QStackedWidget()

        # Create the different screens
        self.startup_screen = self.create_startup_screen()
        self.main_menu = self.create_main_menu()
        self.robot_name_window = self.create_robot_name_window()
        self.registered_robots_window = self.create_registered_robots_window()

        # Add screens to the stacked widget
        self.stacked_widget.addWidget(self.startup_screen)
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.robot_name_window)
        self.stacked_widget.addWidget(self.registered_robots_window)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def create_startup_screen(self):
        """Create the startup screen with logo and circular button."""
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

        # Opacity effect for fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect()
        self.logo_label.setGraphicsEffect(self.opacity_effect)

        # Fade-in animation
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(5000)  # 5 seconds
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.start()

        # Circular button under the logo
        self.start_button = CircularButton("#FFFFFF", hover_color="#CCCCCC")
        self.start_button.clicked.connect(self.switch_to_main_menu)

        layout.addWidget(self.logo_label)
        layout.addSpacing(20)  # Space between logo and button
        layout.addWidget(self.start_button)
        widget.setLayout(layout)

        return widget

    def switch_to_main_menu(self):
        """Switch from startup screen to main menu."""
        self.stacked_widget.setCurrentWidget(self.main_menu)

    def create_main_menu(self):
        """Create the main menu screen."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Prompt Label
        self.label = QLabel("Would you like to register a robot?")
        self.label.setFont(QFont(font_family, 18))
        self.label.setStyleSheet(f"color: {text_color};")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        # Yes Button
        self.yes_button = PulsingButton(yes_button_label, yes_button_color, hover_color=hover_yes_button_color)
        self.yes_button.clicked.connect(self.switch_to_robot_name_window)
        button_layout.addWidget(self.yes_button)

        # No Button
        self.no_button = PulsingButton(no_button_label, no_button_color, hover_color=hover_pale_red)
        self.no_button.clicked.connect(self.close)
        button_layout.addWidget(self.no_button)

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

        return widget

    def create_robot_name_window(self):
        """Create the robot name input screen."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Label
        self.label = QLabel("Enter the name of Robot A:")
        self.label.setFont(QFont(font_family, 14))
        self.label.setStyleSheet(f"color: {text_color};")

        # Input Field
        self.name_input = QLineEdit(self)
        self.name_input.setText(default_robot_name)
        self.name_input.setStyleSheet("""
            padding: 10px;
            background-color: white;
            border: 1px solid #CCCCCC;
            border-radius: 8px;
            font-size: 14px;
        """)

        # Submit Button
        self.submit_button = PulsingButton(submit_button_label, yes_button_color, hover_color=hover_yes_button_color)
        self.submit_button.clicked.connect(self.submit_name)

        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.submit_button)

        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

        return widget

    def create_registered_robots_window(self):
        """Create the registered robots display screen."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Label
        self.label = QLabel("Registered Robots:")
        self.label.setFont(QFont(font_family, 16))
        self.label.setStyleSheet(f"color: {text_color};")
        layout.addWidget(self.label)

        # List of registered robots
        self.robot_list = QListWidget()
        self.update_robot_list()
        layout.addWidget(self.robot_list)

        # Add and Remove buttons
        button_layout = QHBoxLayout()

        # Add Robot Button
        self.add_button = PulsingButton("Add Robot", yes_button_color, hover_color=hover_yes_button_color)
        self.add_button.clicked.connect(self.switch_to_robot_name_window)
        button_layout.addWidget(self.add_button)

        # Remove Robot Button
        self.remove_button = PulsingButton("Remove Robot", no_button_color, hover_color=hover_pale_red)
        self.remove_button.clicked.connect(self.remove_robot)
        button_layout.addWidget(self.remove_button)

        layout.addLayout(button_layout)
        layout.setAlignment(Qt.AlignCenter)
        widget.setLayout(layout)

        return widget

    def update_robot_list(self):
        """Update the robot list display."""
        self.robot_list.clear()
        self.robot_list.addItems(registered_robots)

    def switch_to_robot_name_window(self):
        """Switch to the robot name input screen."""
        self.stacked_widget.setCurrentWidget(self.robot_name_window)

    def submit_name(self):
        """Save the robot name and switch to the registered robots screen."""
        self.robot_name = self.name_input.text()
        if self.robot_name:
            registered_robots.append(self.robot_name)
            print(f"Registered Robots: {registered_robots}")
            self.switch_to_registered_robots_window()

    def remove_robot(self):
        """Remove the selected robot from the list."""
        selected_items = self.robot_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Remove Robot", "No robot selected.")
            return
        for item in selected_items:
            registered_robots.remove(item.text())  # Remove robot from the list
            print(f"Removed {item.text()}")
            print(f"Updated Registered Robots: {registered_robots}")
        self.update_robot_list()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    app.exec_()


if __name__ == '__main__':
    main()















