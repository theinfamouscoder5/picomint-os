from framebuf import FrameBuffer, MONO_VLSB
import time

class OLED(FrameBuffer):
    def __init__(self, width, height, i2c, addr=0x3C, y_offset=0):
        self.width = width
        self.y_offset = y_offset
        self.height = height - y_offset
        self._phys_height = height
        self.i2c = i2c
        self.addr = addr
        self.pages = height // 8
        self.buffer = bytearray(self.pages * width)
        super().__init__(self.buffer, width, height, MONO_VLSB)
        time.sleep_ms(100)
        self.init_display()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytes([0x00, cmd]))

    def init_display(self):
        for cmd in (
            0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00,
            0x40, 0xAD, 0x8B, 0xA1, 0xC8, 0xDA, 0x12,
            0x81, 0x80, 0xD9, 0x1F, 0xDB, 0x40, 0xA4,
            0xA6, 0xAF
        ):
            self.write_cmd(cmd)

    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xB0 + page)
            self.write_cmd(0x02)
            self.write_cmd(0x10)
            start = page * self.width
            end = start + self.width
            self.i2c.writeto(self.addr, b'\x40' + self.buffer[start:end])

    def _fit_line(self, line, x):
        max_chars = (self.width - max(0, x)) // 8
        if max_chars <= 0:
            return ""
        if len(line) > max_chars:
            return line[:max_chars - 2] + ".." if max_chars > 2 else line[:max_chars]
        return line

    def text(self, string, x, y, color=1, spacing=2, truncate=True):
        for i, line in enumerate(string.split("\n")):
            line_y = y + i * (8 + spacing)
            if line_y + 8 > self.height:
                break
            if truncate:
                line = self._fit_line(line, x)
            super().text(line, x, line_y + self.y_offset, color)

    def center_text(self, string, y, color=1, spacing=2, truncate=True):
        for i, line in enumerate(string.split("\n")):
            line_y = y + i * (8 + spacing)
            if line_y + 8 > self.height:
                break
            x = max(0, (self.width - len(line) * 8) // 2)
            if truncate:
                line = self._fit_line(line, x)
            super().text(line, x, line_y + self.y_offset, color)

    def center_screen(self, string, color=1, spacing=2, truncate=True):
        lines = string.split("\n")
        line_height = 8 + spacing
        total_height = len(lines) * line_height - spacing
        y = max(0, (self.height - total_height) // 2)
        self.center_text(string, y, color, spacing, truncate)

    def hline(self, x, y, w, color=1):
        super().hline(x, y + self.y_offset, w, color)

    def vline(self, x, y, h, color=1):
        super().vline(x, y + self.y_offset, h, color)

    def line(self, x1, y1, x2, y2, color=1):
        super().line(x1, y1 + self.y_offset, x2, y2 + self.y_offset, color)

    def rect(self, x, y, w, h, color=1):
        super().rect(x, y + self.y_offset, w, h, color)

    def fill_rect(self, x, y, w, h, color=1):
        super().fill_rect(x, y + self.y_offset, w, h, color)

    def pixel(self, x, y, color=None):
        if color is None:
            return super().pixel(x, y + self.y_offset)
        super().pixel(x, y + self.y_offset, color)

    def progress_bar(self, progress, y=None, height=8, margin=0):
        if y is None:
            y = self.height - height
        w = self.width - (margin * 2)
        fill_w = int((w - 4) * max(0.0, min(1.0, progress)))
        self.rect(margin, y, w, height, 1)
        if fill_w > 0:
            self.fill_rect(margin + 2, y + 2, fill_w, height - 4, 1)
