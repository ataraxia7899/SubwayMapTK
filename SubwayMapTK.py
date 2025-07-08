import copy
from tkinter import *
from tkinter import ttk
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
        self.click_start_x = 0
        self.click_start_y = 0
        self.img_btns = []
        self.img_btn_ids = []
        self.routing = {place: {'shortestDist': 0, 'route': [], 'visited': 0} for place in SUBWAY.keys()}
        self._init_style()
        self._init_ui()
        self._init_canvas()
        self._create_image_buttons()
        self._update_all_img_btns()

    def _init_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('맑은 고딕', 11, 'bold'), foreground='#222', background='#e0e0e0', borderwidth=0, focusthickness=3, focuscolor='none', padding=8)
        style.map('TButton', background=[('active', '#b3e5fc'), ('pressed', '#81d4fa')])
        style.configure('TLabel', font=('맑은 고딕', 12), background='#f8f9fa', foreground='#222')
        style.configure('TFrame', background='#f8f9fa')
        self.root.configure(bg="#f8f9fa")

    def _init_ui(self):
        self.top_frame = ttk.Frame(self.root, style='TFrame')
        self.top_frame.pack(side=TOP, fill=X, pady=8)
        self.center_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.center_frame.pack(side=TOP, fill=X, expand=True)
        self.station_status_var = StringVar()
        self.station_status_var.set("출발역: (미지정)     ➔     도착역: (미지정)")
        self.station_status_label = ttk.Label(self.center_frame, textvariable=self.station_status_var, style='TLabel', anchor='center', font=('Arial', 16, 'bold'))
        self.station_status_label.pack(expand=True, anchor='center', pady=8)
        self.find_route_btn = ttk.Button(self.top_frame, text='길 찾기', style='TButton', command=self.show_route_popup)
        self.find_route_btn.pack(side=RIGHT, padx=20)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=2)
        self.top_frame.grid_columnconfigure(2, weight=1)

    def _init_canvas(self):
        self.img = Image.open("./Image/subway.png")
        self.canvas = Canvas(self.root, width=900, height=600, bg='white', highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.img_id = self.canvas.create_image(0, 0, anchor=CENTER, image=self.img_tk)
        self.root.update()
        self._place_image_center()
        # 확대/축소 버튼
        self.plus_btn = ttk.Button(self.root, text='+', style='TButton', command=self.zoom_in)
        self.minus_btn = ttk.Button(self.root, text='-', style='TButton', command=self.zoom_out)
        self.plus_btn.place(relx=1.0, rely=1.0, x=-30, y=-120, anchor='se')
        self.minus_btn.place(relx=1.0, rely=1.0, x=-30, y=-60, anchor='se')
        # 이벤트 바인딩
        self.root.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind('<ButtonPress-1>', self.on_button_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<Configure>', self.on_configure)
        self.canvas.tag_bind('invisible_btn', '<Button-1>', self.on_invisible_btn_click)

    def _create_image_buttons(self):
        for x, y, text in BUTTON_COORDS:
            btn_id = self.canvas.create_rectangle(0, 0, 20, 20, outline='', fill='', tags='invisible_btn')
            self.img_btns.append((text, x, y))
            self.img_btn_ids.append(btn_id)

    def _update_all_img_btns(self):
        w, h = self.img.size
        img_cx, img_cy = self.canvas.coords(self.img_id)
        for idx, (_, bx, by) in enumerate(self.img_btns):
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
        self.click_start_x = event.x
        self.click_start_y = event.y

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

    def on_invisible_btn_click(self, event):
        for idx, btn_id in enumerate(self.img_btn_ids):
            coords = self.canvas.coords(btn_id)
            if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                station = self.img_btns[idx][0]
                self.show_station_select_popup(station)
                break

    # --- 팝업 및 상태 업데이트 ---
    def show_station_select_popup(self, station):
        popup = Toplevel(self.root)
        popup.title(f"{station}역 선택")
        popup.geometry("380x120")
        popup.configure(bg='#f8f9fa')
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        ttk.Label(popup, text=f"{station}역을 출발/도착역으로 설정", style='TLabel').pack(pady=16)
        btn_frame = ttk.Frame(popup, style='TFrame')
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="출발역으로", style='TButton', command=lambda: self.set_start_station(station, popup)).pack(side=LEFT, padx=10)
        ttk.Button(btn_frame, text="도착역으로", style='TButton', command=lambda: self.set_end_station(station, popup)).pack(side=RIGHT, padx=10)

    def set_start_station(self, station, popup):
        self.start = station
        self.update_station_status()
        popup.destroy()

    def set_end_station(self, station, popup):
        self.end = station
        self.update_station_status()
        popup.destroy()

    def update_station_status(self):
        if self.start and self.end:
            self.station_status_var.set(f"출발역: {self.start}     -->     도착역: {self.end}")
        elif self.start:
            self.station_status_var.set(f"출발역: {self.start}     -->     도착역: (미지정)")
        elif self.end:
            self.station_status_var.set(f"출발역: (미지정)     -->     도착역: {self.end}")
        else:
            self.station_status_var.set("출발역: (미지정)     -->     도착역: (미지정)")

    # --- 경로 탐색 및 안내 ---
    def show_route_popup(self):
        if not self.start or not self.end:
            popup = Toplevel(self.root)
            popup.title('경로 안내')
            popup.configure(bg='#f8f9fa')
            ttk.Label(popup, text='출발역과 도착역을 모두 선택하세요.', style='TLabel').pack(padx=20, pady=20)
            ttk.Button(popup, text='확인', style='TButton', command=popup.destroy).pack(pady=10)
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            return
        # routing 초기화
        for place in self.routing.keys():
            self.routing[place] = {'shortestDist': 0, 'route': [], 'visited': 0}
        self.visit_place(self.start)
        while 1:
            minDist = max(self.routing.values(), key=lambda x: x['shortestDist'])['shortestDist']
            toVisit = ''
            for name, search in self.routing.items():
                if 0 < search['shortestDist'] <= minDist and not search['visited']:
                    minDist = search['shortestDist']
                    toVisit = name
            if toVisit == '':
                break
            self.visit_place(toVisit)
        route = self.routing[self.end]['route'] + [self.end] if self.routing[self.end]['route'] else []
        dist = self.routing[self.end]['shortestDist']
        popup = Toplevel(self.root)
        popup.title('경로 안내')
        popup.configure(bg='#f8f9fa')
        if route:
            route_str = ' → '.join(route)
            ttk.Label(popup, text=f'[{self.start} → {self.end}]', style='TLabel').pack(pady=5)
            ttk.Label(popup, text=f'경로: {route_str}', style='TLabel').pack(pady=5)
            ttk.Label(popup, text=f'최단거리: {dist}', style='TLabel').pack(pady=5)
        else:
            ttk.Label(popup, text='경로를 찾을 수 없습니다.', style='TLabel').pack(padx=20, pady=20)
        ttk.Button(popup, text='확인', style='TButton', command=popup.destroy).pack(pady=10)
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    def visit_place(self, visit):
        self.routing[visit]['visited'] = 1
        for togo, betweenDist in SUBWAY[visit].items():
            toDist = self.routing[visit]['shortestDist'] + betweenDist
            if (self.routing[togo]['shortestDist'] >= toDist) or not self.routing[togo]['route']:
                self.routing[togo]['shortestDist'] = toDist
                self.routing[togo]['route'] = copy.deepcopy(self.routing[visit]['route'])
                self.routing[togo]['route'].append(visit)

if __name__ == "__main__":
    root = Tk()
    root.title("Subway Map")
    root.geometry("900x700")
    app = SubwayApp(root)
    root.mainloop()