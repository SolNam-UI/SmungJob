import pygame
import random
import time
import sys

pygame.init()

# 화면 설정
WIDTH, HEIGHT = 1500, 950
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("수뭉이의 치즈밥가게")

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
YELLOW = (255, 230, 50)
GREEN = (100, 220, 100)
RED = (200, 50, 50)
BLUE = (120, 180, 255) 

# 이미지 로드
try:
    IMG_SIZE_ING = (100, 100)
    rice_img = pygame.image.load("rice.png").convert_alpha()
    rice_img = pygame.transform.scale(rice_img, IMG_SIZE_ING)
    
    cheese_img = pygame.image.load("cheese.png").convert_alpha()
    cheese_img = pygame.transform.scale(cheese_img, IMG_SIZE_ING)
    
    flyfish_img = pygame.image.load("flyfish.png").convert_alpha()
    flyfish_img = pygame.transform.scale(flyfish_img, IMG_SIZE_ING)
    
    truffle_img = pygame.image.load("truffle.png").convert_alpha()
    truffle_img = pygame.transform.scale(truffle_img, IMG_SIZE_ING)
    
    bulgogi_img = pygame.image.load("bulgogi.png").convert_alpha()
    bulgogi_img = pygame.transform.scale(bulgogi_img, IMG_SIZE_ING)

    IMG_SIZE_POT = (150, 150)
    pot_img = pygame.image.load("pot.png").convert_alpha()
    pot_img = pygame.transform.scale(pot_img, IMG_SIZE_POT)
    
    soomoong_tray_img = pygame.image.load("soomoong.png").convert_alpha() 
    soomoong_tray_img = pygame.transform.scale(soomoong_tray_img, (250, 250))


except pygame.error as e:
    print("이미지 파일 로드 실패. 파일 이름(rice.png, pot.png, soomoong.png 등)이 올바른지,")
    print("파일이 .py 코드와 같은 폴더에 있는지 확인하세요.")
    print("오류:", e)
    pygame.quit()
    sys.exit()


# 게임 변수
money = 0
start_time = time.time()
order_interval = 9
last_order_time = 0
orders = []
drag_item = None
drag_offset = (0, 0)
remaining = 90

customer_feedback = ""
feedback_display_time = 0

# 재료 및 메뉴
ingredients = [
    {"name": "밥", "pos": (50, 550), "img": rice_img},
    {"name": "치즈", "pos": (150, 550), "img": cheese_img},
    {"name": "날치알", "pos": (300, 550), "img": flyfish_img}, 
    {"name": "트러플", "pos": (400, 550), "img": truffle_img}, 
    {"name": "불고기", "pos": (500, 550), "img": bulgogi_img}, 
]

base_ingredients = ["밥", "치즈"] 
toppings = ["날치알", "트러플", "불고기"]
requests = ["치즈 추가", "밥 추가", "토핑 추가"]
menu = ["날치알 치즈밥", "트러플 치즈밥", "불고기 치즈밥"]

# 객체
cookpots = [{"rect": pygame.Rect(100 + i * 220, 200, 150, 150), # 뚝배기 영역
             "ingredients": [],
             "start": None,
             "status": "empty",
             "menu": None} for i in range(4)]

tray = pygame.Rect(1150, 600, 250, 250) 

# 함수
def draw_text(text, x, y, color=BLACK, size=26):
    try:
        f = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", size)
    except:
        try:
            f = pygame.font.SysFont("malgungothic", size)
        except:
            f = pygame.font.SysFont(None, size)
            
    t = f.render(text, True, color)
    screen.blit(t, (x, y))

def display_pot_ingredients_text(pot, x, y):
    ingredients_str = ", ".join(pot["ingredients"])
    if len(ingredients_str) > 20: 
        ingredients_str = ingredients_str[:17] + "..."
    draw_text(ingredients_str, x, y, BLACK, 18)


def generate_order():
    m = random.choice(menu)
    r = random.choice(requests)
    orders.append({"menu": m, "request": r, "time": time.time()})

def calc_price(order, burned, request_done):
    if burned:
        return 0
    price = 8000
    penalty = 0

    if not request_done:
        penalty += 1
    
    for _ in range(penalty):
        price //= 2
    return price

# 메인 루프
clock = pygame.time.Clock()

