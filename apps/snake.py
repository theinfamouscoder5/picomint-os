import keypad
import random
import time

CELL = 4

def run(oled):
    header_h = 10
    cols = oled.width // CELL
    rows = (oled.height - header_h) // CELL
    offset_x = (oled.width - (cols * CELL)) // 2
    offset_y = header_h + ((oled.height - header_h - (rows * CELL)) // 2)

    def spawn_food(snake):
        while True:
            pos = (random.randint(0, cols - 1), random.randint(0, rows - 1))
            if pos not in snake:
                return pos

    start_x = cols // 2
    start_y = rows // 2
    snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
    direction = (1, 0)
    food = spawn_food(snake)
    score = 0
    speed_ms = 240
    last_move = time.ticks_ms()

    while True:
        key = keypad.get_key()
        if key:
            k = key.lower()
            if k == "esc":
                return
            elif k in ("w", "up") and direction != (0, 1):
                direction = (0, -1)
            elif k in ("s", "down") and direction != (0, -1):
                direction = (0, 1)
            elif k in ("a", "left") and direction != (1, 0):
                direction = (-1, 0)
            elif k in ("d", "right") and direction != (-1, 0):
                direction = (1, 0)

        if time.ticks_diff(time.ticks_ms(), last_move) >= speed_ms:
            last_move = time.ticks_ms()
            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            if (
                new_head[0] < 0 or new_head[0] >= cols or
                new_head[1] < 0 or new_head[1] >= rows or
                new_head in snake
            ):
                oled.fill(0)
                oled.center_screen(f"GAME OVER\nScore: {score}\n[ENT] Retry\n[ESC] Exit")
                oled.show()
                while True:
                    k = keypad.get_key()
                    if k:
                        k = k.lower()
                        if k == "esc":
                            return
                        elif k in ("enter", " "):
                            snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
                            direction = (1, 0)
                            food = spawn_food(snake)
                            score = 0
                            speed_ms = 240
                            last_move = time.ticks_ms()
                            break
                    time.sleep_ms(20)
                continue

            snake.insert(0, new_head)

            if new_head == food:
                score += 1
                food = spawn_food(snake)
                speed_ms = max(110, speed_ms - 6)
            else:
                snake.pop()

            oled.fill(0)
            oled.text(f"SNAKE  {score}", 0, 0)
            oled.rect(offset_x - 1, offset_y - 1, cols * CELL + 2, rows * CELL + 2, 1)

            fx = offset_x + food[0] * CELL
            fy = offset_y + food[1] * CELL
            oled.rect(fx, fy, CELL, CELL, 1)

            for i, (sx, sy) in enumerate(snake):
                px = offset_x + sx * CELL
                py = offset_y + sy * CELL
                if i == 0:
                    oled.fill_rect(px, py, CELL, CELL, 1)
                else:
                    oled.fill_rect(px + 1, py + 1, CELL - 2, CELL - 2, 1)

            oled.show()

        time.sleep_ms(10)

