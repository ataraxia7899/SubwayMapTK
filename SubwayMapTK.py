import copy
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

# --- 데이터 상수 분리 ---
BUTTON_COORDS = [
    (2046, 589, "노포"),
    (2045, 662, "범어사"),
    (2045, 734, "남산"),
    (2043, 807, "두실"),
    (2046, 881, "구서"),
    (2045, 953, "장전"),
    (2045, 1025, "부산대"),
    (2046, 1098, "온천장"),
    (2045, 1169, "명륜"),
    (2046, 1247, "동래"),
    (2046, 1350, "교대"),
    (2044, 1454, "연산"),
    (2044, 1571, "시청"),
    (2043, 1681, "양정"),
    (2044, 1790, "부전"),
    (2044, 1906, "서면"),
    (2044, 1985, "범내골"),
    (2044, 2052, "범일"),
    (2044, 2116, "좌천"),
    (2043, 2178, "부산진"),
    (2044, 2244, "초량"),
    (2044, 2309, "부산역"),
    (2032, 2375, "중앙"),
    (1999, 2435, "남포"),
    (1954, 2477, "자갈치"),
    (1896, 2506, "토성"),
    (1825, 2517, "동대신"),
    (1757, 2515, "서대신"),
    (1689, 2518, "대티"),
    (1621, 2517, "괴정"),
    (1552, 2517, "사하"),
    (1483, 2517, "당리"),
    (1422, 2537, "하단"),
    (1370, 2571, "신평"),
    (1332, 2618, "동매"),
    (1307, 2675, "장링"),
    (1300, 2737, "신장림"),
    (1301, 2804, "낫개"),
    (1302, 2867, "다대포항"),
    (1300, 2933, "다대포해수욕장"),
    (1301, 588, "양산"),
    (1302, 654, "남양산"),
    (1301, 719, "부산대양산캠퍼스"),
    (1301, 781, "증산"),
    (1302, 845, "호포"),
    (1299, 910, "금곡"),
    (1299, 974, "동원"),
    (1302, 1038, "율리"),
    (1302, 1104, "화명"),
    (1300, 1168, "수정"),
    (1300, 1248, "덕천"),
    (1300, 1330, "구명"),
    (1303, 1403, "구남"),
    (1300, 1487, "모라"),
    (1302, 1568, "모덕"),
    (1300, 1650, "덕포"),
    (1300, 1735, "사상"),
    (1339, 1848, "감전"),
    (1426, 1906, "주례"),
    (1529, 1912, "냉정"),
    (1632, 1913, "개금"),
    (1735, 1913, "동의대"),
    (1839, 1915, "가야"),
    (1940, 1913, "부암"),
    (2173, 1963, "전포"),
    (2222, 2091, "국제금융센터부산은행"),
    (2272, 2223, "문현"),
    (2398, 2299, "지게골"),
    (2541, 2301, "못골"),
    (2681, 2275, "대연"),
    (2769, 2177, "경성대부경대"),
    (2789, 2035, "남천"),
    (2786, 1906, "금련산"),
    (2789, 1776, "광안"),
    (2787, 1638, "수영"),
    (2791, 1507, "민락"),
    (2857, 1399, "센텀시티"),
    (2979, 1354, "벡스코"),
    (3121, 1361, "동백"),
    (3263, 1362, "해운대"),
    (3404, 1359, "중동"),
    (3498, 1255, "장산"),
    (946, 1421, "대저"),
    (996, 1300, "체육공원"),
    (1078, 1247, "강서구청"),
    (1188, 1240, "구포"),
    (1446, 1239, "숙등"),
    (1590, 1240, "남산정"),
    (1738, 1240, "만덕"),
    (1868, 1334, "미남"),
    (1881, 1399, "사직"),
    (1912, 1433, "종합운동장"),
    (1975, 1461, "거제"),
    (2243, 1453, "물만골"),
    (2440, 1453, "배산"),
    (2639, 1454, "망미"),
    (2788, 588, "안평"),
    (2788, 691, "고촌"),
    (2788, 796, "윗반송"),
    (2788, 896, "영산대"),
    (2788, 1001, "석대"),
    (2781, 1106, "반여농산물시장"),
    (2723, 1198, "금사"),
    (2624, 1239, "서동"),
    (2509, 1240, "명장"),
    (2396, 1240, "충렬사"),
    (2280, 1239, "낙민"),
    (2169, 1239, "수안"),
    (592, 590, "가야대"),
    (592, 655, "장신대"),
    (592, 723, "연지공원"),
    (592, 789, "박물관"),
    (592, 855, "수로왕릉"),
    (592, 923, "봉황"),
    (592, 990, "부원"),
    (592, 1055, "김해시청"),
    (601, 1123, "인제대"),
    (640, 1185, "김해대학"),
    (712, 1232, "지내"),
    (794, 1241, "불암"),
    (874, 1274, "대사"),
    (924, 1335, "평강"),
    (946, 1558, "등구"),
    (945, 1692, "덕두"),
    (968, 1822, "공항"),
    (1077, 1906, "서부산유통지구"),
    (1221, 1882, "괘법르네시떼"),
    (3142, 480, "태화강"),
    (3142, 554, "개운포"),
    (3142, 621, "덕하"),
    (3142, 688, "망양"),
    (3142, 757, "남창"),
    (3142, 825, "서생"),
    (3142, 893, "월내"),
    (3142, 960, "동해좌천"),
    (3142, 1028, "일광"),
    (3142, 1095, "동해기장"),
    (3142, 1163, "오시리아"),
    (3131, 1232, "송정"),
    (3095, 1290, "신해운대"),
    (2807, 1347, "센텀"),
    (2657, 1347, "재송"),
    (2507, 1347, "부산원동"),
    (2357, 1347, "안락"),
    (2207, 1347, "동해동래"),
    (1975, 1628, "거제해맞이"),
    (1975, 1790, "동해부전")
]

