import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QSpinBox, QPushButton, QGridLayout,
    QVBoxLayout, QTableWidget, QLineEdit,
    QComboBox, QHeaderView
)



# Tab 이동 커스터마이즈, 이름 작성시 중앙정렬
class TabLineEdit(QLineEdit):
    def __init__(self, row, table):
        super().__init__()
        self.row = row
        self.table = table
        self.setAlignment(Qt.AlignCenter)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            next_row = self.row + 1
            if next_row < self.table.rowCount():
                w = self.table.cellWidget(next_row, 0)
                if w :
                    w.setFocus()
                    w.selectAll()
                    return
        super().keyPressEvent(event)

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
        num_staff    = self.spin_staff.value()
        num_days     = self.spin_days.value()
        num_workdays = self.spin_workdays.value()

        print("입력된 값 : ",
              num_staff,
              num_days,
              num_workdays)
        
        # 2) SecondScreen 생성 & 표시
        self.second = SecondScreen(num_staff, num_days, num_workdays)
        self.second.show()

        # 3) FirstScreen 닫기
        self.close()
        
class SecondScreen(QWidget):
    def __init__(self, num_staff, num_days, num_workdays):
        super().__init__()
        self.num_staff = num_staff
        self.num_days = num_days
        self.num_workdays = num_workdays

        self.setWindowTitle("두 번째 화면 : 스케쥴 입력")
        self.resize(1200,600)

        # 테이블 생성 : 행-num_staff , 열-num_days+2
        cols = self.num_days + 2
        self.table = QTableWidget(self.num_staff, cols, self)
        headers = ["이름", "선호"] + [f"{i}일" for i in range(1, self.num_days+1)]
        self.table.setHorizontalHeaderLabels(headers)

        # 셀마다 위젯 배치 (col 너비 조절 버젼)
        self.table.setColumnWidth(0,200) #이름
        self.table.setColumnWidth(1,120) #선호
        for c in range(2, cols):
            self.table.setColumnWidth(c,30)

        # 기본 리사이즈 모드는 고정(Fixed)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)

        for r in range(self.num_staff):
            #이름 입력
            name_edit = TabLineEdit(r, self.table)
            self.table.setCellWidget(r, 0, QLineEdit())

            #주야선호 드롭다운
            combo_pref = QComboBox()
            combo_pref.addItems(["주간 선호", "야간 선호", "상관 없음"])
            self.table.setCellWidget(r, 1 , combo_pref)

            #나머지 날짜 칸
            for c in range(2, cols):
                combo_day = QComboBox()
                combo_day.addItems(["X", "주", "야", "비", "휴", "연"])
                self.table.setCellWidget(r, c , combo_day)

        btn_finish = QPushButton("완료")
        btn_finish.clicked.connect(self.on_finish)

        #레이아웃
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(btn_finish)
    
    def on_finish(self):
        # 예시 : 테이블 데이터 추출
        data = []
        for r in range(self.num_staff):
            row = []
            for c in range (self.num_days+2):
                w = self.table.cellWidget(r,c)
                if isinstance(w, QLineEdit):
                    row.append(w.text())
                elif isinstance(w, QComboBox):
                    row.append(w.currentText())
            data.appen(row)
        print("테이블 전체 데이터", data)
        # TODO "X" 채우기 및 3번 로직 진행


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FirstScreen()
    win.show()
    sys.exit(app.exec())
