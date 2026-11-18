import time

SPRITE_W = 30
SPRITE_H = 24
SCALE = 2
FRAME_DELAY = 0.22

FRAMES = (
    bytes.fromhex("000000000000000000000000000000000011000000ee0000073801e03fe00fc0ff007f83d903ff07fa07fdbff00bfffe800bfff80007fff0003fffc000ffff0003fffc000ffbf0001fcfc0003e1f000000000000"),
    bytes.fromhex("0000000000000000000000000000000000000000008800000770000039c00381ff002f07f801fe1ec80ff03fd01fedff802ffff4003fffc0003fff8001fffe0007fff8000ffbf0001fcfc0003e1f000000000000"),
    bytes.fromhex("000000000000000000000000000000000011000000ee0000073801e03fe00fc0ff007f83d903ff07fa07fdbff00bfffe800bfff80007fff0003fffc000ffff0003fffc000ffbf0001fcfc0003e1f000000000000"),
    bytes.fromhex("000000000000000000000000000000000022000001dc00000e7000e07fc00bc1fe007f87b203fc0ff407fb7fe00bfffd000ffff0000fffe0007fff8001fffe0003e3b8000ffbf0001fcfc0003e1f000000000000"),
    bytes.fromhex("000000000000000000000000000000000011000000ee00f8073807f03fe03fe0ff007fc3d900ff87fa01fcbff002fffe8001fff8000ffff0003fffc000ffff0003fffc000ffbf0001fcfc0003e1f000000000000"),
)

def draw_window(fb, x, y, tick):
    fb.rect(x, y, 26, 22, 1)
    fb.hline(x - 1, y + 22, 28, 1)
    fb.vline(x + 13, y + 1, 20, 1)
    fb.hline(x + 1, y + 11, 24, 1)
    fb.pixel(x + 5, y + 3, 1)
    fb.pixel(x + 4, y + 4, 1)
    fb.pixel(x + 4, y + 5, 1)
    fb.pixel(x + 5, y + 6, 1)
    if (tick // 4) % 2 == 0:
        fb.pixel(x + 18, y + 4, 1)
        fb.pixel(x + 21, y + 15, 1)
    else:
        fb.pixel(x + 20, y + 6, 1)
        fb.pixel(x + 17, y + 17, 1)

def draw_desk_setup(fb, x, floor_y, tick):
    desk_y = floor_y - 12
    fb.hline(x, desk_y, 34, 1)
    fb.hline(x, desk_y + 1, 34, 1)
    fb.vline(x + 2, desk_y + 2, 10, 1)
    fb.vline(x + 31, desk_y + 2, 10, 1)

    mon_x = x + 13
    mon_y = desk_y - 14
    fb.rect(mon_x, mon_y, 18, 12, 1)
    fb.hline(mon_x + 5, desk_y - 2, 8, 1)
    line1_w = 5 + ((tick * 2) % 9)
    line2_w = 4 + (((tick + 2) * 3) % 10)
    fb.hline(mon_x + 2, mon_y + 3, line1_w, 1)
    fb.hline(mon_x + 2, mon_y + 6, line2_w, 1)
    if tick % 2 == 0:
        fb.pixel(mon_x + 2 + line2_w + 1, mon_y + 6, 1)

    mug_x = x + 3
    mug_y = desk_y - 5
    fb.fill_rect(mug_x, mug_y, 5, 5, 1)
    fb.pixel(mug_x + 5, mug_y + 1, 1)
    fb.pixel(mug_x + 5, mug_y + 3, 1)
    phase = tick % 4
    fb.pixel(mug_x + 1 + (phase % 2), mug_y - 2 - (phase // 2), 1)
    fb.pixel(mug_x + 3 - (phase % 2), mug_y - 4 - ((phase + 1) // 2), 1)

def draw_frame(fb, tick):
    fb.fill(0)
    w = fb.width
    h = fb.height

    floor_y = h - 3
    fb.hline(0, floor_y, w, 1)

    draw_window(fb, 2, 4, tick)

    if w >= 120:
        draw_desk_setup(fb, w - 36, floor_y, tick)

    scaled_w = SPRITE_W * SCALE
    scaled_h = SPRITE_H * SCALE
    draw_x = (w - scaled_w) // 2 - 4
    draw_y = floor_y - scaled_h + (3 * SCALE)

    sprite = FRAMES[tick % len(FRAMES)]
    sprite_len = len(sprite)
    for y in range(SPRITE_H):
        for x in range(SPRITE_W):
            bit_index = y * SPRITE_W + x
            byte_idx = bit_index >> 3
            if byte_idx < sprite_len and (sprite[byte_idx] & (1 << (7 - (bit_index & 7)))):
                fb.fill_rect(draw_x + x * SCALE, draw_y + y * SCALE, SCALE, SCALE, 1)

def run(fb, refresh=None):
    show_fn = refresh if refresh else fb.show
    tick = 0
    while True:
        draw_frame(fb, tick)
        show_fn()
        tick += 1
        time.sleep(FRAME_DELAY)

