import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel,
    QSpinBox, QPushButton, QGridLayout,
    QVBoxLayout, QTableWidget, QLineEdit,
    QComboBox, QHeaderView, QTableWidgetItem
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
    pref_map = {
            "상관 없음" : 0,
            "주간 선호" : 1,
            "야간 선호" : 2
        }
    day_map = {
            "X" : 0,
            "주" : 1,
            "야" : 2,
            "비" : 3,
            "휴" : 4,
            "연" : 5
        }

    def __init__(self, num_staff, num_days, num_workdays):
        super().__init__()
        self.num_staff = num_staff
        self.num_days = num_days
        self.num_workdays = num_workdays

        self.setWindowTitle("두 번째 화면 : 스케쥴 입력")
        self.resize(1400,400)

        # 테이블 생성 : 행-num_staff , 열-num_days+2

        self.day_start = 2
        self.stat_start = self.num_days + 2
        total_rows = self.num_staff + 2
        total_cols = self.stat_start + 4
        
        self.table = QTableWidget(total_rows, total_cols, self)
        headers = (
            ["이름", "선호"] + 
            [f"{i}일" for i in range(1, self.num_days+1)] + 
            ["주" , "야" , "총", "rem"]
        )
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # 셀마다 위젯 배치 (col 너비 조절 버젼)
        self.table.setColumnWidth(0,50) #이름
        self.table.setColumnWidth(1,80) #선호
        for c in range(2, self.stat_start):
            self.table.setColumnWidth(c, 38)
        for c in range(self.stat_start, total_cols):
            self.table.setColumnWidth(c, 38)
        
        self.table.verticalHeader().setDefaultSectionSize(24)
        self.table.setRowHeight(self.num_staff, 20)
        self.table.setRowHeight(self.num_staff+1, 20)


        # 기본 리사이즈 모드는 고정(Fixed)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)

        for r in range(self.num_staff):
            #이름 입력
            self.table.setCellWidget(r, 0, QLineEdit())

            #주야선호 드롭다운
            combo_pref = QComboBox()
            combo_pref.addItems(["주간 선호", "야간 선호", "상관 없음"])
            self.table.setCellWidget(r, 1 , combo_pref)

            #나머지 날짜 칸
            for c in range(2, self.stat_start):
                combo_day = QComboBox()
                combo_day.addItems(["X", "주", "야", "비", "휴", "연"])
                self.table.setCellWidget(r, c , combo_day)

            for c in range(self.stat_start, total_cols):
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(r,c,item)

        for summary_row in (self.num_staff, self.num_staff+1):
            for c in range(0, total_cols):
                item = QTableWidgetItem("-" if c<self.day_start else "0")
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(summary_row, c, item)

        btn_finish = QPushButton("완료")
        btn_finish.clicked.connect(self.on_finish)

        #레이아웃
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(btn_finish)
    

    def on_finish(self):
        arr = self.extract_array()
        """
        1) 테이블 → 정수 배열로 변환
        2) 첫 번째 알고리즘 단계 적용:
           [i][j] == 2 이고 다음 두 칸이 0 이면,
           [i][j+1]=3, [i][j+2]=4
           (열 인덱스 2 ~ stat_start-1 구간만)
        3) 변경된 배열을 다시 GUI에 덮어쓰기
        4) 집계 열 갱신
        """
        # 1) 맵핑 테이블 정의
        inv_day_map = {v:k for k, v in self.day_map.items() if v in (0,1,2,3,4,5)}

        self.apply_rule_pref1(arr)
        self.apply_rule_pref2(arr)
        self.apply_rule_rem(arr)
        self.apply_rule0(arr)
        self.final_feedback(arr)
        
        
        

        # 4) 배열을 GUI에 반영 (날짜 칸만)
        for r in range(self.num_staff):
            for j, val in enumerate(arr[r]):
                col_idx = self.day_start + j
                combo = self.table.cellWidget(r, col_idx)
                if combo:
                    combo.setCurrentText(inv_day_map[val])

        # 5) 집계 갱신
        for r in range(self.num_staff):
            # 날짜 값만 다시 읽어와서 집계
            day_vals = arr[r]
            cnt1 = day_vals.count(1)
            cnt2 = day_vals.count(2)
            total_work = cnt1 + cnt2 * 2
            remain = self.num_workdays - total_work

            stats = [cnt1, cnt2, total_work, remain]
            for k,v in enumerate(stats, start=self.stat_start):
                self.table.item(r,k).setText(str(v))

        self.update_summary(arr)

        # 6) 결과 출력
        print("입력된 스케쥴 정수 배열 : ")
        for row in arr:
            print(row)

    def extract_array(self):
        arr = []
        for r in range(self.num_staff):
            row_vals = []
            for c in range(self.day_start, self.stat_start):
                combo = self.table.cellWidget(r,c)
                text = combo.currentText()
                row_vals.append(self.day_map[text])
            arr.append(row_vals)
        return arr


    def apply_rule_pref1(self, arr):
        """Rule A: '주간 선호'인 사람부터 remain이 0 될 때까지 0 → 1로 채우되,
       1이 4일 연속되면 다음 날은 4로 채움."""
        for r in range(self.num_staff):
            pref = self.table.cellWidget(r,1).currentText()
            if pref != "주간 선호":
                continue

            day_vals = arr[r]
            cnt1 = day_vals.count(1)
            cnt2 = day_vals.count(2)
            remain = self.num_workdays - (cnt1 + cnt2 * 2)

            j = 0
            while j < len(day_vals) and remain > 0:
                if day_vals[j] == 0:
                    day_vals[j] = 1
                    remain -= 1

                    if j >= 3 and all(day_vals[k] == 1 for k in range(j-3, j+1)):
                        nxt = j + 1
                        if nxt < len(day_vals) and day_vals[nxt] == 0:
                            day_vals[nxt] = 4
                            j = nxt + 1
                            continue
                j += 1


    def apply_rule_pref2(self, arr):
        for r in range(self.num_staff):
            pref = self.table.cellWidget(r,1).currentText()
            if pref != "야간 선호":
                continue

            day_vals = arr[r]
            cnt1 = day_vals.count(1)
            cnt2 = day_vals.count(2)
            remain = self.num_workdays - (cnt1 + cnt2 * 2)
            j = 0

            while j < len(day_vals) - 2 and remain >= 2:
                if day_vals[j] == 0 and day_vals[j+1] == 0 and day_vals[j+2]==0:
                    day_vals[j], day_vals[j+1], day_vals[j+2] = 2,3,4
                    remain -= 2
                    j += 3
                else :
                    j += 1

    def apply_rule0(self, arr):
        """
    1) 매일(열)마다 1의 개수 < 1 이면 빈 칸에 1 추가
       2의 개수 < 1 이면 빈 칸에 2 추가
    2) 1의 개수 > 2 이면 초과분을 휴무(4)로 채움
       2의 개수 > 2 이면 초과분을 휴무(4)로 채움
    """
        n_days = len(arr[0])
        for j in range(n_days):
            # 1) counting
            col_vals = [arr[r][j] for r in range(self.num_staff)]
            cnt1 = col_vals.count(1)
            cnt2 = col_vals.count(2)

            # 2) 부족분 채우기
            if cnt1 < 1 :
                need = 1 - cnt1
                for r in range(self.num_staff):
                    if need == 0: break
                    #빈 칸이면서 주간 선호자 우선
                    pref = self.table.cellWidget(r,1).currentText()
                    if arr[r][j] == 0 and pref == "주간 선호":
                        arr[r][j] = 1
                        need -= 1
                    #남은 need는 상관없음 그룹에서 채우기
                    for r in range(self.num_staff):
                        if need == 0: break
                        if arr[r][j] == 0:
                            arr[r][j] = 1
                            need -= 1

            if cnt2 < 1:
                need = 1 - cnt2
                for r in range(self.num_staff):
                    if need == 0: break
                    pref = self.table.cellWidget(r,1).currentText()
                    if arr[r][j] == 0 and pref == "야간 선호":
                        arr[r][j] = 2
                        need -= 1
                for r in range(self.num_staff):
                    if need == 0: break
                    if arr[r][j] == 0:
                        arr[r][j] = 2
                        need -= 1
                
            # 3) 초과분 휴무로 변경
            col_vals = [arr[r][j] for r in range(self.num_staff)]
            while col_vals.count(1) > 2:
                idx = len(col_vals) - 1 - col_vals[::-1].index(1)
                arr[idx][j] = 4
                col_vals[idx] = 4
            col_vals = [arr[r][j] for r in range(self.num_staff)]
            while col_vals.count(2) > 2:
                idx = len(col_vals) - 1 - col_vals[::-1].index(2)
                arr[idx][j] = 4
                col_vals[idx] = 4

    def apply_rule_rem(self, arr):
        """
        남은(rem)>0 직원에 대해
        1) 먼저 빈 칸(0) 또는 주간(1) 슬롯을 찾아 채우고,
        2) 이후 rem이 남으면 업그레이드(1→2) 합니다.
        직원은 rem 내림차순 우선, 칸은 compute_priority_columns 순으로 채웁니다.
        """
        n_days = len(arr[0])
        max_iters = 100

        for _ in range(max_iters):
            # 1) rem 리스트 구하기
            rem_list = []
            for r in range(self.num_staff):
                cnt1 = arr[r].count(1)
                cnt2 = arr[r].count(2)
                rem  = self.num_workdays - (cnt1 + cnt2 * 2)
                rem_list.append((rem, r))
            rem_list.sort(reverse=True)  # rem 큰 순

            # 종료 조건: 가장 큰 rem <= 0
            if rem_list[0][0] <= 0:
                break

            changed = False
            # 2) 직원별로 탐색
            for rem, r in rem_list:
                if rem <= 0:
                    continue

                # 2-1) 이 직원의 선호
                pref_text = self.table.cellWidget(r,1).currentText()
                pref_val  = self.pref_map.get(pref_text, 0)

                # 2-2) 이 직원의 우선순위 날짜 열
                cols = self.compute_priority_columns(arr)

                # 3) 슬롯 채우기: 먼저 빈칸(0) → then 업그레이드(1→2)
                #   A) 0 슬롯
                for j in cols:
                    if rem <= 0:
                        break
                    if arr[r][j] != 0:
                        continue
                    # 선호대로 채워보기
                    if pref_val == 2 and rem >= 2:
                        arr[r][j] = 2; rem -= 2
                    elif pref_val == 1:
                        arr[r][j] = 1; rem -= 1
                    else:
                        # 비선호 채우기: rem>=2→야, else 주
                        if rem >= 2:
                            arr[r][j] = 2; rem -= 2
                        else:
                            arr[r][j] = 1; rem -= 1
                    changed = True

                #  B) 1→2 업그레이드 (해당 직원이 야간 선호거나 rem>=1인 경우)
                if rem > 0:
                    for j in cols:
                        if rem <= 0:
                            break
                        if arr[r][j] == 1:
                            arr[r][j] = 2
                            rem -= 1
                            changed = True

                # 4) 한 칸이라도 채웠으면 다음 반복에서 rem_list 재계산
                if changed:
                    break

            if not changed:
                # 더 이상 채울 곳이 없으면 종료
                break

        if changed is False:
            print("⚠ apply_rule_rem: 채울 슬롯이 남아있지 않아 중단")

                
    def final_feedback(self, arr):
        for r in range(self.num_staff):
            for j in range(len(arr[r]) - 1 ):
                if arr[r][j] == 2 and arr[r][j+1] == 2:
                    arr[r][j+1] = 3
        for r in range(self.num_staff):
            cnt1 = arr[r].count(1)
            cnt2 = arr[r].count(2)
            rem = self.num_workdays - (cnt1 + cnt2*2)
            if rem<0:
                for j in range(len(arr[r])):
                    col_vals = [arr[x][j] for x in range(self.num_staff)]
                    if col_vals.count(1) == 2 and arr[r][j] == 1:
                        arr[r][j] = 4


    def update_summary(self, arr):
        self.col_cnt1 = []
        self.col_cnt2 = []

        days = self.num_days
        sum_row1 = self.table.rowCount() - 2
        sum_row2 = self.table.rowCount() - 1

        for j in range(days):
            cnt1 = sum(1 for r in range(self.num_staff) if arr[r][j] == 1)
            cnt2 = sum(1 for r in range(self.num_staff) if arr[r][j] == 2)
            self.col_cnt1.append(cnt1)
            self.col_cnt2.append(cnt2)

            col_idx = self.day_start + j

            item1 = self.table.item(sum_row1, col_idx)
            if item1 is None:
                item1 = QTableWidgetItem()
                item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item1.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(sum_row1, col_idx, item1)
            item1.setText(str(cnt1))

            item2 = self.table.item(sum_row2, col_idx)
            if item2 is None:
                item2 = QTableWidgetItem()
                item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                item2.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(sum_row2, col_idx, item2)
            item2.setText(str(cnt2))

    def compute_priority_columns(self, arr):
        n_days = len(arr[0])
        col_cnt1 = [
            sum(1 for r in range(self.num_staff) if arr[r][j] == 1)
            for j in range(n_days)
        ]
        col_cnt2 = [
            sum(1 for r in range(self.num_staff) if arr[r][j] == 2)
            for j in range(n_days)
        ]

        priority = []
        priority += [j for j in range(n_days) if col_cnt2[j] == 0]
        priority += [j for j in range(n_days) if col_cnt1[j] == 0]
        priority += [j for j in range(n_days) if col_cnt2[j] == 1]
        priority += [j for j in range(n_days) if col_cnt1[j] == 1]

        # 중복 제거하면서 순서 유지
        seen = set()
        return [j for j in priority if j not in seen and not seen.add(j)]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FirstScreen()
    win.show()
    sys.exit(app.exec())


