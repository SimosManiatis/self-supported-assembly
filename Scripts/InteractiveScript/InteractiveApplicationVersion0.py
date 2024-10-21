import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QMessageBox, QListWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve

# Parameters for the design and functionality
window_title = "Robot Registration"
yes_button_label = "Add Robot"
no_button_label = "Cancel"
submit_button_label = "Submit"
default_robot_name = "Robot A"

# Aspect Ratio 16:9
window_width = 960
window_height = 540

# Apple-inspired colors and fonts
window_background_color = "#F9F9F9"  # Light grayish-white background
yes_button_color = "#007AFF"  # Apple-like blue color for the main action buttons
no_button_color = "#D3D3D3"  # Soft muted color for cancel/secondary actions
hover_pale_red = "#FFA07A"  # Pale red for hover effect on Cancel/Remove buttons
hover_yes_button_color = "#005EC9"  # Darker blue when hovered over Yes button
text_color = "#000000"  # Black text color
font_family = "Helvetica"  # Use Helvetica for a clean, Apple-like feel

# Registered robots list and a reference to the current Registered Robots window
registered_robots = []
current_registered_window = None  # This will keep track of the active Registered Robots window


def apply_shadow(widget):
    """Applies a soft shadow effect to a widget (used for buttons)."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setOffset(2, 2)
    shadow.setColor(QColor(0, 0, 0, 100))  # Soft shadow with slight transparency
    widget.setGraphicsEffect(shadow)


def animate_widget_bounce(widget):
    """Bounce animation effect when the widget is shown."""
    bounce_animation = QPropertyAnimation(widget, b"geometry")
    bounce_animation.setDuration(600)
    bounce_animation.setStartValue(QRect(widget.x(), widget.y() - 20, widget.width(), widget.height()))
    bounce_animation.setEndValue(QRect(widget.x(), widget.y(), widget.width(), widget.height()))
    bounce_animation.setEasingCurve(QEasingCurve.OutBounce)
    bounce_animation.start()


class PulsingButton(QPushButton):
    """A QPushButton that pulses and changes color when hovered."""
    def __init__(self, label, color, hover_color=None):
        super().__init__(label)
        self.default_color = color
        self.hover_color = hover_color if hover_color else color
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)
        self.setFont(QFont(font_family, 12))
        self.default_geometry = None
        apply_shadow(self)

    def enterEvent(self, event):
        """Triggers the pulsing effect and changes the color when hovering over the button."""
        if not self.default_geometry:
            self.default_geometry = self.geometry()
        
        # Pulse animation
        self.pulse_animation = QPropertyAnimation(self, b"geometry")
        self.pulse_animation.setDuration(200)
        self.pulse_animation.setStartValue(self.default_geometry)
        self.pulse_animation.setEndValue(QRect(self.x() - 5, self.y() - 5, self.width() + 10, self.height() + 10))
        self.pulse_animation.start()

        # Change color on hover
        self.setStyleSheet(f"""
            background-color: {self.hover_color};
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)

    def leaveEvent(self, event):
        """Resets the button back to its original size and color when the hover ends."""
        if self.default_geometry:
            self.pulse_animation = QPropertyAnimation(self, b"geometry")
            self.pulse_animation.setDuration(200)
            self.pulse_animation.setStartValue(self.geometry())
            self.pulse_animation.setEndValue(self.default_geometry)
            self.pulse_animation.start()

        # Reset color to default
        self.setStyleSheet(f"""
            background-color: {self.default_color};
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-family: {font_family};
            font-size: 14px;
        """)


