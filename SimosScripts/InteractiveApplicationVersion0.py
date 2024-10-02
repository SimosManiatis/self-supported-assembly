import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Parameters you can change at the beginning of the script
window_title = "CORE 2024: Self-Supported Robotic Assembly"
yes_button_label = "Yes"
no_button_label = "No"
submit_button_label = "Submit"
default_robot_name = ""
window_width = 300
window_height = 300

def create_ui(window_title, yes_button_label, no_button_label, submit_button_label, default_robot_name, window_width, window_height):

    class RobotNameWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.robot_name = default_robot_name
            self.init_ui()
        
        def init_ui(self):
            self.setWindowTitle("Enter Robot A Name")
            self.setGeometry(100, 100, 300, 100)

            layout = QVBoxLayout()

            # Label
            self.label = QLabel("Enter the name of Robot A:")
            self.label.setFont(QFont('Arial', 12))
            
            # Input Field
            self.name_input = QLineEdit(self)
            self.name_input.setText(default_robot_name)
            self.name_input.setStyleSheet("""
                padding: 8px;
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-bottom: 15px;
            """)

            # Submit Button
            self.submit_button = QPushButton(submit_button_label)
            self.submit_button.setStyleSheet("""
                background-color: #5cb85c;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
            """)
            self.submit_button.setFont(QFont('Arial', 10))
            self.submit_button.clicked.connect(self.submit_name)

            layout.addWidget(self.label)
            layout.addWidget(self.name_input)
            layout.addWidget(self.submit_button)

            self.setLayout(layout)

        def submit_name(self):
            self.robot_name = self.name_input.text()
            if self.robot_name:
                QMessageBox.information(self, "Success", f"Robot A's name is {self.robot_name}")
                self.close()

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

            layout = QVBoxLayout()

            # Prompt Label
            self.label = QLabel("Hey, would you like to register a robot to the system?")
            self.label.setFont(QFont('Arial', 12))
            self.label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.label)

            # Yes Button
            self.yes_button = QPushButton(yes_button_label)
            self.yes_button.setStyleSheet("""
                background-color: #5bc0de;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
            """)
            self.yes_button.setFont(QFont('Arial', 10))
            self.yes_button.clicked.connect(self.on_yes)
            layout.addWidget(self.yes_button)

            # No Button
            self.no_button = QPushButton(no_button_label)
            self.no_button.setStyleSheet("""
                background-color: #d9534f;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
            """)
            self.no_button.setFont(QFont('Arial', 10))
            self.no_button.clicked.connect(self.on_no)
            layout.addWidget(self.no_button)

            # Centering
            layout.setAlignment(self.label, Qt.AlignCenter)
            layout.setAlignment(self.yes_button, Qt.AlignCenter)
            layout.setAlignment(self.no_button, Qt.AlignCenter)
            layout.setSpacing(10)

            self.setLayout(layout)

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
            if self.robot_name_window and self.robot_name_window.isVisible():
                self.robot_name_window.close()
            event.accept()

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
response, robot_name = create_ui(window_title, yes_button_label, no_button_label, submit_button_label, default_robot_name, window_width, window_height)

# Print outputs
print(f"User Response: {response}")
if response == "Yes":
    print(f"Robot A's Name: {robot_name}")
else:
    print("No robot registered.")
