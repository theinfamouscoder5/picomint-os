class Button:
    def __init__(self, label, x, y, w=None, h=12, selected=False, on_click=None):
        self.label = label
        self.x = x
        self.y = y
        self.w = w if w is not None else (len(label) * 8) + 8
        self.h = h
        self.selected = selected
        self.on_click = on_click

    def draw(self, oled):
        text_x = self.x + max(2, (self.w - len(self.label) * 8) // 2)
        text_y = self.y + max(1, (self.h - 8) // 2)

        if self.selected:
            oled.fill_rect(self.x, self.y, self.w, self.h, 1)
            oled.text(self.label, text_x, text_y, 0)
        else:
            oled.rect(self.x, self.y, self.w, self.h, 1)
            oled.text(self.label, text_x, text_y, 1)

    def press(self):
        if self.on_click:
            self.on_click()

class ButtonStack:
    def __init__(self, buttons, x=0, y=14, w=None, spacing=3):
        self.buttons = buttons
        self.x = x
        self.y = y
        self.w = w
        self.spacing = spacing
        self.selected_idx = 0
        self.scroll_offset = 0

    def move(self, delta):
        if self.buttons:
            self.selected_idx = (self.selected_idx + delta) % len(self.buttons)

    def press_selected(self):
        if self.buttons:
            self.buttons[self.selected_idx].press()

    def draw(self, oled):
        if not self.buttons:
            return

        row_h = self.buttons[0].h + self.spacing
        avail_h = oled.height - self.y + self.spacing
        max_visible = max(1, avail_h // row_h)

        if self.selected_idx < self.scroll_offset:
            self.scroll_offset = self.selected_idx
        elif self.selected_idx >= self.scroll_offset + max_visible:
            self.scroll_offset = self.selected_idx - max_visible + 1

        needs_scroll = len(self.buttons) > max_visible
        bar_space = 4 if needs_scroll else 0
        target_w = (self.w if self.w is not None else oled.width) - bar_space

        cur_y = self.y
        for i in range(self.scroll_offset, min(len(self.buttons), self.scroll_offset + max_visible)):
            btn = self.buttons[i]
            btn.x = self.x
            btn.y = cur_y
            btn.w = target_w
            btn.selected = (i == self.selected_idx)
            btn.draw(oled)
            cur_y += btn.h + self.spacing

        if needs_scroll:
            track_x = (self.x + target_w + 2)
            track_h = oled.height - self.y
            thumb_h = max(4, (track_h * max_visible) // len(self.buttons))
            max_scroll = len(self.buttons) - max_visible
            thumb_y = self.y + ((track_h - thumb_h) * self.scroll_offset) // max_scroll
            oled.vline(track_x, self.y, track_h, 1)
            oled.fill_rect(track_x - 1, thumb_y, 3, thumb_h, 1)