SUBWAY = {
    '노포': {'범어사':1},
    "범어사":{'노포': 1, '남산': 1},
    "남산" : {'범어사': 1, '두실': 1},
    '두실' : {'남산': 1, '구서': 1},
    "구서" : {'두실': 1, '장전': 1},
    "장전" : {"구서": 1, "부산대": 1},
    "부산대" : {"장전": 1, "온천장": 1},
    "온천장" : {"부산대": 1, "명륜": 1},
    "명륜" : {'온천장': 1, '동래': 1},
    "동래" : {'명륜': 1, '교대': 1, "수안": 1, "미남": 1},
    "교대" : {'동래': 1, '동해동래': 1, "연산": 1, "거제": 1},
    "연산" : {'교대': 1, '거제': 1, '물만골': 1, '시청': 1},
    "시청" : {'연산': 1, '양정': 1},
    "양정" : {'시청': 1, '부전': 1},
    "부전" : {'서면': 1, '양정': 1},
    "서면" : {'부전': 1, '전포': 1, '부암': 1, '범내골': 1},    
    "범내골" : {'서면': 1, '범일': 1},
    "범일" : {'범내골': 1, '좌천': 1},
    "좌천" : {'부산진': 1, '범일': 1},
    "부산진" : {'좌천': 1, '초량': 1},
    "초량" : {'부산진': 1, '부산역': 1},
    "부산역" : {'초량': 1, '중앙': 1},
    "중앙" : {'부산역': 1, '남포': 1},
    "남포" : {'중앙': 1, '자갈치': 1},
    "자갈치" : {'남포': 1, '토성': 1},
    "토성" : {'자갈치': 1, '동대신': 1},
    "동대신" : {'토성': 1, '서대신': 1},
    "서대신" : {'동대신': 1, '대티': 1},
    "대티" : {'서대신': 1, '괴정': 1},
    "괴정" : {'대티': 1, '사하': 1},
    "사하" : {'괴정': 1, '당리': 1},
    "당리" : {'사하': 1, '하단': 1},
    "하단" : {'당리': 1, '신평': 1},
    "신평" : {'하단': 1, '동매': 1},
    "동매" : {'신평': 1, '장링': 1},
    "장링" : {'동매': 1, '신장림': 1},
    "신장림" : {'장링': 1, '낫개': 1},
    "낫개" : {'신장림': 1, '다대포항': 1},
    "다대포항" : {'낫개': 1, '다대포해수욕장': 1},
    "다대포해수욕장" : {'다대포항': 1},
    '양산': {'남양산':1},
    '남양산': {'양산':1, '부산대양산캠퍼스':1},
    '부산대양산캠퍼스': {'남양산':1, '증산':1},
    '증산': {'부산대양산캠퍼스':1, '호포':1},
    '호포': {'증산':1, '금곡':1},
    '금곡': {'호포':1, '동원':1},
    '동원': {'금곡':1, '율리':1},
    '율리': {'동원':1, '화명':1},
    '화명': {'율리':1, '수정':1},
    '수정': {'화명':1, '덕천':1},
    '덕천': {'수정':1, '구명':1, '구포':1, '숙등':1},
    '구명': {'덕천':1, '구남':1},
    '구남': {'구명':1, '모라':1},
    '모라': {'구남':1, '모덕':1},
    '모덕': {'모라':1, '덕포':1},
    '덕포': {'모덕':1, '사상':1},
    '사상': {'덕포':1, '감전':1, '괘법르네시떼':1},
    '감전': {'사상':1, '주례':1},
    '주례': {'감전':1, '냉정':1},
    '냉정': {'주례':1, '개금':1},
    '개금': {'냉정':1, '동의대':1},
    '동의대': {'개금':1, '가야':1},
    '가야': {'동의대':1, '부암':1},
    '부암': {'가야':1, '서면':1},
    '전포': {'서면':1, '국제금융센터부산은행':1},
    '국제금융센터부산은행': {'전포':1, '문현':1},
    '문현': {'국제금융센터부산은행':1, '지게골':1},
    '지게골': {'문현':1, '못골':1},
    '못골': {'지게골':1, '대연':1},
    '대연': {'못골':1, '경성대부경대':1},
    '경성대부경대': {'대연':1, '남천':1},
    '남천': {'경성대부경대':1, '금련산':1},
    '금련산': {'남천':1, '광안':1},
    '광안': {'금련산':1, '수영':1},
    '수영': {'광안':1, '민락':1, '망미':1},
    '민락': {'수영':1, '센텀시티':1},
    '센텀시티': {'민락':1, '벡스코':1},
    '벡스코': {'센텀시티':1, '동백':1, '신해운대':1, '센텀':1},
    '동백': {'벡스코':1, '해운대':1},
    '해운대': {'동백':1, '중동':1},
    '중동': {'해운대':1, '장산':1},
    '장산': {'중동':1},
    "대저":{"등구":1,"체육공원":1, "평강":1},
    "체육공원":{"강서구청":1, "대저":1},
    "강서구청":{"구포":1, "체육공원":1},
    "구포":{"덕천":1, "강서구청":1},
    "숙등":{"남산정":1, "덕천":1},
    "남산정":{"만덕":1, "숙등":1},
    "만덕":{"미남":1, "남산정":1},
    "미남":{"사직":1, "만덕":1,"동래":1},
    "사직":{"종합운동장":1, "미남":1},
    "종합운동장":{"거제":1, "사직":1},
    "거제":{"연산":1, "종합운동장":1},
    "물만골":{"배산":1, "연산":1},
    "배산":{"망미":1, "물만골":1},
    "망미":{"수영":1, "배산":1},
    '안평': {'고촌':1},
    '고촌': {'안평':1, '윗반송':1},
    '윗반송': {'고촌':1, '영산대':1},
    '영산대': {'윗반송':1, '석대':1},
    '석대': {'영산대':1, '반여농산물시장':1},
    '반여농산물시장': {'석대':1, '금사':1},
    '금사': {'반여농산물시장':1, '서동':1},
    '서동': {'금사':1, '명장':1},
    '명장': {'서동':1, '충렬사':1},
    '충렬사': {'명장':1, '낙민':1},
    '낙민': {'충렬사':1, '수안':1},
    '수안': {'낙민':1, '동래':1},
    "가야대": {"장신대":1},
    "장신대":{"연지공원":1, "가야대":1},
    "연지공원" : {"박물관":1, "장신대":1},
    "박물관":{"수로왕릉":1, "연지공원":1},
    "수로왕릉" : {"봉황":1, "박물관":1},
    "봉황":{"부원":1, "수로왕릉":1},
    "부원":{"김해시청":1, "봉황":1},
    "김해시청":{"인제대":1, "부원":1},
    "인제대":{"김해대학":1, "김해시청":1},
    "김해대학":{"지내":1, "인제대":1},
    "지내":{"불암":1, "김해대학":1},
    "불암":{"대사":1, "지내":1},
    "대사":{"평강":1, "불암":1},
    "평강":{"대저":1, "대사":1},
    "등구":{"덕두":1, "대저":1},
    "덕두":{"공항":1, "등구":1},
    "공항":{"서부산유통지구":1, "덕두":1},
    "서부산유통지구":{"괘법르네시떼":1, "공항":1},
    "괘법르네시떼":{"사상":1, "서부산유통지구":1},
    '태화강' : {'개운포': 1},
    '개운포' : {'태화강': 1, '덕하': 1},
    '덕하' : {'개운포': 1, '망양': 1},
    '망양' : {'덕하': 1, '남창': 1},
    '남창' : {'망양': 1, '서생': 1},
    '서생' : {'남창': 1, '월내': 1},
    '월내' : {'서생': 1, '동해좌천': 1},
    '동해좌천' : {'월내': 1, '일광': 1},
    '일광' : {'동해좌천': 1, '동해기장': 1},
    '동해기장' : {'일광': 1, '오시리아': 1},
    '오시리아' : {'동해기장': 1, '송정': 1},
    '송정' : {'오시리아': 1, '신해운대': 1},
    '신해운대' : {'송정': 1, '벡스코': 1},
    '센텀' : {'벡스코': 1, '재송': 1},
    '재송' : {'센텀': 1, '부산원동': 1},
    '부산원동' : {'재송': 1, '안락': 1},
    '안락' : {'부산원동': 1, '동해동래': 1},
    '동해동래' : {'안락': 1, '교대': 1},
    '거제해맞이' : {'거제': 1, '동해부전': 1},
    '동해부전' : {'거제해맞이': 1}
}

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
        self.station_status_var.set("출발역: (미지정)     -->     도착역: (미지정)")
        self.station_status_label = ttk.Label(self.center_frame, textvariable=self.station_status_var, style='TLabel', anchor='center')
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
            popup.geometry("380x120")
            popup.configure(bg='#f8f9fa')
            popup.update_idletasks()
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            ttk.Label(popup, text='출발역과 도착역을 모두 선택하세요.', style='TLabel').pack(padx=20, pady=20)
            ttk.Button(popup, text='확인', style='TButton', command=popup.destroy).pack(pady=10)
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
        popup.geometry("380x120")
        popup.configure(bg='#f8f9fa')
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (popup.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        if route:
            route_str = ' → '.join(route)
            ttk.Label(popup, text=f'[{self.start} → {self.end}]', style='TLabel').pack(pady=5)
            ttk.Label(popup, text=f'경로: {route_str}', style='TLabel').pack(pady=5)
            ttk.Label(popup, text=f'최단거리: {dist}', style='TLabel').pack(pady=5)
        else:
            ttk.Label(popup, text='경로를 찾을 수 없습니다.', style='TLabel').pack(padx=20, pady=20)
        ttk.Button(popup, text='확인', style='TButton', command=popup.destroy).pack(pady=10)

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