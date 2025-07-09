import copy
from tkinter import Tk, Toplevel, StringVar, Canvas, BOTH, LEFT, RIGHT, TOP, X, CENTER
from tkinter import ttk
from tkinter import font, Label
from PIL import Image, ImageTk
import sys
sys.path.append('./SubwayMap')
from SubwayData import BUTTON_COORDS, SUBWAY

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
        self.popup_opened = False  # 팝업 중복 방지 플래그
        self._init_style()
        self._init_ui()
        self._init_canvas()
        self._create_image_buttons()
        self._update_all_img_btns()

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
        self.img = Image.open("./Image/subway.png")
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
        self.canvas.bind('<Configure>', self.on_configure)
        # 역 버튼 클릭/드래그 구분 바인딩
        self.canvas.tag_bind('invisible_btn', '<ButtonPress-1>', self.on_btn_press)
        self.canvas.tag_bind('invisible_btn', '<ButtonRelease-1>', self.on_btn_release)

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
        self.img_drag_start_x = event.x
        self.img_drag_start_y = event.y

    def on_drag(self, event):
        dx = event.x - self.img_drag_start_x
        dy = event.y - self.img_drag_start_y
        self.canvas.move(self.img_id, dx, dy)
        self.img_drag_start_x = event.x
        self.img_drag_start_y = event.y
        self._update_all_img_btns()

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

    def show_station_select_popup(self, station, line):
        if self.popup_opened:
            return
        self.popup_opened = True
        popup = Toplevel(self.root)
        popup.title(f"{station}역 선택")
        popup.geometry("380x120")
        popup.configure(bg='#f8f9fa')
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        ttk.Label(popup, text=f"{station}역 ({line}) 을 출발/도착역으로 설정", style='TLabel').pack(pady=16)
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
            return [], 0, 0
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
        if start_valid:
            self.start = start_input
        if end_valid:
            self.end = end_input
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

    def visit_place(self, visit):
        self.routing[visit]['visited'] = 1
        for togo, betweenDist in SUBWAY[visit].items():
            toDist = self.routing[visit]['shortestDist'] + betweenDist
            if (self.routing[togo]['shortestDist'] >= toDist) or not self.routing[togo]['route']:
                self.routing[togo]['shortestDist'] = toDist
                self.routing[togo]['route'] = copy.deepcopy(self.routing[visit]['route'])
                self.routing[togo]['route'].append(visit)

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

if __name__ == "__main__":
    root = Tk()
    root.title("Subway Map")
    root.geometry("900x700")
    app = SubwayApp(root)
    root.mainloop()