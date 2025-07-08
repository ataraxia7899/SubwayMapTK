import copy
from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.title("Subway Map")
root.geometry("640x480")

img = Image.open("./Image/subway.png")
img_scale = 1.0
img_min_scale = 0.2
img_max_scale = 3.0

canvas = Canvas(root, width=640, height=480, bg='white')
canvas.pack(fill=BOTH, expand=True)

# 여러 좌표에 버튼을 쉽게 추가할 수 있도록 리스트로 관리
button_coords = [
    # (, , "노포"),
    # (, , "범어사"),
    # (, , "남산"),
    # (, , "두실"),
    # (, , "구서"),
    # (, , "장전"),
    # (, , "부산대"),
    # (, , "온천장"),
    # (, , "명륜"),
    # (, , "동래"),
    # (, , "교대"),
    # (, , "연산"),
    # (, , "시청"),
    # (, , "양정"),
    # (, , "부전"),
    # (, , "서면"),
    # (, , "범내골"),
    # (, , "범일"),
    # (, , "좌천"),
    # (, , "부산진"),
    # (, , "초량"),
    # (, , "부산역"),
    # (, , "중앙"),
    # (, , "남포"),
    # (, , "자갈치"),
    # (, , "토성"),
    # (, , "동대신"),
    # (, , "서대신"),
    # (, , "대티"),
    # (, , "괴정"),
    # (, , "사하"),
    # (, , "당리"),
    # (, , "하단"),
    # (, , "신평"),
    # (, , "동매"),
    # (, , "장링"),
    # (, , "신장림"),
    # (, , "낫개"),
    # (, , "다대포항"),
    # (, , "다대포해수욕장"),
    # (, , "양산"),
    # (, , "남양산"),
    # (, , "부산대양산캠퍼스"),
    # (, , "증산"),
    # (, , "호포"),
    # (, , "금곡"),
    # (, , "동원"),
    # (, , "율리"),
    # (, , "화명"),
    # (, , "수정"),
    # (, , "덕천"),
    # (, , "구명"),
    # (, , "구남"),
    # (, , "모라"),
    # (, , "모덕"),
    # (, , "덕포"),
    # (, , "사상"),
    # (, , "감전"),
    # (, , "주례"),
    # (, , "냉정"),
    # (, , "개금"),
    # (, , "동의대"),
    # (, , "가야"),
    # (, , "부암"),
    # (, , "전포"),
    # (, , "국제금융센터부산은행"),
    # (, , "문현"),
    # (, , "지게골"),
    # (, , "못골"),
    # (, , "대연"),
    # (, , "경성대부경대"),
    # (, , "남천"),
    # (, , "금련산"),
    # (, , "광안"),
    # (, , "수영"),
    # (, , "민락"),
    # (, , "센텀시티"),
    # (, , "벡스코"),
    # (, , "동백"),
    # (, , "해운대"),
    # (, , "중동"),
    # (, , "장산"),
    # (, , "대저"),
    # (, , "체육공원"),
    # (, , "강서구청"),
    # (, , "구포"),
    # (, , "숙등"),
    # (, , "남산정"),
    # (, , "만덕"),
    # (, , "미남"),
    # (, , "사직"),
    # (, , "종합운동장"),
    # (, , "거제"),
    # (, , "물만골"),
    # (, , "배산"),
    # (, , "망미"),
    # (, , "안평"),
    # (, , "고촌"),
    # (, , "윗반송"),
    # (, , "영산대"),
    # (, , "석대"),
    # (, , "반여농산물시장"),
    # (, , "금사"),
    # (, , "서동"),
    # (, , "명장"),
    # (, , "충렬사"),
    # (, , "낙민"),
    # (, , "수안"),
    # (, , "미남"),
    # (, , "가야대"),
    # (, , "장신대"),
    # (, , "연지공원"),
    # (, , "박물관"),
    # (, , "수로왕릉"),
    # (, , "봉황"),
    # (, , "부원"),
    # (, , "김해시청"),
    # (, , "인제대"),
    # (, , "김해대학"),
    # (, , "지내"),
    # (, , "불암"),
    # (, , "대사"),
    # (, , "평강"),
    # (, , "등구"),
    # (, , "덕두"),
    # (, , "공항"),
    # (, , "서부산유통지구"),
    # (, , "괘법르네시떼"),
    # (, , "태화강"),
    # (, , "개운포"),
    # (, , "덕하"),
    # (, , "망양"),
    # (, , "남창"),
    # (, , "서생"),
    # (, , "월내"),
    # (, , "동해좌천"),
    # (, , "일광"),
    # (, , "동해기장"),
    # (, , "오시리아"),
    # (, , "송정"),
    # (, , "신해운대"),
    # (, , "센텀"),
    # (, , "재송"),
    # (, , "부산원동"),
    # (, , "안락"),
    # (, , "동해동래"),
    # (, , "거제해맞이"),
    # (, , "동해부전"),
    # 여기에 원하는 좌표를 추가하세요. 예: (x, y, "텍스트"),
]

img_btns = []  # (Button, x, y) 튜플
img_btn_ids = []

def create_image_buttons():
    for x, y, text in button_coords:
        # 투명한 캔버스 윈도우(실제 위젯 없음)
        btn_id = canvas.create_rectangle(0, 0, 20, 20, outline='', fill='', tags='invisible_btn')
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

def on_button_release(event):
    global click_start_x, click_start_y
    dx = event.x - click_start_x
    dy = event.y - click_start_y
    if abs(dx) < 5 and abs(dy) < 5:
        # 클릭으로 간주, 이미지 좌표 출력
        img_cx, img_cy = canvas.coords(img_id)
        ddx = event.x - img_cx
        ddy = event.y - img_cy
        w, h = img.size
        img_x = w / 2 + ddx / img_scale
        img_y = h / 2 + ddy / img_scale
        img_x = int(round(img_x))
        img_y = int(round(img_y))
        print(f"이미지 내 좌표: ({img_x}, {img_y})")

# 마우스 휠 확대/축소
root.bind("<MouseWheel>", on_mousewheel)
# 마우스 드래그 이동
canvas.bind('<ButtonPress-1>', on_button_press)
canvas.bind('<B1-Motion>', on_drag)
canvas.bind('<ButtonRelease-1>', on_button_release)
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

start = '노포'
end = '벡스코'
print("-------------[",start,"-->",end,"]--------------")

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
    '미남': {'동래':1, '만덕':1, '사직':1},
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
    print("["+toVisit+"]")
    print("거리 : ",minDist)

print("\n","[",start,"->",end,"]")
print("Route : ",routing[end]['route'])
print("최단거리 : ",routing[end]['shortestDist'])

# 클릭 이벤트 바인딩
def on_invisible_btn_click(event):
    # 클릭된 좌표가 버튼 영역 안에 있는지 확인
    for idx, btn_id in enumerate(img_btn_ids):
        coords = canvas.coords(btn_id)
        if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
            text = img_btns[idx][0]  # 텍스트 가져오기
            print(f"{text} 클릭됨!")
            break

canvas.tag_bind('invisible_btn', '<Button-1>', on_invisible_btn_click)

root.mainloop()