def create_ui(window_title, yes_button_label, no_button_label, submit_button_label, default_robot_name, window_width, window_height, window_background_color, yes_button_color, no_button_color, hover_yes_button_color, hover_pale_red, text_color, font_family):

    class RobotNameWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.robot_name = default_robot_name
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("Enter Robot A Name")
            self.setGeometry(100, 100, int(window_width * 0.6), int(window_height * 0.3))  # Smaller window size
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

            self.setLayout(layout)
            animate_widget_bounce(self)

        def submit_name(self):
            self.robot_name = self.name_input.text()
            if self.robot_name:
                registered_robots.append(self.robot_name)
                print(f"Registered Robots: {registered_robots}")
                self.close()
                self.show_registered_robots_window()

        def show_registered_robots_window(self):
            global current_registered_window
            if current_registered_window:
                current_registered_window.close()  # Close the outdated Registered Robots window

            current_registered_window = RegisteredRobotsWindow()
            current_registered_window.show()

    class RegisteredRobotsWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle("Registered Robots")
            self.setGeometry(100, 100, window_width, window_height)
            self.setStyleSheet(f"background-color: {window_background_color};")  # Set background color
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
            self.add_button.clicked.connect(self.add_robot)
            button_layout.addWidget(self.add_button)

            # Remove Robot Button
            self.remove_button = PulsingButton("Remove Robot", no_button_color, hover_color=hover_pale_red)
            self.remove_button.clicked.connect(self.remove_robot)
            button_layout.addWidget(self.remove_button)

            layout.addLayout(button_layout)
            self.setLayout(layout)

            animate_widget_bounce(self)

        def update_robot_list(self):
            """Update the robot list display."""
            self.robot_list.clear()
            self.robot_list.addItems(registered_robots)

        def add_robot(self):
            """Open the RobotNameWindow to add a new robot."""
            self.robot_name_window = RobotNameWindow()
            self.robot_name_window.show()

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

    class MainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.robot_name_window = None
            self.user_response = None
            self.robot_name = None
            self.init_ui()

        def init_ui(self):
            self.setWindowTitle(window_title)
            self.setGeometry(100, 100, window_width, window_height)
            self.setStyleSheet(f"background-color: {window_background_color};")  # Set window background

            layout = QVBoxLayout()

            # Prompt Label
            self.label = QLabel("Would you like to register a robot?")
            self.label.setFont(QFont(font_family, 18))
            self.label.setStyleSheet(f"color: {text_color};")
            self.label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.label)

            # Yes Button
            self.yes_button = PulsingButton(yes_button_label, yes_button_color, hover_color=hover_yes_button_color)
            self.yes_button.clicked.connect(self.on_yes)
            layout.addWidget(self.yes_button)

            # No Button
            self.no_button = PulsingButton(no_button_label, no_button_color, hover_color=hover_pale_red)
            self.no_button.clicked.connect(self.on_no)
            layout.addWidget(self.no_button)

            layout.setAlignment(self.label, Qt.AlignCenter)
            layout.setAlignment(self.yes_button, Qt.AlignCenter)
            layout.setAlignment(self.no_button, Qt.AlignCenter)
            layout.setSpacing(10)

            self.setLayout(layout)

            # Bounce animation for the main window
            animate_widget_bounce(self)

        def on_yes(self):
            # Open the child window to prompt for robot name
            self.robot_name_window = RobotNameWindow()
            self.robot_name_window.show()
            self.user_response = "Yes"

        def on_no(self):
            # Close the window and log the response
            self.user_response = "No"
            self.close()

        def closeEvent(self, event):
            # Fade-out animation when the window is closed
            fade_out = QPropertyAnimation(self, b"windowOpacity")
            fade_out.setDuration(500)
            fade_out.setStartValue(1)
            fade_out.setEndValue(0)
            fade_out.start()

            if self.robot_name_window and self.robot_name_window.isVisible():
                self.robot_name_window.close()
            event.accept()

        def resizeEvent(self, event):
            """Override the resize event to adjust button geometry on window resize."""
            super().resizeEvent(event)
            if self.yes_button.default_geometry:
                self.yes_button.default_geometry = self.yes_button.geometry()
            if self.no_button.default_geometry:
                self.no_button.default_geometry = self.no_button.geometry()

    def main():
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()

        app.exec_()

        # Return values after windows close
        user_response = main_window.user_response
        robot_name = main_window.robot_name_window.robot_name if main_window.robot_name_window else None
        return user_response, robot_name

    return main()


# Call the function to run the UI
response, robot_name = create_ui(window_title, yes_button_label, no_button_label, submit_button_label, default_robot_name, window_width, window_height, window_background_color, yes_button_color, no_button_color, hover_yes_button_color, hover_pale_red, text_color, font_family)

# Print outputs
print(f"User Response: {response}")
if response == "Yes":
    print(f"Robot A's Name: {robot_name}")
else:
    print("No robot registered.")