'''
    def apply_rule_rem(self, arr):
        # 1) 열 우선순위 계산 (col_cnt1/col_cnt2 기반)
        max_iters = 100
        iters = 0
        n_days = len(arr[0])

        # 2) rem이 모두 0이 될 때 까지 반복
        while True:
            
            # 2-a) 각 직원 rem 계산
            rem_list = []
            for r in range(self.num_staff):
                cnt1 = arr[r].count(1)
                cnt2 = arr[r].count(2)
                rem = self.num_workdays - (cnt1 + cnt2 * 2)
                rem_list.append((rem,r))

            if all(rem == 0 for rem, _  in rem_list) or iters >= max_iters: break
            priority = self.compute_priority_columns(arr)
            
            candidates = sorted(
                [(rem, r) for rem, r in rem_list if rem > 0],
                reverse=True, key=lambda x: x[0]
            )
            for j in priority:
                for status in (0,1):
                    for rem, r in candidates:
                        if rem <= 0:
                            continue
                        if arr[r][j] == status:
                            if status == 0:
                                if rem >= 2:
                                    arr[r][j] = 2
                                    rem -= 2
                                else:
                                    arr[r][j] = 1
                                    rem -= 1
                            else:
                                arr[r][j] = 2
                                rem -= 1
                            for idx, (old_rem, rr) in enumerate(candidates):
                                if rr == r:
                                    candidates[idx] = (rem, rr)
                                    break
                            break

            negatives = sorted(
                [(rem,r) for rem, r in rem_list if rem < 0],
                key=lambda x: x[0]
            )
            for rem, r in negatives:
                for j in reversed(priority):
                    if rem >= 0:
                        break
                    if arr[r][j] == 1:
                        arr[r][j] = 4
                        rem += 1

            iters += 1
            if iters >= max_iters:
                print(f"⚠ 반복 횟수 {max_iters}회 도달: 루프를 중단합니다.")
                break
'''