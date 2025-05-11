import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QSpinBox, QPushButton, QGridLayout
)

class FirstScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("첫 화면 : 근무 정보 입력")
        self.resize(300, 200)

        layout = QGridLayout(self)

        layout.addWidget(QLabel("근무 인원:"), 0 , 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Pyside6 테스트 창")
    window.resize(300, 200)
    window.show()
    sys.exit(app.exec())
