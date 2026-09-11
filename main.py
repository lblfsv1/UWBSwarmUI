import pygame
from datetime import datetime
import serial

pygame.init()


# =========================================================
# Serial Communication Configuration
# =========================================================


ser = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=0.1)


# =========================================================
# 画面設定
# =========================================================


screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("UWB Swarm System Monitor")
pygame.mouse.set_visible(False)

WIDTH, HEIGHT = screen.get_size()

clock = pygame.time.Clock()


# =========================================================
# 色
# =========================================================

BG = (4, 17, 20)
PANEL_BG = (6, 25, 28)

GREEN = (0, 255, 180)
GREEN_DARK = (0, 110, 90)

YELLOW = (255, 215, 0)
RED = (255, 70, 70)

WHITE = (230, 245, 245)
GRAY = (130, 170, 170)

GRID = (10, 55, 58)


# =========================================================
# フォント
# =========================================================

font_big = pygame.font.SysFont(None, 34)
font_mid = pygame.font.SysFont(None, 26)
font_small = pygame.font.SysFont(None, 20)
font_tiny = pygame.font.SysFont(None, 17)


# =========================================================
# レイアウト
# =========================================================

LEFT_WIDTH = int(WIDTH * 0.65)

RIGHT_X = LEFT_WIDTH
RIGHT_WIDTH = WIDTH - LEFT_WIDTH

RADAR_CENTER = (
    LEFT_WIDTH // 2,
    HEIGHT // 2 + 25
)

RADAR_RADIUS = int(
    min(LEFT_WIDTH, HEIGHT) * 0.36
)

MAX_DISTANCE = 15.0


# =========================================================
# 自車 Heading
# =========================================================

MY_HEADING = 30.0


# =========================================================
# 車両データ
# =========================================================

vehicles = [
    {
        "id": "A",
        "distance": 12.5,
        "heading": 80.0
    },
    {
        "id": "B",
        "distance": 8.1,
        "heading": 200.0
    },
    {
        "id": "C",
        "distance": 4.2,
        "heading": 310.0
    }
]


# =========================================================
# 車両画像読み込み
# =========================================================

car_images = {
    "A": pygame.image.load(
        "assets/red_forklift.jpg"
    ).convert_alpha(),

    "B": pygame.image.load(
        "assets/blue_forklift.jpg"
    ).convert_alpha(),

    "C": pygame.image.load(
        "assets/yellow_forklift.jpg"
    ).convert_alpha()
}


# =========================================================
# 白背景を透明化
# =========================================================

def remove_white_background(image):

    image = image.copy()
    image.lock()

    for x in range(image.get_width()):
        for y in range(image.get_height()):

            r, g, b, a = image.get_at((x, y))

            if r > 245 and g > 245 and b > 245:
                image.set_at(
                    (x, y),
                    (255, 255, 255, 0)
                )

    image.unlock()

    return image


for key in car_images:

    car_images[key] = remove_white_background(
        car_images[key]
    )


# =========================================================
# 距離 → ピクセル変換
# =========================================================

def distance_to_pixel(distance):

    return int(
        distance
        / MAX_DISTANCE
        * RADAR_RADIUS
    )


# =========================================================
# 危険判定
# =========================================================

def get_status(distance):

    if distance < 5.0:
        return "DANGER"

    elif distance < 10.0:
        return "CAUTION"

    else:
        return "NORMAL"


# =========================================================
# 危険度に応じた色
# =========================================================

def get_status_color(status):

    if status == "NORMAL":
        return GREEN

    if status == "CAUTION":
        return YELLOW

    if status == "DANGER":
        return RED

    return WHITE


# =========================================================
# 相対Heading
# =========================================================

def relative_heading(
    my_heading,
    other_heading
):

    return (
        other_heading
        - my_heading
        + 180
    ) % 360 - 180


# =========================================================
# 相対方向の文字
# =========================================================

def relative_direction(angle):

    if -22.5 <= angle < 22.5:
        return "SAME"

    elif 22.5 <= angle < 67.5:
        return "RIGHT 45"

    elif 67.5 <= angle < 112.5:
        return "RIGHT"

    elif 112.5 <= angle < 157.5:
        return "BACK RIGHT"

    elif angle >= 157.5 or angle < -157.5:
        return "OPPOSITE"

    elif -157.5 <= angle < -112.5:
        return "BACK LEFT"

    elif -112.5 <= angle < -67.5:
        return "LEFT"

    elif -67.5 <= angle < -22.5:
        return "LEFT 45"

    return ""


# =========================================================
# Vehicle検索
# =========================================================

def get_vehicle(vehicle_id):

    for vehicle in vehicles:

        if vehicle["id"] == vehicle_id:
            return vehicle

    return None


# =========================================================
# テキスト描画
# =========================================================

