import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QSpinBox, QPushButton, QGridLayout,
    QVBoxLayout, QTableWidget, QLineEdit,
    QComboBox
)

class FirstScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("첫 화면 : 근무 정보 입력")
        self.resize(300, 200)

        layout = QGridLayout(self)

        # 1) 근무 인원 정보
        layout.addWidget(QLabel("근무 인원:"), 0 , 0)
        self.spin_staff = QSpinBox()
        self.spin_staff.setMinimum(1) #공익이 최소 한명은 있겠죠 :)
        self.spin_staff.setMaximum(10)
        layout.addWidget(self.spin_staff, 0 , 1)

        # 2) 당 월 총 일수 (ex. 3월이면 31)
        layout.addWidget(QLabel("당 월 총 일수:"), 1 , 0 )
        self.spin_days = QSpinBox()
        self.spin_days.setMinimum(27)
        self.spin_days.setMaximum(31)
        layout.addWidget(self.spin_days, 1 , 1)

        # 3) 당 월 총 근무 일수
        layout.addWidget(QLabel("당 월 총 근무 일수:"), 2, 0)
        self.spin_workdays = QSpinBox()
        self.spin_workdays.setMinimum(10)
        self.spin_workdays.setMaximum(31)
        layout.addWidget(self.spin_workdays, 2 , 1)

        # 4) 다음 화면 넘어가기 버튼
        btn_next = QPushButton("다음")
        layout.addWidget(btn_next, 3,0,1,2)
        btn_next.clicked.connect(self.on_next)

    def on_next(self):
        #입력값을 변수로 저장
        self.num_staff    = self.spin_staff.value()
        self.num_days     = self.spin_days.value()
        self.num_workdays = self.spin_workdays.value()

        print("입력된 값 : ",
              self.num_staff,
              self.num_days,
              self.num_workdays)
        
        # 2) SecondScreen 생성 & 표시
        self.second = SecondScreen(num_staff, num_days, num_workdays)
        self.second.show()

        # 3) FirstScreen 닫기
        self.close()
        
        # TODO : 두 번째 화면으로 넘어가는 로직 구현 필요

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FirstScreen()
    win.show()
    sys.exit(app.exec())
