# 8x32 WS2812 matrix on XIAO ESP32C3 D3 / GPIO 5 (snake-column wiring).
# Speeds 1-7 move one column and only the wait changes. Speeds 8-10 move a
# little farther, and never more than two columns.

import machine
import neopixel
import utime as time

WIDTH = 32
HEIGHT = 8
PIN = 5
NUM_LEDS = WIDTH * HEIGHT
SCROLL_MS = 70
_scroll_base = SCROLL_MS
_scroll_ms = SCROLL_MS
_step_num = 1
_step_den = 1
_step_live_num = 1
_step_live_den = 1
_step_acc = 0
_pace_sig = None
# SNAKE_COLUMN: even columns top->bottom, odd columns bottom->top.
WIRING = "SNAKE_COLUMN"

# 4x6 (variable width) row bitmaps. Packed to columns at import; this file
# is only imported when DISPLAY_TYPE is LED_MATRIX.
_FONT_ROWS = {
    "A": [[0,1,1,0],[1,0,0,1],[1,0,0,1],[1,1,1,1],[1,0,0,1],[1,0,0,1]],
    "B": [[1,1,1,0],[1,0,0,1],[1,1,1,0],[1,0,0,1],[1,0,0,1],[1,1,1,0]],
    "C": [[0,1,1,0],[1,0,0,1],[1,0,0,0],[1,0,0,0],[1,0,0,1],[0,1,1,0]],
    "D": [[1,1,1,0],[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,1,1,0]],
    "E": [[1,1,1,1],[1,0,0,0],[1,1,1,0],[1,0,0,0],[1,0,0,0],[1,1,1,1]],
    "F": [[1,1,1,1],[1,0,0,0],[1,1,1,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],
    "G": [[0,1,1,0],[1,0,0,1],[1,0,0,0],[1,0,1,1],[1,0,0,1],[0,1,1,0]],
    "H": [[1,0,0,1],[1,0,0,1],[1,1,1,1],[1,0,0,1],[1,0,0,1],[1,0,0,1]],
    "I": [[1,1,1],[0,1,0],[0,1,0],[0,1,0],[0,1,0],[1,1,1]],
    "J": [[0,0,1],[0,0,1],[0,0,1],[0,0,1],[1,0,1],[0,1,0]],
    "K": [[1,0,0,1],[1,0,1,0],[1,1,0,0],[1,0,1,0],[1,0,1,0],[1,0,0,1]],
    "L": [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,1,1,1]],
    "M": [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
    "N": [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[1,0,0,0,1]],
    "O": [[0,1,1,0],[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
    "P": [[1,1,1,0],[1,0,0,1],[1,0,0,1],[1,1,1,0],[1,0,0,0],[1,0,0,0]],
    "Q": [[0,1,1,0],[1,0,0,1],[1,0,0,1],[1,0,0,1],[0,1,1,0],[0,0,0,1]],
    "R": [[1,1,1,0],[1,0,0,1],[1,0,0,1],[1,1,1,0],[1,0,0,1],[1,0,0,1]],
    "S": [[0,1,1,1],[1,0,0,0],[0,1,1,0],[0,0,0,1],[1,0,0,1],[0,1,1,0]],
    "T": [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
    "U": [[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
    "V": [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,1,0,1,0],[0,0,1,0,0]],
    "W": [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,0,0,0,1]],
    "X": [[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1]],
    "Y": [[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
    "Z": [[1,1,1,1,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
    "0": [[0,1,1,0],[1,0,0,1],[1,0,1,1],[1,1,0,1],[1,0,0,1],[0,1,1,0]],
    "1": [[0,1,0],[1,1,0],[0,1,0],[0,1,0],[0,1,0],[1,1,1]],
    "2": [[0,1,1,0],[1,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0],[1,1,15,1]],
    "3": [[1,1,1,0],[0,0,0,1],[0,1,1,0],[0,0,0,1],[0,0,0,1],[1,1,1,0]],
    "4": [[0,0,1,0],[0,1,1,0],[1,0,1,0],[1,1,1,1],[0,0,1,0],[0,0,1,0]],
    "5": [[1,1,1,1],[1,0,0,0],[1,1,1,0],[0,0,0,1],[1,0,0,1],[0,1,1,0]],
    "6": [[0,1,1,0],[1,0,0,0],[1,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
    "7": [[1,1,1,1],[0,0,0,1],[0,0,1,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
    "8": [[0,1,1,0],[1,0,0,1],[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]],
    "9": [[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,1],[0,0,0,1],[0,1,1,0]],
    "=": [[0,0,0,0],[1,1,1,1],[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    "/": [[0,0,0,1],[0,0,1,0],[0,0,1,0],[0,1,0,0],[0,1,0,0],[1,0,0,0]],
    "-": [[0,0,0,0],[0,0,0,0],[1,1,1,1],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    "+": [[0,0,0,0],[0,0,1,0],[0,0,1,0],[1,1,1,1],[0,0,1,0],[0,0,1,0]],
    " ": [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    ":": [[0,0,0],[0,1,0],[0,0,0],[0,0,0],[0,1,0],[0,0,0]],
    ".": [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,1,0],[0,0,0]],
    ",": [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,1,0],[1,0,0]],
    "!": [[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,0,0],[0,1,0]],
    "?": [[0,1,1,0],[1,0,0,1],[0,0,1,0],[0,1,0,0],[0,0,0,0],[0,1,0,0]],
    "$": [[0,1,1,1,0],[1,0,1,0,0],[0,1,1,1,0],[0,0,1,0,1],[0,1,1,1,0]],
    "@": [[0,1,1,0],[1,0,0,1],[1,0,1,1],[1,0,1,1],[1,0,0,0],[0,1,1,0]],
    "#": [[0,1,0,1,0],[1,1,1,1,1],[0,1,0,1,0],[1,1,1,1,1],[0,1,0,1,0],[0,0,0,0,0]],
    "%": [[1,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,1],[0,0,0,0,0]],
    "&": [[0,1,1,0],[1,0,0,1],[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,1]],
    "*": [[0,0,0,0,0],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[0,0,0,0,0],[0,0,0,0,0]],
    "(": [[0,0,1],[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,0,1]],
    ")": [[1,0,0],[0,1,0],[0,1,0],[0,1,0],[0,1,0],[1,0,0]],
    "[": [[1,1,0],[1,0,0],[1,0,0],[1,0,0],[1,0,0],[1,1,0]],
    "]": [[0,1,1],[0,0,1],[0,0,1],[0,0,1],[0,0,1],[0,1,1]],
    "{": [[0,0,1],[0,1,0],[1,0,0],[0,1,0],[0,1,0],[0,0,1]],
    "}": [[1,0,0],[0,1,0],[0,0,1],[0,1,0],[0,1,0],[1,0,0]],
    "<": [[0,0,1],[0,1,0],[1,0,0],[0,1,0],[0,0,1],[0,0,0]],
    ">": [[1,0,0],[0,1,0],[0,0,1],[0,1,0],[1,0,0],[0,0,0]],
    "^": [[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
    "_": [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[1,1,1,1]],
    "|": [[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,1,0]],
    "~": [[0,0,0,0,0],[0,1,1,0,1],[1,0,0,1,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
    '"': [[1,0,1,0],[1,0,1,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],
    "'": [[0,1,0],[0,1,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],
    "`": [[1,0,0],[0,1,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]],
}


def _pack_rows(rows):
    width = 0
    for row in rows:
        n = len(row)
        if n > width:
            width = n
    cols = [0] * width
    y = 0
    for row in rows:
        if y > 5:
            break
        x = 0
        for bit in row:
            if bit:
                cols[x] |= (1 << y)
            x += 1
        y += 1
    return tuple(cols)


_FONT = {}
for _ch, _rows in _FONT_ROWS.items():
    _FONT[_ch] = _pack_rows(_rows)
del _FONT_ROWS

_np = None
_index = None
_columns = []
_col_colors = []
_offset = 0
_pass = 0
_scroll_times = 1
_last_ms = 0
_color = (255, 180, 48)
_text = ""
_sleep_cleared = False


def _pixel_index(x, y):
    if WIRING == "SNAKE_COLUMN":
        if x % 2 == 0:
            return x * HEIGHT + y
        return x * HEIGHT + (HEIGHT - 1 - y)
    if WIRING == "COLUMN_MAJOR":
        return x * HEIGHT + y
    if WIRING == "SNAKE_ROW":
        if y % 2 == 0:
            return y * WIDTH + x
        return y * WIDTH + (WIDTH - 1 - x)
    return y * WIDTH + x


def _build_indices():
    table = []
    for x in range(WIDTH):
        col = []
        for y in range(HEIGHT):
            col.append(_pixel_index(x, y))
        table.append(col)
    return table


def _text_columns(text):
    cols = []
    for ch in text.upper():
        glyph = _FONT.get(ch) or _FONT.get(" ")
        for byte in glyph:
            cols.append(byte)
        cols.append(0)
    for _ in range(WIDTH):
        cols.append(0)
    return cols


def active():
    return _np is not None


def init():
    global _np, _index, _columns, _col_colors, _offset, _last_ms
    try:
        _np = neopixel.NeoPixel(machine.Pin(PIN), NUM_LEDS)
        _index = _build_indices()
        _np.fill((0, 0, 0))
        _np.write()
        _columns = []
        _col_colors = []
        _offset = 0
        _last_ms = 0
        print("LED matrix GPIO", PIN, "x", NUM_LEDS)
        return True
    except Exception as e:
        _np = None
        print("LED matrix skipped:", e)
        return False


def set_text(text, color=(255, 180, 48)):
    set_segments([(text, color)])


def set_scroll_ms(ms, step_num=1, step_den=1):
    """Store the slider pace. Zero ms means move on every frame."""
    global _scroll_base, _step_num, _step_den
    try:
        base = int(ms)
    except Exception:
        base = SCROLL_MS
    if base < 0:
        base = 0
    elif base > 400:
        base = 400
    try:
        num = int(step_num)
        den = int(step_den)
    except Exception:
        num = 1
        den = 1
    if num < 1:
        num = 1
    if den < 1:
        den = 1
    if num > den * 2:
        num = den * 2
    _scroll_base = base
    _step_num = num
    _step_den = den
    _apply_length_speed()


def _apply_length_speed():
    """The slider wait is the pace. The same speed stays smooth on a long line."""
    global _scroll_ms, _step_live_num, _step_live_den, _pace_sig
    ms = _scroll_base
    if ms < 0:
        ms = 0
    if ms > 400:
        ms = 400
    num = _step_num
    den = _step_den
    real = len(_columns) - WIDTH
    sig = (ms, num, den)
    if sig != _pace_sig and _columns:
        _pace_sig = sig
        print("Matrix pace", real, "cols", ms, "ms", "step", num, "/", den)
    _scroll_ms = ms
    _step_live_num = num
    _step_live_den = den


def set_scroll_times(n):
    global _scroll_times
    try:
        _scroll_times = max(1, min(10, int(n)))
    except Exception:
        _scroll_times = 1


def set_segments(segments):
    global _columns, _col_colors, _offset, _pass, _color, _text, _step_acc
    parts = []
    for text, color in segments or []:
        t = str(text or "").strip()
        if t:
            parts.append((t, color or (255, 180, 48)))
    if not parts:
        _text = ""
        _columns = []
        _col_colors = []
        _offset = 0
        _pass = 0
        _step_acc = 0
        clear()
        _apply_length_speed()
        return
    key = "|".join(p[0] + str(p[1]) for p in parts)
    if key == _text and _columns:
        return
    _text = key
    cols = []
    colors = []
    for _ in range(WIDTH):
        cols.append(0)
        colors.append((0, 0, 0))
    for text, color in parts:
        for ch in text.upper():
            glyph = _FONT.get(ch) or _FONT.get(" ")
            for byte in glyph:
                cols.append(byte)
                colors.append(color)
            cols.append(0)
            colors.append(color)
        for _ in range(3):
            cols.append(0)
            colors.append(color)
    for _ in range(WIDTH):
        cols.append(0)
        colors.append((0, 0, 0))
    _columns = cols
    _col_colors = colors
    _color = parts[0][1]
    _offset = 0
    _pass = 0
    _step_acc = 0
    _apply_length_speed()


_blank = None


def _clear_pixels():
    """Clear the LED buffer in one copy. NeoPixel.fill walks every pixel in Python."""
    global _blank
    buf = getattr(_np, "buf", None)
    if not buf:
        _np.fill((0, 0, 0))
        return
    n = len(buf)
    if _blank is None or len(_blank) != n:
        _blank = bytes(n)
    buf[:] = _blank


def clear():
    if _np is None:
        return
    _clear_pixels()
    _np.write()


def tick(level=8, sleeping=False):
    global _offset, _pass, _last_ms, _sleep_cleared
    if _np is None or _index is None:
        return False
    if sleeping:
        if not _sleep_cleared:
            clear()
            _sleep_cleared = True
        return False
    _sleep_cleared = False
    now = time.ticks_ms()
    if _last_ms and _scroll_ms and time.ticks_diff(now, _last_ms) < _scroll_ms:
        return False
    _last_ms = now
    if not _columns:
        return False
    n = len(_columns)
    span = max(1, n - WIDTH)
    scale = max(0, min(255, int(level)))
    _clear_pixels()
    if scale <= 0:
        _np.write()
        return _advance(span)
    for x in range(WIDTH):
        idx = _offset + x
        if idx < 0 or idx >= n:
            continue
        bits = _columns[idx] << 1
        if not bits:
            continue
        rgb = _col_colors[idx] if idx < len(_col_colors) else _color
        peak = rgb[0]
        if rgb[1] > peak:
            peak = rgb[1]
        if rgb[2] > peak:
            peak = rgb[2]
        if peak <= 0:
            continue
        pix = (rgb[0] * scale // peak, rgb[1] * scale // peak, rgb[2] * scale // peak)
        for y in range(HEIGHT):
            if bits & (1 << y):
                _np[_index[x][y]] = pix
    _np.write()
    return _advance(span)


def _advance(span):
    global _offset, _pass, _step_acc
    den = _step_live_den if _step_live_den >= 1 else 1
    _step_acc += _step_live_num if _step_live_num >= 1 else 1
    step = _step_acc // den
    _step_acc -= step * den
    if step < 1:
        step = 1
        _step_acc = 0
    elif step > 2:
        step = 2
        _step_acc = 0
    _offset += step
    if _offset >= span:
        _offset = 0
        _pass += 1
        if _pass >= _scroll_times:
            _pass = 0
            return True
    return False