def draw_text(
    text,
    font,
    color,
    x,
    y
):

    surface = font.render(
        str(text),
        True,
        color
    )

    screen.blit(
        surface,
        (x, y)
    )


# =========================================================
# パネル描画
# =========================================================

def draw_panel(
    rect,
    border_color=GREEN_DARK
):

    pygame.draw.rect(
        screen,
        PANEL_BG,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        border_color,
        rect,
        2,
        border_radius=8
    )


# =========================================================
# 背景グリッド
# =========================================================

def draw_grid():

    step = 40

    for x in range(
        0,
        LEFT_WIDTH,
        step
    ):

        pygame.draw.line(
            screen,
            GRID,
            (x, 70),
            (x, HEIGHT),
            1
        )

    for y in range(
        70,
        HEIGHT,
        step
    ):

        pygame.draw.line(
            screen,
            GRID,
            (0, y),
            (LEFT_WIDTH, y),
            1
        )


# =========================================================
# 車両画像表示
# =========================================================

def draw_car_image(
    image,
    center,
    angle,
    size=(45, 75)
):

    image = pygame.transform.smoothscale(
        image,
        size
    )

    rotated = pygame.transform.rotate(
        image,
        -angle
    )

    rect = rotated.get_rect(
        center=center
    )

    screen.blit(
        rotated,
        rect
    )


# =========================================================
# ヘッダー
# =========================================================

def draw_header():

    draw_text(
        "FORKLIFT SWARM MONITOR",
        font_big,
        WHITE,
        20,
        12
    )

    draw_text(
        "PROXIMITY WARNING SYSTEM",
        font_small,
        GRAY,
        20,
        45
    )

    now = datetime.now()

    time_text = now.strftime(
        "%H:%M:%S"
    )

    draw_text(
        time_text,
        font_small,
        WHITE,
        WIDTH - 90,
        20
    )

    draw_text(
        f"YOU Heading: {MY_HEADING:.0f} deg",
        font_small,
        GREEN,
        RIGHT_X + 12,
        50
    )


# =========================================================
# 左側レーダー
# =========================================================

def draw_radar():

    cx, cy = RADAR_CENTER

    # 十字線
    pygame.draw.line(
        screen,
        GRAY,
        (
            cx - RADAR_RADIUS,
            cy
        ),
        (
            cx + RADAR_RADIUS,
            cy
        ),
        1
    )

    pygame.draw.line(
        screen,
        GRAY,
        (
            cx,
            cy - RADAR_RADIUS
        ),
        (
            cx,
            cy + RADAR_RADIUS
        ),
        1
    )


    # -----------------------------------------
    # 基準距離リング
    # -----------------------------------------

    base_distances = [
        (5, RED),
        (10, YELLOW),
        (15, GREEN)
    ]

    for distance, color in base_distances:

        radius = distance_to_pixel(
            distance
        )

        pygame.draw.circle(
            screen,
            color,
            RADAR_CENTER,
            radius,
            1
        )

        draw_text(
            f"{distance} m",
            font_tiny,
            color,
            cx + 5,
            cy - radius + 3
        )


    # -----------------------------------------
    # 各vehicleまでの距離円
    # -----------------------------------------

    for vehicle in vehicles:

        status = get_status(
            vehicle["distance"]
        )

        color = get_status_color(
            status
        )

        radius = distance_to_pixel(
            vehicle["distance"]
        )

        pygame.draw.circle(
            screen,
            color,
            RADAR_CENTER,
            radius,
            3
        )

        label_x = (
            cx
            + radius
            - 25
        )

        label_y = (
            cy
            - 18
        )

        draw_text(
            vehicle["id"],
            font_mid,
            color,
            label_x,
            label_y
        )


    # -----------------------------------------
    # YOU
    # -----------------------------------------

    pygame.draw.circle(
        screen,
        GREEN,
        RADAR_CENTER,
        5
    )

    draw_text(
        "YOU",
        font_mid,
        WHITE,
        cx - 23,
        cy + 15
    )


# =========================================================
# 右側 Vehicle List
# =========================================================

