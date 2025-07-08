import copy
from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.title("Subway Map")
root.geometry("640x480")

# 출발역/도착역 표시용 라벨과 길찾기 버튼을 담을 프레임 생성
# (상단 한 줄에 나란히 배치)
top_frame = Frame(root, bg="#f0f0f0")
top_frame.pack(side=TOP, fill=X, pady=2)

center_frame = Frame(top_frame, bg="#f0f0f0")
center_frame.pack(side=TOP, fill=X, expand=True)

# 출발역/도착역 변수 초기화
start = ''
end = ''

station_status_var = StringVar()
station_status_var.set("출발역: (미지정)     -->     도착역: (미지정)")
station_status_label = Label(center_frame, textvariable=station_status_var, font=("맑은 고딕", 12, "bold"), bg="#f0f0f0")
station_status_label.pack(expand=True, anchor='center')

find_route_btn = Button(top_frame, text='길 찾기', command=lambda: show_route_popup())
find_route_btn.pack(side=RIGHT, padx=10)

# column 0(왼쪽 여백), 1(라벨), 2(버튼) 비율 설정
top_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=2)
top_frame.grid_columnconfigure(2, weight=1)

img = Image.open("./Image/subway.png")
img_scale = 1.0
img_min_scale = 0.2
img_max_scale = 3.0

canvas = Canvas(root, width=640, height=480, bg='white')
canvas.pack(fill=BOTH, expand=True)