while True:
    screen.fill(WHITE)
    current_time = time.time() 
    elapsed = current_time - start_time
    remaining = max(0, 90 - int(elapsed))

    # 시간 종료
    if remaining <= 0:
        screen.fill(WHITE)
        draw_text(f"게임 종료! 총 수입: {money:,}원", 300, 300, RED, 40)
        pygame.display.flip()
        pygame.time.wait(4000)
        pygame.quit()
        sys.exit()

    # 주문 생성 주기
    if elapsed < 30:
        order_interval = 9
    elif elapsed < 60:
        order_interval = 7
    else:
        order_interval = 5

    if current_time - last_order_time > order_interval:
        generate_order()
        last_order_time = current_time

    # 이벤트
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for ing in ingredients:
                ix, iy = ing["pos"]
                if pygame.Rect(ix, iy, 80, 80).collidepoint(mx, my):
                    drag_item = ing
                    drag_offset = (mx - ix, my - iy)

            for i, pot in enumerate(cookpots):
                if pot["status"] in ["cooking", "ready", "burned"]: 
                    if pot["rect"].collidepoint(mx, my):
                        drag_item = {"type": "pot", "index": i}
                        drag_offset = (mx - pot["rect"].x, my - pot["rect"].y)

        elif event.type == pygame.MOUSEBUTTONUP:
            if drag_item:
                mx, my = pygame.mouse.get_pos()
                
                if "name" in drag_item:
                    for pot in cookpots:
                        if pot["rect"].collidepoint(mx, my):
                            
                            if pot["status"] == "empty":
                                pot["ingredients"].append(drag_item["name"])
                                pot["status"] = "cooking"
                                pot["start"] = current_time 

                            elif pot["status"] == "cooking":
                                pot["ingredients"].append(drag_item["name"])
                            
                            if pot["menu"] is None: 
                                base_check = all(i in pot["ingredients"] for i in base_ingredients)
                                topping_check = any(t in pot["ingredients"] for t in toppings)

                                if base_check and topping_check:
                                    if "날치알" in pot["ingredients"]: pot["menu"] = "날치알 치즈밥"
                                    elif "트러플" in pot["ingredients"]: pot["menu"] = "트러플 치즈밥"
                                    elif "불고기" in pot["ingredients"]: pot["menu"] = "불고기 치즈밥"

                elif drag_item["type"] == "pot":
                    i = drag_item["index"]
                    pot = cookpots[i]
                    if tray.collidepoint(mx, my): 
                        if orders:
                            order = orders.pop(0)
                            
                            burned = pot["status"] == "burned"
                            request_done = True 
                            
                            menu_match = (pot["menu"] == order["menu"])
                            if not menu_match:
                                request_done = False 

                            undercooked = (pot["status"] == "cooking")
                            if undercooked:
                                request_done = False 

                            price = calc_price(order, burned, request_done)
                            money += price
                            
                            if burned:
                                customer_feedback = "탄 걸 어떻게 먹으라는 거야!!"
                            elif undercooked:
                                customer_feedback = "하 이게 최선인가? (덜 익음)"
                            elif price == 8000:
                                customer_feedback = "여기가 미슐랭인가\n감동을 주는 맛!!"
                            elif price == 4000:
                                customer_feedback = "흠 먹을만하군"
                            elif price == 2000:
                                customer_feedback = "하 이게 최선인가?"
                            else: 
                                customer_feedback = "이런 가게는 장사 접어야 돼!"
                            feedback_display_time = current_time
                            
                        cookpots[i] = {"rect": pot["rect"], "ingredients": [], "start": None, 
                                       "status": "empty", "menu": None}
                        
                drag_item = None

    # 상태 업데이트
    for pot in cookpots:
        if pot["status"] in ["cooking", "ready"]: 
            if pot["start"] is not None:
                t = current_time - pot["start"]
                
                if t >= 5:
                    pot["status"] = "burned"
                elif t >= 3: 
                    pot["status"] = "ready"

    #UI
    draw_text(f"돈: {money:,}원", 20, 20) 
    
    draw_text(f"남은 시간: {remaining}s", 300, 20)
    draw_text("주문 목록", 1000, 50) 
    for i, o in enumerate(orders[-4:]): 
        draw_text(f"{o['menu']} / {o['request']}", 1000, 90 + i * 35) 

    if customer_feedback and current_time - feedback_display_time < 4:
        feedback_lines = customer_feedback.split('\n')
        feedback_y = 450 
        for line in feedback_lines:
            draw_text(line, 1000, feedback_y, RED, 30)
            feedback_y += 35
    else:
        customer_feedback = "" 

    for i, pot in enumerate(cookpots):
        color = None 
        if pot["status"] == "cooking":
            color = YELLOW 
        elif pot["status"] == "ready":
            color = GREEN 
        elif pot["status"] == "burned":
            color = RED 
        
        if color:
             pygame.draw.rect(screen, color, pot["rect"])
        
        screen.blit(pot_img, pot["rect"].topleft)
        
        if pot["ingredients"]: 
            text_width = len(", ".join(pot["ingredients"])) * 9 
            text_x = pot["rect"].x + (pot["rect"].width - text_width) // 2
            display_pot_ingredients_text(pot, text_x, pot["rect"].y - 25)

        if pot["status"] in ["cooking", "ready"]:
            if pot["start"] is not None:
                t = int(current_time - pot["start"])
                draw_text(f"{t}s", pot["rect"].x + (pot["rect"].width - 30) // 2, pot["rect"].y + pot["rect"].height + 5, BLACK) 
        elif pot["status"] == "burned":
            draw_text("탔음!", pot["rect"].x + (pot["rect"].width - 60) // 2, pot["rect"].y + pot["rect"].height + 5, RED)

    screen.blit(soomoong_tray_img, tray.topleft) 

    for ing in ingredients:
        screen.blit(ing["img"], ing["pos"])

    if drag_item:
        mx, my = pygame.mouse.get_pos()
        drag_pos = (mx - drag_offset[0], my - drag_offset[1])

        if "name" in drag_item:
            screen.blit(drag_item["img"], drag_pos)

        elif drag_item["type"] == "pot": 
            i = drag_item["index"]
            pot_rect = cookpots[i]["rect"]
            r = pygame.Rect(drag_pos[0], drag_pos[1], pot_rect.width, pot_rect.height)
            
            screen.blit(pot_img, (r.x, r.y))
            draw_text("서빙", r.x + (pot_rect.width - 60) // 2, r.y + pot_rect.height + 5, BLACK) 

    pygame.display.flip()
    clock.tick(30)