def draw_vehicle_list():

    x = RIGHT_X + 12

    panel_width = (
        RIGHT_WIDTH - 24
    )

    draw_text(
        "VEHICLES",
        font_mid,
        WHITE,
        x,
        80
    )

    y = 110


    for vehicle in vehicles:

        # -----------------------------------------
        # 自動危険判定
        # -----------------------------------------

        status = get_status(
            vehicle["distance"]
        )

        color = get_status_color(
            status
        )


        # -----------------------------------------
        # 相対Heading
        # -----------------------------------------

        relative = relative_heading(
            MY_HEADING,
            vehicle["heading"]
        )

        direction = relative_direction(
            relative
        )


        # -----------------------------------------
        # パネル
        # -----------------------------------------

        rect = pygame.Rect(
            x,
            y,
            panel_width,
            105
        )

        draw_panel(
            rect,
            color
        )


        # -----------------------------------------
        # Vehicle ID
        # -----------------------------------------

        draw_text(
            f'VEHICLE {vehicle["id"]}',
            font_mid,
            color,
            x + 12,
            y + 10
        )


        # -----------------------------------------
        # Status
        # -----------------------------------------

        draw_text(
            status,
            font_small,
            color,
            x + 125,
            y + 13
        )


        # -----------------------------------------
        # Distance
        # -----------------------------------------

        draw_text(
            f'Distance: {vehicle["distance"]:.1f} m',
            font_small,
            WHITE,
            x + 12,
            y + 42
        )


        # -----------------------------------------
        # Relative Heading
        # -----------------------------------------

        draw_text(
            f'Relative: {relative:+.0f} deg',
            font_small,
            WHITE,
            x + 12,
            y + 65
        )


        # -----------------------------------------
        # Relative direction
        # -----------------------------------------

        draw_text(
            direction,
            font_tiny,
            GRAY,
            x + 12,
            y + 85
        )


        # -----------------------------------------
        # 車両画像
        # -----------------------------------------

        car_image = car_images[
            vehicle["id"]
        ]

        draw_car_image(
            car_image,
            (
                x
                + panel_width
                - 48,

                y
                + 55
            ),
            relative,
            size=(42, 70)
        )


        y += 115


# =========================================================
# 警告パネル
# =========================================================

def draw_warning():

    dangerous_vehicles = []

    for vehicle in vehicles:

        status = get_status(
            vehicle["distance"]
        )

        if status == "DANGER":

            dangerous_vehicles.append(
                vehicle
            )


    if len(dangerous_vehicles) == 0:
        return


    # 一番近いvehicleを選ぶ
    dangerous_vehicle = min(
        dangerous_vehicles,
        key=lambda v: v["distance"]
    )


    x = RIGHT_X + 12

    rect = pygame.Rect(
        x,
        465,
        RIGHT_WIDTH - 24,
        110
    )

    draw_panel(
        rect,
        RED
    )


    draw_text(
        "!! COLLISION RISK",
        font_mid,
        RED,
        x + 12,
        478
    )


    draw_text(
        f'VEHICLE {dangerous_vehicle["id"]}',
        font_small,
        WHITE,
        x + 12,
        515
    )


    draw_text(
        f'Distance: {dangerous_vehicle["distance"]:.1f} m',
        font_small,
        WHITE,
        x + 12,
        540
    )


# =========================================================
# メインループ
# =========================================================

running = True


while running:

    #-----------------------------------------------------
    # Serial Communication
    #-----------------------------------------------------

    if ser.in_waiting > 0:

        line = ser.readline().decode("utf-8").strip()

        data = line.split(",")

        if len(data) == 1:

            MY_HEADING = float(data[0])

        if len(data) == 3:

            vehicle = get_vehicle(data[0])

            vehicle["distance"] = float(data[1])

            vehicle["heading"] = float(data[2])


    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        if event.type == pygame.KEYDOWN:


            # -----------------------------------------
            # ESC
            # -----------------------------------------

            if event.key == pygame.K_ESCAPE:

                running = False


            # -----------------------------------------
            # ← 自車Headingを左へ
            # -----------------------------------------

            elif event.key == pygame.K_LEFT:

                MY_HEADING -= 10

                MY_HEADING %= 360


            # -----------------------------------------
            # → 自車Headingを右へ
            # -----------------------------------------

            elif event.key == pygame.K_RIGHT:

                MY_HEADING += 10

                MY_HEADING %= 360


            # -----------------------------------------
            # ↑ Vehicle Cを近づける
            # -----------------------------------------

            elif event.key == pygame.K_UP:

                vehicle_c = get_vehicle("C")

                if vehicle_c is not None:

                    vehicle_c["distance"] -= 0.5

                    if vehicle_c["distance"] < 0.5:

                        vehicle_c["distance"] = 0.5


            # -----------------------------------------
            # ↓ Vehicle Cを遠ざける
            # -----------------------------------------

            elif event.key == pygame.K_DOWN:

                vehicle_c = get_vehicle("C")

                if vehicle_c is not None:

                    vehicle_c["distance"] += 0.5

                    if vehicle_c["distance"] > MAX_DISTANCE:

                        vehicle_c["distance"] = MAX_DISTANCE


    # =====================================================
    # 描画
    # =====================================================

    screen.fill(
        BG
    )

    draw_grid()

    draw_header()

    draw_radar()

    draw_vehicle_list()

    draw_warning()


    pygame.display.flip()

    clock.tick(
        30
    )


pygame.quit()