# 여러 좌표에 버튼을 쉽게 추가할 수 있도록 리스트로 관리
button_coords = [
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

img_btns = []  # (Button, x, y) 튜플
img_btn_ids = []

def create_image_buttons():
    for x, y, text in button_coords:
        # 투명한 캔버스 윈도우(실제 위젯 없음)
        btn_id = canvas.create_rectangle(0, 0, 20, 20, outline='', fill='red', tags='invisible_btn')
        img_btns.append((text, x, y))
        img_btn_ids.append(btn_id)

def update_all_img_btns():
    w, h = img.size
    img_cx, img_cy = canvas.coords(img_id)
    for idx, (_, bx, by) in enumerate(img_btns):
        dx = (bx - w / 2) * img_scale
        dy = (by - h / 2) * img_scale
        btn_canvas_x = img_cx + dx
        btn_canvas_y = img_cy + dy
        # 사각형 위치 갱신 (20x20 크기, 필요시 조정)
        canvas.coords(img_btn_ids[idx],
                    btn_canvas_x-10, btn_canvas_y-10,
                    btn_canvas_x+10, btn_canvas_y+10)

# 중앙 좌표 계산 함수
def get_center_coords(img_w, img_h):
    c_w = canvas.winfo_width()
    c_h = canvas.winfo_height()
    x = c_w // 2
    y = c_h // 2
    return x, y

# 초기 중앙 배치
def place_image_center():
    global img_id, img_tk, img_scale
    w, h = img.size
    new_w = int(w * img_scale)
    new_h = int(h * img_scale)
    x, y = get_center_coords(new_w, new_h)
    canvas.coords(img_id, x, y)

img_tk = ImageTk.PhotoImage(img)
img_id = canvas.create_image(0, 0, anchor=CENTER, image=img_tk)
canvas.update()  # 실제 크기 반영
place_image_center()
create_image_buttons()
update_all_img_btns()

# 이미지 이동 관련 변수
img_drag_start_x = 0
img_drag_start_y = 0

# 클릭 시작 좌표 저장용 변수
click_start_x = 0
click_start_y = 0

def update_image(center_x=None, center_y=None, scale_from=None):
    global img_tk, img_id, img_scale
    w, h = img.size
    new_w = int(w * img_scale)
    new_h = int(h * img_scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(resized)
    canvas.itemconfig(img_id, image=img_tk)
    canvas.config(scrollregion=(0, 0, new_w, new_h))
    # 확대/축소 기준점 보정
    if center_x is not None and center_y is not None and scale_from is not None:
        img_cx, img_cy = canvas.coords(img_id)
        new_img_cx = center_x - (center_x - img_cx) * (img_scale / scale_from)
        new_img_cy = center_y - (center_y - img_cy) * (img_scale / scale_from)
        canvas.coords(img_id, new_img_cx, new_img_cy)
    else:
        x, y = get_center_coords(new_w, new_h)
        canvas.coords(img_id, x, y)
    update_all_img_btns()

def on_configure(event):
    w, h = img.size
    new_w = int(w * img_scale)
    new_h = int(h * img_scale)
    x, y = get_center_coords(new_w, new_h)
    canvas.coords(img_id, x, y)
    update_all_img_btns()

def on_mousewheel(event):
    global img_scale
    old_scale = img_scale
    if event.delta > 0:
        img_scale = min(img_max_scale, img_scale * 1.1)
    else:
        img_scale = max(img_min_scale, img_scale * 0.9)
    # 마우스 위치를 기준으로 확대/축소
    canvas_x = event.x
    canvas_y = event.y
    update_image(center_x=canvas_x, center_y=canvas_y, scale_from=old_scale)

def on_button_press(event):
    global img_drag_start_x, img_drag_start_y, click_start_x, click_start_y
    img_drag_start_x = event.x
    img_drag_start_y = event.y
    click_start_x = event.x
    click_start_y = event.y

def on_drag(event):
    global img_drag_start_x, img_drag_start_y
    dx = event.x - img_drag_start_x
    dy = event.y - img_drag_start_y
    canvas.move(img_id, dx, dy)
    img_drag_start_x = event.x
    img_drag_start_y = event.y
    update_all_img_btns()

# 마우스 휠 확대/축소
root.bind("<MouseWheel>", on_mousewheel)
# 마우스 드래그 이동
canvas.bind('<ButtonPress-1>', on_button_press)
canvas.bind('<B1-Motion>', on_drag)
# 창 크기 변경 시 중앙 정렬
canvas.bind('<Configure>', on_configure)

def zoom_in():
    global img_scale
    old_scale = img_scale
    img_scale = min(img_max_scale, img_scale * 1.1)
    # 캔버스 중앙 기준 확대
    c_w = canvas.winfo_width() // 2
    c_h = canvas.winfo_height() // 2
    update_image(center_x=c_w, center_y=c_h, scale_from=old_scale)

def zoom_out():
    global img_scale
    old_scale = img_scale
    img_scale = max(img_min_scale, img_scale * 0.9)
    # 캔버스 중앙 기준 축소
    c_w = canvas.winfo_width() // 2
    c_h = canvas.winfo_height() // 2
    update_image(center_x=c_w, center_y=c_h, scale_from=old_scale)

# 오른쪽 하단 +, - 버튼 추가
plus_btn = Button(root, text='+', command=zoom_in)
minus_btn = Button(root, text='-', command=zoom_out)
# 오른쪽 하단에 세로로 배치 (여백 20, 버튼 높이 40 기준)
plus_btn.place(relx=1.0, rely=1.0, x=-20, y=-80, anchor='se')
minus_btn.place(relx=1.0, rely=1.0, x=-20, y=-30, anchor='se')

landscape = {
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

routing = {}
for place in landscape.keys():
    routing[place] = {'shortestDist':0, 'route':[], 'visited':0}

def visitPlace(visit):
    routing[visit]['visited'] = 1
    for togo, betweenDist in landscape[visit].items():
        toDist = routing[visit]['shortestDist'] + betweenDist
        if(routing[togo]['shortestDist']>=toDist) or not routing[togo]['route']:
            routing[togo]['shortestDist'] = toDist
            routing[togo]['route'] = copy.deepcopy(routing[visit]['route'])
            routing[togo]['route'].append(visit)

# 클릭 이벤트 바인딩
def on_invisible_btn_click(event):
    for idx, btn_id in enumerate(img_btn_ids):
        coords = canvas.coords(btn_id)
        if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
            station = img_btns[idx][0]
            show_station_select_popup(station)
            break

def show_station_select_popup(station):
    popup = Toplevel(root)
    popup.title(f"{station}역 선택")
    popup.geometry("200x100")
    # 팝업을 메인 윈도우 중앙에 배치
    popup.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (popup.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (popup.winfo_height() // 2)
    popup.geometry(f"+{x}+{y}")
    Label(popup, text=f"{station}역을 출발/도착역으로 설정").pack(pady=10)
    Button(popup, text="출발역으로", command=lambda: set_start_station(station, popup)).pack(side=LEFT, padx=10)
    Button(popup, text="도착역으로", command=lambda: set_end_station(station, popup)).pack(side=RIGHT, padx=10)

def set_start_station(station, popup):
    global start
    start = station
    print(f"출발역이 {station}로 설정되었습니다.")
    update_station_status()
    popup.destroy()

def set_end_station(station, popup):
    global end
    end = station
    print(f"도착역이 {station}로 설정되었습니다.")
    update_station_status()
    popup.destroy()

canvas.tag_bind('invisible_btn', '<Button-1>', on_invisible_btn_click)

def show_route_popup():
    # 출발역, 도착역이 모두 지정되어야 함
    if not start or not end:
        popup = Toplevel(root)
        popup.title('경로 안내')
        Label(popup, text='출발역과 도착역을 모두 선택하세요.').pack(padx=20, pady=20)
        Button(popup, text='확인', command=popup.destroy).pack(pady=10)
        return
    # 경로 탐색 로직 실행 (기존 코드 활용)
    # routing 초기화
    for place in routing.keys():
        routing[place] = {'shortestDist':0, 'route':[], 'visited':0}
    visitPlace(start)
    while 1:
        minDist = max(routing.values(),key = lambda x:x['shortestDist'])['shortestDist']
        toVisit = ''
        for name, search in routing.items():
            if 0 < search['shortestDist'] <=minDist and not search['visited']:
                minDist = search['shortestDist']
                toVisit=name
        if toVisit == '':
            break
        visitPlace(toVisit)
    # 결과 표시
    route = routing[end]['route'] + [end] if routing[end]['route'] else []
    dist = routing[end]['shortestDist']
    popup = Toplevel(root)
    popup.title('경로 안내')
    if route:
        route_str = ' → '.join(route)
        Label(popup, text=f'[{start} → {end}]').pack(pady=5)
        Label(popup, text=f'경로: {route_str}').pack(pady=5)
        Label(popup, text=f'최단거리: {dist}').pack(pady=5)
    else:
        Label(popup, text='경로를 찾을 수 없습니다.').pack(padx=20, pady=20)
    Button(popup, text='확인', command=popup.destroy).pack(pady=10)

def update_station_status():
    if start and end:
        station_status_var.set(f"출발역: {start}     -->     도착역: {end}")
    elif start:
        station_status_var.set(f"출발역: {start}     -->     도착역: (미지정)")
    elif end:
        station_status_var.set(f"출발역: (미지정)     -->     도착역: {end}")
    else:
        station_status_var.set("출발역: (미지정)     -->     도착역: (미지정)")

root.mainloop()