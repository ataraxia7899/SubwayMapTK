import pandas as pd
from datetime import datetime
from tkinter import Tk, Toplevel, StringVar, Canvas, BOTH, LEFT, RIGHT, TOP, X, CENTER
from tkinter import ttk
from tkinter import font, Label
from PIL import Image, ImageTk
import sys
sys.path.append('./SubwayMap')
from SubwayData import BUTTON_COORDS, SUBWAY

# 전역 변수로 드래그 상태 추적
is_dragging_global = False
mouse_start_x = 0
mouse_start_y = 0

def get_mouse_click_coor(event):
    # """마우스 클릭 시 좌표 값을 출력하고 클립보드에 복사하는 함수"""
    global is_dragging_global, mouse_start_x, mouse_start_y
    
    # 드래그 중이면 좌표 출력하지 않음
    if is_dragging_global:
        return
    
    # 클릭과 드래그 구분 (5픽셀 이상 움직였으면 드래그로 간주)
    dx = abs(event.x - mouse_start_x)
    dy = abs(event.y - mouse_start_y)
    if dx > 5 or dy > 5:
        return
    
    x = event.x
    y = event.y
    coordinates = f"{x}, {y}" # 좌표 문자열 생성
    print(f"클릭 좌표: {coordinates}")
    # 클립보드에 복사
    root.clipboard_clear()  # 기존 클립보드 내용 삭제
    root.clipboard_append(coordinates) # 새로운 좌표 추가
    print(f"좌표 '{coordinates}'가 클립보드에 복사되었습니다.")
    
    # 클릭 후 드래그 상태 초기화
    is_dragging_global = False

class SubwayApp:
    def __init__(self, root):
        self.root = root
        self.start = ''
        self.end = ''
        self.img_scale = 1.0
        self.img_min_scale = 0.2
        self.img_max_scale = 3.0
        self.img_drag_start_x = 0
        self.img_drag_start_y = 0
        self.is_dragging = False  # 드래그 상태 추적
        self.img_btns = []
        self.img_btn_ids = []
        self.routing = {place: {'shortestDist': 0, 'route': [], 'visited': 0} for place in SUBWAY.keys()}
        # 역 버튼 클릭/드래그 구분용 변수
        self.btn_click_start_x = 0
        self.btn_click_start_y = 0
        self.btn_click_candidate_idx = None
        # 역 목록 생성
        self.station_list = list(SUBWAY.keys())
        self.station_list.sort()
        
        # 환승역 리스트 (인접 노드 3개 이상)
        self.transfer_stations = [name for name, adj in SUBWAY.items() if len(adj) >= 3]
        
        # 디버깅: station_list에 "숙등"과 "남산정"이 있는지 확인
        print(f"DEBUG: station_list에 '숙등' 포함: {'숙등' in self.station_list}")
        print(f"DEBUG: station_list에 '남산정' 포함: {'남산정' in self.station_list}")
        print(f"DEBUG: station_list 길이: {len(self.station_list)}")
        print(f"DEBUG: station_list 처음 10개: {self.station_list[:10]}")
        print(f"DEBUG: station_list 마지막 10개: {self.station_list[-10:]}")
        self.popup_opened = False  # 팝업 중복 방지 플래그
        self.time_popup_opened = False  # 시간표 팝업 중복 방지 플래그
        
        # 시간 정보 관련 변수 추가
        self.time_data = None
        self.load_time_data()
        
        self._init_style()
        self._init_ui()
        self._init_canvas()
        self._create_image_buttons()
        self._update_all_img_btns()

    def load_time_data(self):
        """CSV 파일에서 시간 정보를 로드합니다."""
        try:
            self.time_data = pd.read_csv('./SubwayData/Subway.csv', encoding='cp949')
            print(f"시간 데이터 로드 완료: {len(self.time_data)}개 레코드")
            
            # 역 이름별 인덱스 생성 (성능 최적화)
            self.station_index = {}
            for _, row in self.time_data.iterrows():
                stations_str = row['운행구간정거장']
                if pd.isna(stations_str):
                    continue
                
                stations = stations_str.split('+')
                for i, station_info in enumerate(stations):
                    if '-' in station_info:
                        station_code, station_full_name = station_info.split('-', 1)
                        normalized_name = station_full_name.strip().replace('역', '').strip()
                        if normalized_name not in self.station_index:
                            self.station_index[normalized_name] = []
                        self.station_index[normalized_name].append((row.name, i))
                    else:
                        normalized_name = station_info.strip().replace('역', '').strip()
                        if normalized_name not in self.station_index:
                            self.station_index[normalized_name] = []
                        self.station_index[normalized_name].append((row.name, i))
            
            print(f"역 이름 인덱스 생성 완료: {len(self.station_index)}개 역")
            
        except Exception as e:
            print(f"시간 데이터 로드 실패: {e}")
            self.time_data = None
            self.station_index = {}

    def parse_time_string(self, time_str):
        """시간 문자열을 파싱합니다. (예: '001-05:08+002-05:09')"""
        if pd.isna(time_str) or time_str == '':
            return {}
        
        times = {}
        try:
            # '+'로 분리하여 각 정거장의 시간 정보 추출
            parts = time_str.split('+')
            print(f"DEBUG: 시간 문자열 파싱 - 원본: '{time_str}'")
            print(f"DEBUG: 분리된 부분들: {parts}")
            for part in parts:
                if '-' in part:
                    station_code, time_info = part.split('-', 1)
                    # 시간 형식이 HH:MM인지 확인
                    if ':' in time_info:
                        times[station_code] = time_info
                        print(f"DEBUG: 시간 정보 추가 - 역코드: {station_code}, 시간: {time_info}")
        except Exception as e:
            print(f"시간 파싱 오류: {e}")
        
        print(f"DEBUG: 파싱된 시간 개수: {len(times)}")
        return times

    def get_station_times(self, station_name, dest_station_name=None, direction='both'):
        """특정 역의 시간표를 가져옵니다. (dest_station_name이 있으면 방향 체크)"""
        if self.time_data is None:
            with open('debug.log', 'a', encoding='utf-8') as f:
                f.write("DEBUG: time_data가 None입니다.\n")
            return []
        
        # 역 이름 정규화 (공백 제거, "역" 글자 제거)
        normalized_station_name = self.normalize_station_name(station_name)
        normalized_dest_name = self.normalize_station_name(dest_station_name) if dest_station_name else None
        
        station_times = []
        
        if normalized_dest_name:
            # 출발역과 도착역의 인덱스를 비교해서 정방향 열차만 안내
            for _, row in self.time_data.iterrows():
                stations_str = row['운행구간정거장']
                arrival_times_str = row['정거장도착시각']
                departure_times_str = row['정거장출발시각']
                if pd.isna(stations_str):
                    continue
                stations = stations_str.split('+')
                station_names = []
                for s in stations:
                    if '-' in s:
                        _, name = s.split('-', 1)
                        station_names.append(name.strip().replace('역', '').strip())
                if normalized_station_name in station_names and normalized_dest_name in station_names:
                    idx_start = station_names.index(normalized_station_name)
                    idx_end = station_names.index(normalized_dest_name)
                    if idx_start < idx_end:
                        # 정방향 열차만 안내
                        station_index = idx_start
                        arrival_times = self.parse_time_string(arrival_times_str)
                        departure_times = self.parse_time_string(departure_times_str)
                        station_code = f"{station_index+1:03d}"
                        arrival_time = arrival_times.get(station_code, '')
                        departure_time = departure_times.get(station_code, '')
                        if arrival_time or departure_time:
                            train_info = {
                                'train_id': row['열차번호'],
                                'line': row['노선명'],
                                'direction': f"{row['운행구간기점명']} → {row['운행구간종점명']}",
                                'day_type': row['요일구분'],
                                'arrival_time': arrival_time,
                                'departure_time': departure_time,
                                'speed': row['운행속도']
                            }
                            print(f"DEBUG: 선택된 열차 - 번호: {train_info['train_id']}, 방향: {train_info['direction']}, 출발시간: {train_info['departure_time']}")
                            station_times.append(train_info)
            with open('debug.log', 'a', encoding='utf-8') as f:
                f.write(f"DEBUG: 찾은 시간표 개수: {len(station_times)}\n")
            return station_times
        # 기존 로직 (도착역이 없는 경우)
        # 미리 생성된 인덱스를 사용하여 역 찾기
        if normalized_station_name in self.station_index:
            for row_idx, station_idx in self.station_index[normalized_station_name]:
                row = self.time_data.loc[row_idx]
                arrival_times_str = row['정거장도착시각']
                departure_times_str = row['정거장출발시각']
                
                # 시간 정보 파싱
                arrival_times = self.parse_time_string(arrival_times_str)
                departure_times = self.parse_time_string(departure_times_str)
                
                # 해당 역의 시간 정보 추출
                station_code = f"{station_idx+1:03d}"
                arrival_time = arrival_times.get(station_code, '')
                departure_time = departure_times.get(station_code, '')
                
                if arrival_time or departure_time:
                    station_times.append({
                        'train_id': row['열차번호'],
                        'line': row['노선명'],
                        'direction': f"{row['운행구간기점명']} → {row['운행구간종점명']}",
                        'day_type': row['요일구분'],
                        'arrival_time': arrival_time,
                        'departure_time': departure_time,
                        'speed': row['운행속도']
                    })
        else:
            with open('debug.log', 'a', encoding='utf-8') as f:
                f.write(f"DEBUG: 해당 역 이름 '{normalized_station_name}'에 대한 시간 정보를 찾을 수 없습니다.\n")
        
        with open('debug.log', 'a', encoding='utf-8') as f:
            f.write(f"DEBUG: 찾은 시간표 개수: {len(station_times)}\n")
        return station_times

    def show_time_table_popup(self, station_name, default_direction=None):
        """시간표 팝업을 표시합니다."""
        # 임시로 플래그 체크 제거 (팝업이 안 뜨는 문제 해결)
        # if self.time_popup_opened:
        #     return
        
        station_times = self.get_station_times(station_name)
        
        if not station_times:
            # 시간 정보가 없는 경우 간단한 메시지 표시
            popup = Toplevel(self.root)
            popup.title(f"{station_name} 시간표")
            popup.geometry("400x200")
            popup.configure(bg='#f8f9fa')
            
            ttk.Label(popup, text=f"{station_name}역", 
                     style='RouteBig.TLabel').pack(pady=20)
            ttk.Label(popup, text="시간 정보를 찾을 수 없습니다.", 
                     style='RouteNormal.TLabel').pack(pady=10)
            
            ttk.Button(popup, text="닫기", 
                      command=lambda: self._close_popup(popup)).pack(pady=20)
            
            self.time_popup_opened = True
            popup.protocol("WM_DELETE_WINDOW", lambda: self._close_time_popup(popup))
            return
        
        # 시간표 팝업 생성
        popup = Toplevel(self.root)
        popup.title(f"{station_name} 시간표")
        popup.geometry("900x700")
        popup.configure(bg='#f8f9fa')
        
        # 메인 프레임
        main_frame = ttk.Frame(popup, style='TFrame')
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ttk.Label(main_frame, text=f"{station_name}역 시간표", 
                               style='RouteBig.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 필터 프레임
        filter_frame = ttk.Frame(main_frame, style='TFrame')
        filter_frame.pack(fill=X, pady=(0, 10))
        
        # 요일 필터
        ttk.Label(filter_frame, text="요일:", style='RouteBold.TLabel').pack(side=LEFT, padx=(0, 5))
        day_var = StringVar(value="전체")
        day_combo = ttk.Combobox(filter_frame, textvariable=day_var, 
                                values=["전체", "평일", "토요일", "일요일"], 
                                width=10, state='normal')
        day_combo.pack(side=LEFT, padx=(0, 20))
        
        # 시간대 필터
        ttk.Label(filter_frame, text="시간대:", style='RouteBold.TLabel').pack(side=LEFT, padx=(0, 5))
        time_var = StringVar(value="전체")
        time_combo = ttk.Combobox(filter_frame, textvariable=time_var, 
                                 values=["전체", "새벽(05-07)", "오전(07-12)", "오후(12-18)", "저녁(18-24)"], 
                                 width=12, state='normal')
        time_combo.pack(side=LEFT, padx=(0, 20))
        
        # 방향 필터 추가
        direction_values = list(sorted(set([t['direction'] for t in station_times if t.get('direction')])))
        direction_values = ['전체'] + direction_values
        ttk.Label(filter_frame, text="방향:", style='RouteBold.TLabel').pack(side=LEFT, padx=(0, 5))
        direction_var = StringVar(value=default_direction if (default_direction in direction_values) else "전체")
        direction_combo = ttk.Combobox(filter_frame, textvariable=direction_var, values=direction_values, width=20, state='normal')
        direction_combo.pack(side=LEFT, padx=(0, 20))
        
        # 스크롤 가능한 프레임
        canvas = Canvas(main_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 시간표 헤더
        header_frame = ttk.Frame(scrollable_frame, style='TFrame')
        header_frame.pack(fill=X, pady=(0, 10))
        
        headers = ['열차번호', '노선', '방향', '요일', '도착시간', '출발시간', '속도']
        for i, header in enumerate(headers):
            ttk.Label(header_frame, text=header, style='RouteBold.TLabel', 
                     width=12 if i < 3 else 10).grid(row=0, column=i, padx=2, pady=5)
        
        # 필터링 함수
        def filter_times():
            # 기존 시간표 데이터 제거
            for widget in scrollable_frame.winfo_children():
                if widget != header_frame:
                    widget.destroy()
            
            # 필터 조건
            selected_day = day_var.get()
            selected_time = time_var.get()
            selected_direction = direction_var.get()
            
            # 시간대별 시간 범위
            time_ranges = {
                "새벽(05-07)": ("05:00", "07:00"),
                "오전(07-12)": ("07:00", "12:00"),
                "오후(12-18)": ("12:00", "18:00"),
                "저녁(18-24)": ("18:00", "24:00")
            }
            
            filtered_times = []
            for time_info in station_times:
                # 요일 필터
                if selected_day != "전체" and time_info['day_type'] != selected_day:
                    continue
                # 방향 필터
                if selected_direction != "전체" and time_info['direction'] != selected_direction:
                    continue
                # 시간대 필터
                if selected_time != "전체":
                    time_range = time_ranges.get(selected_time)
                    if time_range:
                        start_time, end_time = time_range
                        arrival_time = time_info['arrival_time']
                        departure_time = time_info['departure_time']
                        
                        # 도착시간이나 출발시간이 선택된 시간대에 포함되는지 확인
                        time_in_range = False
                        if arrival_time and start_time <= arrival_time <= end_time:
                            time_in_range = True
                        if departure_time and start_time <= departure_time <= end_time:
                            time_in_range = True
                        
                        if not time_in_range:
                            continue
                
                filtered_times.append(time_info)
            
            # 필터링된 시간표 표시
            for i, time_info in enumerate(filtered_times):
                row_frame = ttk.Frame(scrollable_frame, style='TFrame')
                row_frame.pack(fill=X, pady=2)
                
                ttk.Label(row_frame, text=time_info['train_id'], 
                         style='RouteNormal.TLabel', width=12).grid(row=0, column=0, padx=2, pady=3)
                ttk.Label(row_frame, text=time_info['line'], 
                         style='RouteNormal.TLabel', width=12).grid(row=0, column=1, padx=2, pady=3)
                ttk.Label(row_frame, text=time_info['direction'], 
                         style='RouteNormal.TLabel', width=12).grid(row=0, column=2, padx=2, pady=3)
                ttk.Label(row_frame, text=time_info['day_type'], 
                         style='RouteNormal.TLabel', width=10).grid(row=0, column=3, padx=2, pady=3)
                ttk.Label(row_frame, text=time_info['arrival_time'], 
                         style='RouteNormal.TLabel', width=10).grid(row=0, column=4, padx=2, pady=3)
                ttk.Label(row_frame, text=time_info['departure_time'], 
                         style='RouteNormal.TLabel', width=10).grid(row=0, column=5, padx=2, pady=3)
                ttk.Label(row_frame, text=time_info['speed'], 
                         style='RouteNormal.TLabel', width=10).grid(row=0, column=6, padx=2, pady=3)
        
        # 필터 버튼
        filter_btn = ttk.Button(filter_frame, text="필터 적용", command=filter_times)
        filter_btn.pack(side=LEFT, padx=(0, 10))
        
        # 초기 시간표 표시
        filter_times()
        
        # 스크롤바와 캔버스 배치
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 닫기 버튼
        ttk.Button(main_frame, text="닫기", 
                  command=lambda: self._close_time_popup(popup)).pack(pady=20)
        
        self.time_popup_opened = True
        popup.protocol("WM_DELETE_WINDOW", lambda: self._close_time_popup(popup))

    def _init_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('맑은 고딕', 11, 'bold'), foreground='#222', background='#e0e0e0', borderwidth=0, focusthickness=3, focuscolor='none', padding=8, anchor='center', justify='center')
        style.map('TButton', background=[('active', '#b3e5fc'), ('pressed', '#81d4fa')])
        style.layout('TbButton', style.layout('TButton'))
        style.configure('TbButton', font=('Arial', 18, 'bold'), foreground='#222', background='#e0e0e0', borderwidth=0, focusthickness=3, focuscolor='none', padding=6, anchor='n', justify='center')
        style.map('TbButton', background=[('active', '#b3e5fc'), ('pressed', '#81d4fa')])
        style.configure('TLabel', font=('맑은 고딕', 12), background='#f8f9fa', foreground='#222')
        style.configure('TFrame', background='#f8f9fa')
        style.configure('TCombobox', font=('맑은 고딕', 11), background='white', fieldbackground='white')
        # 추가: 경로 안내용 스타일
        style.configure('RouteBig.TLabel', font=('맑은 고딕', 16, 'bold'), background='#f8f9fa', foreground='#222')
        style.configure('RouteBold.TLabel', font=('맑은 고딕', 12, 'bold'), background='#f8f9fa', foreground='#222')
        style.configure('RouteNormal.TLabel', font=('맑은 고딕', 12), background='#f8f9fa', foreground='#222')
        # 추가: 화살표 버튼 정사각형 스타일
        style.configure('Arrow.TButton', font=('Arial', 18, 'bold'), padding=0, anchor='center')
        # 추가: 동그라미 버튼 스타일
        style.configure('Circle.TButton', font=('Arial', 18, 'bold'), foreground='#222', background='#e0e0e0', borderwidth=0, focusthickness=3, focuscolor='none', padding=0, anchor='center', relief='flat')
        style.map('Circle.TButton', background=[('active', '#b3e5fc'), ('pressed', '#81d4fa')])
        self.root.configure(bg="#f8f9fa")

    def _init_ui(self):
        self.top_frame = ttk.Frame(self.root, style='TFrame')
        self.top_frame.pack(side=TOP, fill=X, pady=8)
        
        # 지도 선택 프레임 추가
        self.map_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.map_frame.pack(side=TOP, fill=X, pady=4)
        ttk.Label(self.map_frame, text="지도 선택:", style='TLabel', font=('맑은 고딕', 12, 'bold')).pack(side=LEFT, padx=(0, 5))
        
        # 지도 선택을 위한 매핑 딕셔너리
        self.map_options = {
            "부산권": "busan_subway.png",
            "수도권": "sudo_subway.png"
        }
        self.map_var = StringVar(value="부산권")
        self.map_combo = ttk.Combobox(self.map_frame, textvariable=self.map_var, 
                                     values=list(self.map_options.keys()), 
                                     font=('맑은 고딕', 11), width=15, state='readonly')
        self.map_combo.pack(side=LEFT, padx=(0, 10))
        self.map_combo.bind('<<ComboboxSelected>>', self.on_map_changed)
        
        # 출발역/도착역 선택 프레임
        self.station_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.station_frame.pack(side=TOP, fill=X, expand=True, pady=8)
        
        # 출발역 선택
        self.start_frame = ttk.Frame(self.station_frame, style='TFrame')
        self.start_frame.grid(row=0, column=0, padx=4, sticky='e')
        ttk.Label(self.start_frame, text="출발역", style='TLabel', font=('맑은 고딕', 16, 'bold')).pack(side=TOP, pady=(0, 5))
        self.start_var = StringVar()
        self.start_combo = ttk.Combobox(self.start_frame, textvariable=self.start_var, values=self.station_list, 
                                       font=('맑은 고딕', 11), width=20, state='normal')
        self.start_combo.pack(side=TOP, fill=X)
        self.start_combo.bind('<<ComboboxSelected>>', self.on_start_station_selected)
        self.start_combo.bind('<KeyRelease>', self.on_start_search)
        self.start_combo.bind('<KeyPress-Return>', self._open_combo_dropdown)
        
        # 화살표 (동그라미 Canvas 버튼)
        self.arrow_canvas = Canvas(self.station_frame, width=48, height=48, highlightthickness=0, bg='#f8f9fa')
        self.arrow_canvas.grid(row=0, column=1, padx=50, pady=8)
        self.arrow_circle = self.arrow_canvas.create_oval(2, 2, 46, 46, fill='#e0e0e0', outline='#b3e5fc', width=2)
        self.arrow_text = self.arrow_canvas.create_text(24, 24, text='➔', font=('Arial', 18, 'bold'), fill='#222')
        self.arrow_canvas.bind('<Button-1>', lambda e: self.show_route_popup())
        
        # 도착역 선택
        self.end_frame = ttk.Frame(self.station_frame, style='TFrame')
        self.end_frame.grid(row=0, column=2, padx=4, sticky='w')
        ttk.Label(self.end_frame, text="도착역", style='TLabel', font=('맑은 고딕', 16, 'bold')).pack(side=TOP, pady=(0, 5))
        self.end_var = StringVar()
        self.end_combo = ttk.Combobox(self.end_frame, textvariable=self.end_var, values=self.station_list, 
                                     font=('맑은 고딕', 11), width=20, state='normal')
        self.end_combo.pack(side=TOP, fill=X)
        self.end_combo.bind('<<ComboboxSelected>>', self.on_end_station_selected)
        self.end_combo.bind('<KeyRelease>', self.on_end_search)
        self.end_combo.bind('<KeyPress-Return>', self._open_combo_dropdown)
        # 가운데 정렬을 위한 column weight 설정
        self.station_frame.grid_columnconfigure(0, weight=1)
        self.station_frame.grid_columnconfigure(1, weight=0)
        self.station_frame.grid_columnconfigure(2, weight=1)

        # 길 찾기 버튼

        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=2)
        self.top_frame.grid_columnconfigure(2, weight=1)

        # 경로 탐색 모드 선택 라디오버튼 추가
        self.route_mode_var = StringVar(value='shortest')
        mode_frame = ttk.Frame(self.top_frame, style='TFrame')
        mode_frame.pack(side=TOP, pady=2)
        ttk.Radiobutton(mode_frame, text='최단 경로', variable=self.route_mode_var, value='shortest').pack(side=LEFT, padx=4)
        ttk.Radiobutton(mode_frame, text='최소 환승', variable=self.route_mode_var, value='min_transfer').pack(side=LEFT, padx=4)

    def _init_canvas(self):
        self.current_image_path = "./Image/busan_subway.png"
        self.img = Image.open(self.current_image_path)
        self.canvas = Canvas(self.root, width=900, height=600, bg='white', highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.img_id = self.canvas.create_image(0, 0, anchor=CENTER, image=self.img_tk)
        self.root.update()
        self._place_image_center()
        # 확대/축소 버튼 (동그라미 Canvas 버튼)
        self.plus_canvas = Canvas(self.root, width=48, height=48, highlightthickness=0, bg='#f8f9fa')
        self.minus_canvas = Canvas(self.root, width=48, height=48, highlightthickness=0, bg='#f8f9fa')
        self.plus_circle = self.plus_canvas.create_oval(2, 2, 46, 46, fill='#e0e0e0', outline='#b3e5fc', width=2)
        self.plus_text = self.plus_canvas.create_text(24, 24, text='+', font=('Arial', 18, 'bold'), fill='#222')
        self.minus_circle = self.minus_canvas.create_oval(2, 2, 46, 46, fill='#e0e0e0', outline='#b3e5fc', width=2)
        self.minus_text = self.minus_canvas.create_text(24, 24, text='-', font=('Arial', 18, 'bold'), fill='#222')
        self.plus_canvas.place(relx=1.0, rely=1.0, x=-30, y=-120, anchor='se')
        self.minus_canvas.place(relx=1.0, rely=1.0, x=-30, y=-60, anchor='se')
        self.plus_canvas.bind('<Button-1>', lambda e: self.zoom_in())
        self.minus_canvas.bind('<Button-1>', lambda e: self.zoom_out())
        # 이벤트 바인딩
        self.root.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind('<ButtonPress-1>', self.on_button_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_button_release)
        self.canvas.bind('<Configure>', self.on_configure)
        # 역 버튼 클릭/드래그 구분 바인딩
        self.canvas.tag_bind('invisible_btn', '<ButtonPress-1>', self.on_btn_press)
        self.canvas.tag_bind('invisible_btn', '<ButtonRelease-1>', self.on_btn_release)
        
        # 마우스 클릭 좌표 출력은 root에만 바인딩 (캔버스 드래그와 분리)
        self.root.bind("<ButtonRelease-1>", get_mouse_click_coor)

    def _create_image_buttons(self):
        for x, y, text, line in BUTTON_COORDS:
            btn_id = self.canvas.create_oval(0, 0, 20, 20, outline='', fill='', tags='invisible_btn')
            self.img_btns.append((text, x, y, line))
            self.img_btn_ids.append(btn_id)

    def _update_all_img_btns(self):
        w, h = self.img.size
        img_cx, img_cy = self.canvas.coords(self.img_id)
        for idx, (_, bx, by, _) in enumerate(self.img_btns):
            dx = (bx - w / 2) * self.img_scale
            dy = (by - h / 2) * self.img_scale
            btn_canvas_x = img_cx + dx
            btn_canvas_y = img_cy + dy
            self.canvas.coords(self.img_btn_ids[idx], btn_canvas_x-10, btn_canvas_y-10, btn_canvas_x+10, btn_canvas_y+10)

    def _get_center_coords(self, img_w, img_h):
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()
        x = c_w // 2
        y = c_h // 2
        return x, y

    def _place_image_center(self):
        w, h = self.img.size
        new_w = int(w * self.img_scale)
        new_h = int(h * self.img_scale)
        x, y = self._get_center_coords(new_w, new_h)
        self.canvas.coords(self.img_id, x, y)

    def update_image(self, center_x=None, center_y=None, scale_from=None):
        w, h = self.img.size
        new_w = int(w * self.img_scale)
        new_h = int(h * self.img_scale)
        resized = self.img.resize((new_w, new_h), Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(resized)
        self.canvas.itemconfig(self.img_id, image=self.img_tk)
        self.canvas.config(scrollregion=(0, 0, new_w, new_h))
        if center_x is not None and center_y is not None and scale_from is not None:
            img_cx, img_cy = self.canvas.coords(self.img_id)
            new_img_cx = center_x - (center_x - img_cx) * (self.img_scale / scale_from)
            new_img_cy = center_y - (center_y - img_cy) * (self.img_scale / scale_from)
            self.canvas.coords(self.img_id, new_img_cx, new_img_cy)
        else:
            x, y = self._get_center_coords(new_w, new_h)
            self.canvas.coords(self.img_id, x, y)
        self._update_all_img_btns()

    # --- 이벤트 핸들러 ---
    def on_configure(self, event):
        w, h = self.img.size
        new_w = int(w * self.img_scale)
        new_h = int(h * self.img_scale)
        x, y = self._get_center_coords(new_w, new_h)
        self.canvas.coords(self.img_id, x, y)
        self._update_all_img_btns()

    def on_mousewheel(self, event):
        old_scale = self.img_scale
        if event.delta > 0:
            self.img_scale = min(self.img_max_scale, self.img_scale * 1.1)
        else:
            self.img_scale = max(self.img_min_scale, self.img_scale * 0.9)
        canvas_x = event.x
        canvas_y = event.y
        self.update_image(center_x=canvas_x, center_y=canvas_y, scale_from=old_scale)

    def on_button_press(self, event):
        global is_dragging_global, mouse_start_x, mouse_start_y
        self.img_drag_start_x = event.x
        self.img_drag_start_y = event.y
        mouse_start_x = event.x
        mouse_start_y = event.y
        is_dragging_global = False  # 드래그 시작 시 초기화

    def on_drag(self, event):
        global is_dragging_global
        # 드래그 상태로 설정
        is_dragging_global = True
        
        dx = event.x - self.img_drag_start_x
        dy = event.y - self.img_drag_start_y
        self.canvas.move(self.img_id, dx, dy)
        self.img_drag_start_x = event.x
        self.img_drag_start_y = event.y
        self._update_all_img_btns()

    def on_button_release(self, event):
        global is_dragging_global, mouse_start_x, mouse_start_y
        
        # 실제로 드래그였는지 클릭이었는지 판단
        dx = abs(event.x - mouse_start_x)
        dy = abs(event.y - mouse_start_y)
        
        if dx > 5 or dy > 5:
            # 드래그였음 - 좌표 출력하지 않음
            is_dragging_global = True
        else:
            # 클릭이었음 - 좌표 출력 허용
            is_dragging_global = False

    def zoom_in(self):
        old_scale = self.img_scale
        self.img_scale = min(self.img_max_scale, self.img_scale * 1.1)
        c_w = self.canvas.winfo_width() // 2
        c_h = self.canvas.winfo_height() // 2
        self.update_image(center_x=c_w, center_y=c_h, scale_from=old_scale)

    def zoom_out(self):
        old_scale = self.img_scale
        self.img_scale = max(self.img_min_scale, self.img_scale * 0.9)
        c_w = self.canvas.winfo_width() // 2
        c_h = self.canvas.winfo_height() // 2
        self.update_image(center_x=c_w, center_y=c_h, scale_from=old_scale)

    def on_btn_press(self, event):
        # 어떤 버튼 영역에 눌렀는지 확인
        self.btn_click_candidate_idx = None
        for idx, btn_id in enumerate(self.img_btn_ids):
            coords = self.canvas.coords(btn_id)
            if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                self.btn_click_start_x = event.x
                self.btn_click_start_y = event.y
                self.btn_click_candidate_idx = idx
                break

    def on_btn_release(self, event):
        if self.btn_click_candidate_idx is None:
            return
        dx = event.x - self.btn_click_start_x
        dy = event.y - self.btn_click_start_y
        if abs(dx) < 5 and abs(dy) < 5:
            # 클릭으로 간주, 팝업 실행
            station, _, _, line = self.img_btns[self.btn_click_candidate_idx]
            self.show_station_select_popup(station, line)
        # 드래그면 아무 동작 안 함
        self.btn_click_candidate_idx = None

    # --- 팝업 및 상태 업데이트 ---
    def _close_popup(self, popup):
        self.popup_opened = False
        popup.destroy()
    
    def _close_time_popup(self, popup):
        self.time_popup_opened = False
        popup.destroy()

    def show_station_select_popup(self, station, line):
        if self.popup_opened:
            return
        self.popup_opened = True
        popup = Toplevel(self.root)
        popup.title(f"{station}역 선택")
        popup.geometry("380x180")
        popup.configure(bg='#f8f9fa')
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        ttk.Label(popup, text=f"{station}역 ({line}) 을 출발/도착역으로 설정", style='TLabel').pack(pady=16)
        
        # 시간표 버튼 추가
        time_btn_frame = ttk.Frame(popup, style='TFrame')
        time_btn_frame.pack(pady=8)
        ttk.Button(time_btn_frame, text="시간표 보기", 
                  command=lambda: self.show_time_table_popup(station)).pack(side=LEFT, padx=5)
        
        btn_frame = ttk.Frame(popup, style='TFrame')
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="출발역으로", style='TButton', command=lambda: self.set_start_station(station, popup)).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="도착역으로", style='TButton', command=lambda: self.set_end_station(station, popup)).pack(side=RIGHT, padx=10)
        popup.protocol("WM_DELETE_WINDOW", lambda: self._close_popup(popup))

    def set_start_station(self, station, popup):
        self.start = station
        self.start_var.set(station)
        self._close_popup(popup)

    def set_end_station(self, station, popup):
        self.end = station
        self.end_var.set(station)
        self._close_popup(popup)

    def on_start_station_selected(self, event):
        selected = self.start_var.get()
        if selected in self.station_list:
            self.start = selected

    def on_end_station_selected(self, event):
        selected = self.end_var.get()
        if selected in self.station_list:
            self.end = selected

    def on_start_search(self, event):
        search_term = self.start_var.get().lower()
        if search_term:
            filtered_stations = [station for station in self.station_list if search_term in station.lower()]
            self.start_combo['values'] = filtered_stations
        else:
            self.start_combo['values'] = self.station_list

    def on_end_search(self, event):
        search_term = self.end_var.get().lower()
        if search_term:
            filtered_stations = [station for station in self.station_list if search_term in station.lower()]
            self.end_combo['values'] = filtered_stations
        else:
            self.end_combo['values'] = self.station_list

    def _open_combo_dropdown(self, event):
        # 엔터키로 콤보박스 드롭다운 열기
        event.widget.event_generate('<Down>')

    # --- 경로 탐색 및 안내 ---
    def find_shortest_route_with_transfer(self, start, end):
        from collections import deque
        station_to_line = {text: line for _, _, text, line in BUTTON_COORDS}
        
        # 디버깅 출력 추가
        print(f"DEBUG: 경로 찾기 시작 - 출발: {start}, 도착: {end}")
        
        queue = deque()
        visited = dict()  # (역, 호선): 최소 환승횟수
        for line in station_to_line.get(start, '').split('/'):
            queue.append((start, line, [start], 0, 0))
            visited[(start, line)] = 0
        min_dist = float('inf')
        min_route = []
        min_transfer = float('inf')
        while queue:
            curr, curr_line, path, transfer, dist = queue.popleft()
            if curr == end:
                if dist < min_dist or (dist == min_dist and transfer < min_transfer):
                    min_dist = dist
                    min_route = path[:]
                    min_transfer = transfer
                    print(f"DEBUG: 경로 발견 - {path}")
                continue
            for next_station in SUBWAY[curr]:
                next_lines = station_to_line.get(next_station, '').split('/')
                for next_line in next_lines:
                    next_transfer = transfer + (0 if next_line == curr_line else 1)
                    state = (next_station, next_line)
                    if state in visited and visited[state] <= next_transfer:
                        continue
                    visited[state] = next_transfer
                    queue.append((next_station, next_line, path + [next_station], next_transfer, dist + 1))
        if not min_route or min_dist == float('inf') or min_transfer == float('inf'):
            print(f"DEBUG: 경로를 찾을 수 없습니다.")
            return [], 0, 0
        print(f"DEBUG: 최종 경로: {min_route}, 거리: {min_dist}, 환승: {min_transfer}")
        return min_route, min_dist, min_transfer

    def show_route_popup(self):
        if self.popup_opened:
            return
        # 모든 역 버튼을 기본 상태(비활성/비강조)로 초기화
        for btn_id in self.img_btn_ids:
            self.canvas.itemconfig(btn_id, fill='', outline='')
        # 콤보박스에 입력된 값도 우선 반영
        start_input = self.start_var.get()
        end_input = self.end_var.get()
        start_valid = start_input in self.station_list
        end_valid = end_input in self.station_list
        
        # 디버깅 출력 추가
        print(f"DEBUG: 입력된 출발역: '{start_input}', 유효성: {start_valid}")
        print(f"DEBUG: 입력된 도착역: '{end_input}', 유효성: {end_valid}")
        print(f"DEBUG: self.start: '{self.start}', self.end: '{self.end}'")
        
        if start_valid:
            self.start = start_input
        if end_valid:
            self.end = end_input
            
        print(f"DEBUG: 최종 설정된 출발역: '{self.start}', 도착역: '{self.end}'")
        
        error_msg = None
        if not start_input or not end_input:
            error_msg = '출발역과 도착역을 모두 입력하세요.'
        elif not start_valid and not end_valid:
            error_msg = '출발역과 도착역이 모두 올바르지 않습니다. 다시 입력해 주세요.'
        elif not start_valid:
            error_msg = '출발역이 올바르지 않습니다. 다시 입력해 주세요.'
        elif not end_valid:
            error_msg = '도착역이 올바르지 않습니다. 다시 입력해 주세요.'
        if error_msg:
            self.popup_opened = True
            popup = Toplevel(self.root)
            popup.title('경로 안내')
            popup.configure(bg='#f8f9fa')
            ttk.Label(popup, text=error_msg, style='TLabel').pack(padx=20, pady=20)
            ttk.Button(popup, text='확인', style='TButton', command=lambda: self._close_popup(popup)).pack(pady=10)
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            popup.protocol("WM_DELETE_WINDOW", lambda: self._close_popup(popup))
            return
        # --- 경로 탐색 분기 ---
        route = []
        dist = 0
        transfer_count = 0
        if self.route_mode_var.get() == 'shortest':
            route, dist, transfer_count = self.find_shortest_route_with_transfer(self.start, self.end)
        else:
            route, dist, transfer_count = self.find_min_transfer_route(self.start, self.end)
        # 경로가 없으면 안내만 하고 종료
        if not route:
            self.popup_opened = True
            popup = Toplevel(self.root)
            popup.title('경로 안내')
            popup.configure(bg='#f8f9fa')
            ttk.Label(popup, text='경로를 찾을 수 없습니다.', style='TLabel').pack(padx=20, pady=20)
            ttk.Button(popup, text='확인', style='TButton', command=lambda: self._close_popup(popup)).pack(pady=10)
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            popup.protocol("WM_DELETE_WINDOW", lambda: self._close_popup(popup))
            return
        # --- 경로 버튼 강조 및 visible 처리 ---
        if route:
            for idx, (station, _, _, _) in enumerate(self.img_btns):
                if station in route:
                    self.canvas.itemconfig(self.img_btn_ids[idx], fill='red', outline='black', width=3)
                else:
                    self.canvas.itemconfig(self.img_btn_ids[idx], fill='', outline='')
        # --- 여기서부터 경로 필터링 ---
        transfer_stations = [name for name, adj in SUBWAY.items() if len(adj) >= 3]
        # BUTTON_COORDS에서 역-호선 매핑 생성
        station_to_line = {text: line for _, _, text, line in BUTTON_COORDS}
        if route:
            def get_lines(station):
                return station_to_line.get(station, "").split('/')
            # 환승역만 추출 (출발, 도착 포함, 실제 환승이 일어나는 경우만)
            filtered_nodes = [route[0]]
            for i in range(1, len(route)-1):
                prev_station = route[i-1]
                curr_station = route[i]
                next_station = route[i+1]
                if curr_station in transfer_stations:
                    prev_lines = set(get_lines(prev_station))
                    curr_lines = set(get_lines(curr_station))
                    next_lines = set(get_lines(next_station))
                    prev_curr = prev_lines & curr_lines
                    curr_next = curr_lines & next_lines
                    # 환승 판정: 두 교집합이 모두 존재하고, 서로 겹치지 않을 때
                    if prev_curr and curr_next and not (prev_curr & curr_next):
                        filtered_nodes.append(curr_station)
            if len(route) > 1:
                filtered_nodes.append(route[-1])
            # 구간별 거리 계산
            segs = []
            seg_start_idx = 0
            for i in range(1, len(filtered_nodes)):
                seg_end = filtered_nodes[i]
                seg_dist = 0
                for j in range(seg_start_idx, len(route)):
                    if route[j] == seg_end:
                        break
                    seg_dist += SUBWAY[route[j]][route[j+1]]
                segs.append((filtered_nodes[i-1], seg_dist, seg_end))
                seg_start_idx = route.index(seg_end)
            # total_dist 선언 위치 이동
            total_dist = self.routing[self.end]['shortestDist']
            # 경로 안내 라인(구간별로 Label 분리, 환승역에서만 호선명 표시)
            route_str = filtered_nodes[0]
            self.popup_opened = True
            popup = Toplevel(self.root)
            popup.title('경로 안내')
            popup.configure(bg='#f8f9fa')
            bold_font = font.Font(self.root, family='맑은 고딕', size=12, weight='bold')
            normal_font = font.Font(self.root, family='맑은 고딕', size=12)
            # [출발역 → 도착역] 안내 (출발/도착만 크게)
            route_frame = ttk.Frame(popup, style='TFrame')
            route_frame.pack(pady=5)
            ttk.Label(route_frame, text='[', style='RouteNormal.TLabel').pack(side=LEFT)
            ttk.Label(route_frame, text=f'{self.start}', style='RouteBig.TLabel').pack(side=LEFT)
            ttk.Label(route_frame, text=' → ', style='RouteNormal.TLabel').pack(side=LEFT)
            ttk.Label(route_frame, text=f'{self.end}', style='RouteBig.TLabel').pack(side=LEFT)
            ttk.Label(route_frame, text=']', style='RouteNormal.TLabel').pack(side=LEFT)
            # 경로 안내 라인(구간별로 Label 분리)
            path_frame = ttk.Frame(popup, style='TFrame')
            path_frame.pack(pady=5)
            # 출발역
            prev_line = station_to_line.get(filtered_nodes[0], "")
            # 출발역에 호선 정보 표시(선택적)
            if filtered_nodes[0] in transfer_stations:
                label_text = f"{filtered_nodes[0]}({station_to_line.get(filtered_nodes[0], '')})"
            else:
                label_text = filtered_nodes[0]
            ttk.Label(path_frame, text=label_text, style='RouteBold.TLabel').pack(side=LEFT)
            for prev, seg_dist, nxt in segs:
                curr_line = station_to_line.get(nxt, "")
                # 환승역이면 항상 호선 정보 출력
                if nxt in transfer_stations:
                    label_text = f"{nxt}({curr_line})"
                else:
                    label_text = nxt
                # 환승역에서만, 앞뒤 호선이 다를 때만 호선명 출력하는 기존 라벨은 삭제
                ttk.Label(path_frame, text=f' → ({seg_dist}개 역) → ', style='RouteNormal.TLabel').pack(side=LEFT)
                ttk.Label(path_frame, text=label_text, style='RouteBold.TLabel').pack(side=LEFT)
                prev_line = curr_line
            # 기존의 ttk.Label(popup, text=f'   {route_str}   ', style='TLabel').pack(pady=5) 부분 삭제
            # 굵게 표시할 부분만 Label 분리
            def count_transfers_precise(route, station_to_line):
                if not route or len(route) < 2:
                    return 0
                prev_lines = set(station_to_line.get(route[0], '').split('/'))
                transfer_count = 0
                current_lines = prev_lines
                for i in range(1, len(route)):
                    curr_lines = set(station_to_line.get(route[i], '').split('/'))
                    intersection = current_lines & curr_lines
                    if intersection:
                        current_lines = intersection
                    else:
                        transfer_count += 1
                        current_lines = curr_lines
                return transfer_count

            actual_total_dist = len(route) - 1 if route else 0
            # filtered_nodes: [출발역, 환승1, 환승2, ..., 도착역]
            num_transfers_by_nodes = max(0, len(filtered_nodes) - 2)
            info_frame = ttk.Frame(popup, style='TFrame')
            info_frame.pack(pady=5)
            if self.route_mode_var.get() == 'min_transfer':
                # 최소 환승 모드: find_min_transfer_route에서 반환한 transfer_count만 사용
                Label(info_frame, text=f"{self.start}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="역에서 ", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text=f"{self.end}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="역까지의 최소 환승 경로는 총 ", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text=f"{num_transfers_by_nodes}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="회 환승, ", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text=f"{actual_total_dist}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="개의 역을 지나야 합니다.", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
            else:
                # 최단 경로의 환승 횟수 계산 (실제 환승만 카운트, 교집합 방식 개선)
                transfer_count = count_transfers_precise(route, station_to_line)
                Label(info_frame, text=f"{self.start}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="역에서 ", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text=f"{self.end}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="역까지의 최단 경로는 총 ", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text=f"{num_transfers_by_nodes}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="회 환승, ", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text=f"{actual_total_dist}", font=bold_font, bg='#f8f9fa').pack(side=LEFT)
                Label(info_frame, text="개의 역을 지나야 합니다.", font=normal_font, bg='#f8f9fa').pack(side=LEFT)
            # 버튼 프레임 추가
            button_frame = ttk.Frame(popup, style='TFrame')
            button_frame.pack(pady=10)
            
            # 시간표 보기 버튼 추가
            def get_next_train_direction(station):
                input_hour = hour_var.get()
                input_min = min_var.get()
                input_time = f"{input_hour}:{input_min}"
                input_day = day_var.get()
                try:
                    input_dt = datetime.strptime(input_time, '%H:%M')
                except Exception:
                    return None
                times = self.get_station_times(station, self.end if station == self.start else self.start)
                filtered_times = [t for t in times if t['day_type'] == input_day]
                unique_times = {}
                for t in filtered_times:
                    if t['departure_time'] not in unique_times:
                        unique_times[t['departure_time']] = t
                valid_times = list(unique_times.values())
                valid_times.sort(key=lambda t: datetime.strptime(t['departure_time'], '%H:%M'))
                for t in valid_times:
                    if datetime.strptime(t['departure_time'], '%H:%M') >= input_dt:
                        return t['direction']
                return None

            ttk.Button(button_frame, text='시간표 보기', style='TButton', 
                      command=lambda: self.show_time_table_popup(self.start, get_next_train_direction(self.start))).pack(side=LEFT, padx=5)
            
            # 시간 입력 및 다음 열차 안내 프레임 추가
            time_frame = ttk.Frame(popup, style='TFrame')
            time_frame.pack(pady=10)
            # 시간 콤보박스 분리 (시/분)
            hour_options = [f"{h:02d}" for h in range(5, 24)]
            min_options = [f"{m:02d}" for m in range(0, 60)]
            hour_var = StringVar()
            min_var = StringVar()
            hour_combo = ttk.Combobox(time_frame, textvariable=hour_var, values=hour_options, width=4, state='normal')
            min_combo = ttk.Combobox(time_frame, textvariable=min_var, values=min_options, width=4, state='normal')
            hour_combo.set(hour_options[0])
            min_combo.set(min_options[0])
            ttk.Label(time_frame, text='출발 시각:', style='RouteNormal.TLabel').pack(side=LEFT, padx=5)
            hour_combo.pack(side=LEFT)
            hour_combo.bind('<Return>', lambda e: show_next_train())
            ttk.Label(time_frame, text='시', style='RouteNormal.TLabel').pack(side=LEFT)
            min_combo.pack(side=LEFT)
            min_combo.bind('<Return>', lambda e: show_next_train())
            ttk.Label(time_frame, text='분', style='RouteNormal.TLabel').pack(side=LEFT, padx=(0,5))
            # 요일 콤보박스
            day_options = ["평일", "토요일", "일요일"]
            day_var = StringVar()
            day_combo = ttk.Combobox(time_frame, textvariable=day_var, values=day_options, width=8, state='normal')
            day_combo.set(day_options[0])
            day_combo.bind('<Return>', lambda e: show_next_train())
            ttk.Label(time_frame, text='요일 선택:', style='RouteNormal.TLabel').pack(side=LEFT, padx=5)
            day_combo.pack(side=LEFT, padx=5)
            
            def show_next_train():
                input_hour = hour_var.get()
                input_min = min_var.get()
                input_time = f"{input_hour}:{input_min}"
                input_day = day_var.get()
                try:
                    input_dt = datetime.strptime(input_time, '%H:%M')
                except Exception as e:
                    result_var.set('시간 형식이 올바르지 않습니다. (예: 08:30)')
                    return
                # 경로 및 구간 분리
                route, dist, transfer_count = (self.find_shortest_route_with_transfer(self.start, self.end)
                                               if self.route_mode_var.get() == 'shortest'
                                               else self.find_min_transfer_route(self.start, self.end))
                if not route or len(route) < 2:
                    result_var.set('경로를 찾을 수 없습니다.')
                    return
                # BUTTON_COORDS에서 역-호선 매핑
                station_to_line = {text: line for _, _, text, line in BUTTON_COORDS}
                # 구간 분리 (호선이 바뀌는 지점마다)
                segments = []  # [(start, end, line)]
                curr_line = None
                seg_start = route[0]
                for i in range(1, len(route)):
                    prev_station = route[i-1]
                    curr_station = route[i]
                    prev_lines = set(station_to_line.get(prev_station, '').split('/'))
                    curr_lines = set(station_to_line.get(curr_station, '').split('/'))
                    common_lines = prev_lines & curr_lines
                    if common_lines:
                        next_line = list(common_lines)[0]  # 교집합이 있으면 그 중 하나 선택
                    else:
                        next_line = station_to_line.get(curr_station, '').split('/')[0]
                    if curr_line is None:
                        curr_line = next_line
                    if next_line != curr_line:
                        segments.append((seg_start, prev_station, curr_line))
                        seg_start = prev_station
                        curr_line = next_line
                segments.append((seg_start, route[-1], curr_line))
                # 환승이 없는 경우(구간 1개)만 기존 직통 안내, 2개 이상이면 환승 안내
                if len(segments) == 1:
                    # 기존 직통 안내
                    times = self.get_station_times(self.start, self.end)
                    filtered_times = [t for t in times if t['day_type'] == input_day]
                    unique_times = {}
                    for t in filtered_times:
                        if t['departure_time'] not in unique_times:
                            unique_times[t['departure_time']] = t
                    valid_times = list(unique_times.values())
                    valid_times.sort(key=lambda t: datetime.strptime(t['departure_time'], '%H:%M'))
                    next_train = None
                    for t in valid_times:
                        if datetime.strptime(t['departure_time'], '%H:%M') >= input_dt:
                            next_train = t
                            break
                    if next_train:
                        # 도착역 도착시각 구하기 (정확히 도착역 기준)
                        arrival_time = ''
                        try:
                            row = self.time_data[(self.time_data['열차번호'] == next_train['train_id']) &
                                                 (self.time_data['노선명'] == next_train['line']) &
                                                 (self.time_data['운행구간기점명'] + ' → ' + self.time_data['운행구간종점명'] == next_train['direction']) &
                                                 (self.time_data['요일구분'] == next_train['day_type'])].iloc[0]
                            stations_str = row['운행구간정거장']
                            arrival_times_str = row['정거장도착시각']
                            stations = [s.split('-', 1)[1].strip().replace('역', '').strip() if '-' in s else s.strip().replace('역', '').strip() for s in stations_str.split('+')]
                            if self.end.strip().replace('역', '').strip() in stations:
                                idx = stations.index(self.end.strip().replace('역', '').strip())
                                arrival_times = self.parse_time_string(arrival_times_str)
                                station_code = f"{idx+1:03d}"
                                arrival_time = arrival_times.get(station_code, '')
                        except Exception as e:
                            arrival_time = ''
                        # 소요시간 계산 추가
                        travel_time = None
                        if arrival_time:
                            try:
                                dep_dt = datetime.strptime(next_train['departure_time'], '%H:%M')
                                arr_dt = datetime.strptime(arrival_time, '%H:%M')
                                # 도착이 출발보다 빠르면(자정 넘김) 하루 더함
                                if arr_dt < dep_dt:
                                    arr_dt = arr_dt.replace(day=arr_dt.day + 1)
                                travel_time = int((arr_dt - dep_dt).total_seconds() / 60)
                            except:
                                travel_time = None
                        if arrival_time:
                            if travel_time is not None:
                                result_text = f"다음 열차: {next_train['departure_time']} (열차번호: {next_train['train_id']}, 방향: {next_train['direction']}, 요일: {next_train['day_type']})\n예상 도착시간: {arrival_time}\n소요시간: {travel_time}분"
                            else:
                                result_text = f"다음 열차: {next_train['departure_time']} (열차번호: {next_train['train_id']}, 방향: {next_train['direction']}, 요일: {next_train['day_type']})\n예상 도착시간: {arrival_time}\n소요시간: 정보 없음"
                        else:
                            result_text = f"다음 열차: {next_train['departure_time']} (열차번호: {next_train['train_id']}, 방향: {next_train['direction']}, 요일: {next_train['day_type']})\n예상 도착시간: 정보 없음"
                        result_var.set(result_text)
                    else:
                        result_var.set('입력한 시간 이후 출발하는 열차가 없습니다.')
                else:
                    # 환승 포함 안내 (구간별로 강력한 디버깅 및 정규화 적용)
                    curr_time = input_dt
                    msg_lines = []
                    total_wait = 0
                    first_departure_time = None  # 첫 구간 실제 출발시간 저장용
                    for idx, (seg_start, seg_end, line) in enumerate(segments):
                        print(f"DEBUG: {idx+1}구간: {seg_start} → {seg_end} ({line}) | input_day={input_day}")
                        times = self.get_station_times(seg_start)
                        print(f"DEBUG: get_station_times({seg_start}) 결과: {len(times)}개 | times={times}")
                        if not times:
                            print(f"DEBUG: get_station_times({seg_start})가 빈 리스트입니다. 역 이름/노선/데이터를 점검하세요.")
                        for t in times:
                            print(f"DEBUG: time={t}")
                        filtered_times = [t for t in times if line in t['line'] and t['day_type'] == input_day]
                        print(f"DEBUG: filtered_times: {filtered_times}")
                        if not filtered_times:
                            print(f"DEBUG: filtered_times가 빈 리스트입니다. line={line}, input_day={input_day}, times={times}")
                        def is_valid_time(timestr):
                            try:
                                datetime.strptime(timestr, '%H:%M')
                                return True
                            except Exception:
                                return False
                        unique_times = {}
                        for t in filtered_times:
                            if t['departure_time'] not in unique_times:
                                unique_times[t['departure_time']] = t
                        valid_times = [t for t in unique_times.values() if is_valid_time(t['departure_time'])]
                        print(f"DEBUG: valid_times: {valid_times}")
                        valid_times.sort(key=lambda t: datetime.strptime(t['departure_time'], '%H:%M'))
                        next_train = None
                        arrival_time = ''
                        for t in valid_times:
                            if datetime.strptime(t['departure_time'], '%H:%M') >= curr_time:
                                try:
                                    row = self.time_data[(self.time_data['열차번호'] == t['train_id']) &
                                                         (self.time_data['노선명'] == t['line']) &
                                                         (self.time_data['운행구간기점명'] + ' → ' + self.time_data['운행구간종점명'] == t['direction']) &
                                                         (self.time_data['요일구분'] == t['day_type'])].iloc[0]
                                    stations_str = row['운행구간정거장']
                                    arrival_times_str = row['정거장도착시각']
                                    stations = [self.normalize_station_name(s.split('-', 1)[1] if '-' in s else s) for s in stations_str.split('+')]
                                    
                                    # 출발역과 도착역의 인덱스 확인
                                    start_idx = -1
                                    end_idx = -1
                                    for i, station in enumerate(stations):
                                        if self.normalize_station_name(seg_start) in station:
                                            start_idx = i
                                        if self.normalize_station_name(seg_end) in station:
                                            end_idx = i
                                    
                                    # 올바른 방향인지 확인 (출발역이 도착역보다 앞에 있어야 함)
                                    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                                        if self.normalize_station_name(seg_end) in stations:
                                            idx2 = stations.index(self.normalize_station_name(seg_end))
                                            arrival_times = self.parse_time_string(arrival_times_str)
                                            station_code = f"{idx2+1:03d}"
                                            arrival_time = arrival_times.get(station_code, '')
                                            next_train = t
                                            break
                                except Exception as e:
                                    print(f"DEBUG: Exception in arrival_time lookup: {e}")
                                    continue
                        if next_train:
                            print(f"DEBUG: next_train: {next_train}")
                            msg_lines.append(f"[{idx+1}구간] {seg_start} → {seg_end} ({line})\n  - {next_train['departure_time']} 출발, {arrival_time if arrival_time else '정보 없음'} 도착, 열차번호 {next_train['train_id']}, 방향: {next_train['direction']}")
                            if arrival_time:
                                curr_time = datetime.strptime(arrival_time, '%H:%M')
                                if idx < len(segments)-1:
                                    next_seg_start = segments[idx+1][0]
                                    next_line = segments[idx+1][2]
                                    print(f"DEBUG: [환승] next_seg_start={next_seg_start}, next_line={next_line}, curr_time={curr_time}")
                                    next_times = self.get_station_times(next_seg_start)
                                    print(f"DEBUG: get_station_times({next_seg_start}) 결과: {len(next_times)}개")
                                    next_filtered = [t for t in next_times if next_line in t['line'] and t['day_type'] == input_day]
                                    print(f"DEBUG: next_filtered: {next_filtered}")
                                    next_unique = {}
                                    for t in next_filtered:
                                        if t['departure_time'] not in next_unique:
                                            next_unique[t['departure_time']] = t
                                    next_valid = [t for t in next_unique.values() if is_valid_time(t['departure_time'])]
                                    next_valid.sort(key=lambda t: datetime.strptime(t['departure_time'], '%H:%M'))
                                    print(f"DEBUG: next_valid: {next_valid}")
                                    next_departure = None
                                    for t in next_valid:
                                        if datetime.strptime(t['departure_time'], '%H:%M') >= curr_time:
                                            next_departure = t['departure_time']
                                            break
                                    print(f"DEBUG: next_departure: {next_departure}")
                                    if next_departure:
                                        wait_min = (datetime.strptime(next_departure, '%H:%M') - curr_time).seconds // 60
                                        msg_lines.append(f"[환승] {seg_end}에서 {next_line} 환승 (대기 {wait_min}분)")
                                        total_wait += wait_min
                                        curr_time = datetime.strptime(next_departure, '%H:%M')
                                        if idx == 0:
                                            first_departure_time = next_train['departure_time']
                                    else:
                                        msg_lines.append(f"[환승] {seg_end}에서 {next_line} 환승 (환승 후 열차 없음)")
                                        print(f"DEBUG: [환승] {seg_end}에서 {next_line} 환승 (환승 후 열차 없음)")
                                        break
                            else:
                                # 도착시간이 없으면 출발시간 + 5분으로 추정
                                curr_time = datetime.strptime(next_train['departure_time'], '%H:%M')
                                curr_time = curr_time.replace(minute=curr_time.minute + 5)
                                if curr_time.minute >= 60:
                                    curr_time = curr_time.replace(hour=curr_time.hour + 1, minute=curr_time.minute - 60)
                                if idx < len(segments)-1:
                                    next_seg_start = segments[idx+1][0]
                                    next_line = segments[idx+1][2]
                                    print(f"DEBUG: [환승] next_seg_start={next_seg_start}, next_line={next_line}, curr_time={curr_time}")
                                    next_times = self.get_station_times(next_seg_start)
                                    print(f"DEBUG: get_station_times({next_seg_start}) 결과: {len(next_times)}개")
                                    next_filtered = [t for t in next_times if next_line in t['line'] and t['day_type'] == input_day]
                                    print(f"DEBUG: next_filtered: {next_filtered}")
                                    next_unique = {}
                                    for t in next_filtered:
                                        if t['departure_time'] not in next_unique:
                                            next_unique[t['departure_time']] = t
                                    next_valid = [t for t in next_unique.values() if is_valid_time(t['departure_time'])]
                                    next_valid.sort(key=lambda t: datetime.strptime(t['departure_time'], '%H:%M'))
                                    print(f"DEBUG: next_valid: {next_valid}")
                                    next_departure = None
                                    for t in next_valid:
                                        if datetime.strptime(t['departure_time'], '%H:%M') >= curr_time:
                                            next_departure = t['departure_time']
                                            break
                                    print(f"DEBUG: next_departure: {next_departure}")
                                    if next_departure:
                                        wait_min = (datetime.strptime(next_departure, '%H:%M') - curr_time).seconds // 60
                                        msg_lines.append(f"[환승] {seg_end}에서 {next_line} 환승 (대기 {wait_min}분)")
                                        total_wait += wait_min
                                        curr_time = datetime.strptime(next_departure, '%H:%M')
                                        if idx == 0:
                                            first_departure_time = next_train['departure_time']
                                    else:
                                        msg_lines.append(f"[환승] {seg_end}에서 {next_line} 환승 (환승 후 열차 없음)")
                                        print(f"DEBUG: [환승] {seg_end}에서 {next_line} 환승 (환승 후 열차 없음)")
                                        break
                        else:
                            print(f"DEBUG: break! valid_times: {valid_times}")
                            msg_lines.append(f"[{idx+1}구간] {seg_start} → {seg_end} ({line})\n  - {curr_time.strftime('%H:%M')} 이후 출발하는 열차가 없습니다.")
                            break
                    if msg_lines:
                        # 최종 도착시간 계산
                        final_arrival = None
                        if arrival_time:
                            final_arrival = arrival_time
                        else:
                            if next_train and next_train.get('departure_time'):
                                try:
                                    t = datetime.strptime(next_train['departure_time'], '%H:%M')
                                    t = t.replace(minute=t.minute + 5)
                                    if t.minute >= 60:
                                        t = t.replace(hour=t.hour + 1, minute=t.minute - 60)
                                    final_arrival = t.strftime('%H:%M')
                                except:
                                    final_arrival = None
                        # 총 소요시간 계산 (첫 구간 실제 출발시간 기준)
                        total_travel_time = 0
                        if final_arrival and first_departure_time:
                            try:
                                start_time = datetime.strptime(first_departure_time, '%H:%M')
                                end_time = datetime.strptime(final_arrival, '%H:%M')
                                if end_time < start_time:
                                    end_time = end_time.replace(day=end_time.day + 1)
                                total_travel_time = int((end_time - start_time).total_seconds() / 60)
                            except:
                                total_travel_time = 0
                        elif final_arrival:
                            try:
                                # fallback: 기존 input_time 기준
                                start_time = datetime.strptime(input_time, '%H:%M')
                                end_time = datetime.strptime(final_arrival, '%H:%M')
                                if end_time < start_time:
                                    end_time = end_time.replace(day=end_time.day + 1)
                                total_travel_time = int((end_time - start_time).total_seconds() / 60)
                            except:
                                total_travel_time = 0
                        if final_arrival:
                            msg_lines.append(f"총 환승 대기시간: {total_wait}분, 소요시간: {total_travel_time}분, 최종 도착: {final_arrival}")
                        else:
                            msg_lines.append(f"총 환승 대기시간: {total_wait}분")
                        result_var.set('\n'.join(msg_lines))
                    else:
                        result_var.set('안내할 수 있는 열차가 없습니다.')
            
            ttk.Button(time_frame, text='다음 열차 안내', style='TButton', command=show_next_train).pack(side=LEFT, padx=5)
            result_var = StringVar()
            result_label = ttk.Label(popup, textvariable=result_var, style='RouteNormal.TLabel')
            result_label.pack(pady=5)
            
            # 확인 버튼
            ttk.Button(popup, text='확인', style='TButton', command=lambda: self._close_popup(popup)).pack(pady=10)
            
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            popup.protocol("WM_DELETE_WINDOW", lambda: self._close_popup(popup))
        else:
            self.popup_opened = True
            popup = Toplevel(self.root)
            popup.title('경로 안내')
            popup.configure(bg='#f8f9fa')
            ttk.Label(popup, text='경로를 찾을 수 없습니다.', style='TLabel').pack(padx=20, pady=20)
            ttk.Button(popup, text='확인', style='TButton', command=lambda: self._close_popup(popup)).pack(pady=10)
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            popup.protocol("WM_DELETE_WINDOW", lambda: self._close_popup(popup))

    def find_min_transfer_route(self, start, end):
        from collections import deque
        station_to_line = {text: line for _, _, text, line in BUTTON_COORDS}
        queue = deque()
        visited = dict()  # (역, 호선): 최소 환승횟수
        for line in station_to_line.get(start, '').split('/'):
            queue.append((start, line, 0, [start], 0))
            visited[(start, line)] = 0
        min_transfer = float('inf')
        min_route = []
        min_dist = float('inf')
        while queue:
            curr, curr_line, transfer, path, dist = queue.popleft()
            if curr == end:
                if transfer < min_transfer or (transfer == min_transfer and dist < min_dist):
                    min_transfer = transfer
                    min_route = path[:]
                    min_dist = dist
                continue
            for next_station in SUBWAY[curr]:
                next_lines = station_to_line.get(next_station, '').split('/')
                for next_line in next_lines:
                    next_transfer = transfer + (0 if next_line == curr_line else 1)
                    state = (next_station, next_line)
                    if state in visited and visited[state] <= next_transfer:
                        continue
                    visited[state] = next_transfer
                    queue.append((next_station, next_line, next_transfer, path + [next_station], dist + 1))
        if not min_route or min_dist == float('inf') or min_transfer == float('inf'):
            return [], 0, 0
        return min_route, min_dist, min_transfer

    def is_transfer_station(self, station):
        """SUBWAY에서 인접 노드가 3개 이상이면 환승역으로 간주"""
        return len(SUBWAY.get(station, {})) >= 3

    def normalize_station_name(self, name):
        """역 이름을 완전히 정규화 (공백, '역', 소문자)"""
        return name.strip().replace('역', '').replace(' ', '').lower()

    def on_map_changed(self, event):
        """지도 선택이 변경되었을 때 호출되는 이벤트 핸들러"""
        selected_display = self.map_var.get()
        selected_map = self.map_options.get(selected_display, "busan_subway.png")
        new_image_path = f"./Image/{selected_map}"
        
        try:
            # 새 이미지 로드
            self.current_image_path = new_image_path
            self.img = Image.open(self.current_image_path)
            
            # 현재 스케일과 위치 유지하면서 이미지 업데이트
            w, h = self.img.size
            new_w = int(w * self.img_scale)
            new_h = int(h * self.img_scale)
            resized = self.img.resize((new_w, new_h), Image.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(resized)
            self.canvas.itemconfig(self.img_id, image=self.img_tk)
            
            # 이미지 중앙 배치
            self._place_image_center()
            
            # 지도에 따라 버튼 표시/숨김 처리
            if selected_map == "busan_subway.png":
                # 부산권 지도: 버튼들 표시
                for btn_id in self.img_btn_ids:
                    self.canvas.itemconfig(btn_id, state='normal')
                self._update_all_img_btns()
                print(f"지도가 {selected_display}({selected_map})로 변경되었습니다. (버튼 활성화)")
            else:
                # 수도권 지도: 버튼들 숨김
                for btn_id in self.img_btn_ids:
                    self.canvas.itemconfig(btn_id, state='hidden')
                print(f"지도가 {selected_display}({selected_map})로 변경되었습니다. (버튼 비활성화)")
            
        except Exception as e:
            print(f"지도 변경 중 오류 발생: {e}")
            # 오류 발생 시 원래 이미지로 복원
            self.map_var.set("부산권")
            self.current_image_path = "./Image/busan_subway.png"
            self.img = Image.open(self.current_image_path)
            self.update_image()

if __name__ == "__main__":
    root = Tk()
    root.title("Subway Map")
    root.geometry("900x700")
    app = SubwayApp(root)
    root.mainloop()