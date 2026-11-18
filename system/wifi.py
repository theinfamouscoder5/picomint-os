import keypad
import network
import time
from ui import Button, ButtonStack

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def _show_msg(oled, text):
    oled.fill(0)
    oled.center_screen(text)
    oled.show()

def _connect_prompt(oled, ssid):
    password = ""
    max_visible = max(4, (oled.width // 8) - 6)

    while True:
        oled.fill(0)
        oled.text("Wi-Fi Password", 0, 0)
        oled.hline(0, 10, oled.width, 1)
        oled.text(f"Net: {ssid}", 0, 14)

        visible_pwd = password[-max_visible:] if len(password) > max_visible else password
        prefix = "Pwd:<" if len(password) > max_visible else "Pwd: "
        oled.text(f"{prefix}{visible_pwd}_", 0, 26, truncate=False)

        oled.text("[ENTER] Connect", 0, oled.height - 8)
        oled.show()

        key = keypad.get_key()
        if key:
            k = key.lower()
            if k == "esc":
                return
            elif k == "enter":
                break
            elif k == "backspace":
                password = password[:-1]
            else:
                password += key
        time.sleep_ms(20)
    
    _show_msg(oled, f"Connecting to\n{ssid}...")
    wlan.disconnect()
    wlan.connect(ssid, password)
    
    for _ in range(20):
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            _show_msg(oled, f"Connected\n{ip}")
            time.sleep(1.5)
            return
        time.sleep_ms(500)
    
    _show_msg(oled, "Connection failed :(\nCheck password")
    time.sleep(1.5)

def _scan_networks(oled):
    _show_msg(oled, "Scanning\nWi-Fi...")
    nets = wlan.scan()
    
    unique = {}
    for net in nets:
        ssid = net[0].decode("utf-8", "ignore").strip()
        rssi = net[3]
        if ssid and (ssid not in unique or rssi > unique[ssid]):
            unique[ssid] = rssi
    
    sorted_ssids = sorted(unique.keys(), key=lambda s: unique[s], reverse=True)
    
    if not sorted_ssids:
        _show_msg(oled, "No networks found")
        time.sleep(1.2)
        return
    
    scan_menu = ButtonStack([
        Button(ssid, 0, 0, on_click=lambda s=ssid: _connect_prompt(oled, s))
        for ssid in sorted_ssids
    ], x=0, y=14, spacing=3)
    
    while True:
        oled.fill(0)
        oled.text(f"Found ({len(sorted_ssids)})", 0, 0)
        oled.hline(0, 10, oled.width, 1)
        scan_menu.draw(oled)
        oled.show()
        
        key = keypad.get_key()
        if key:
            k = key.lower()
            if k == "esc":
                return
            elif k in ("w", "up"):
                scan_menu.move(-1)
            elif k in ("s", "down"):
                scan_menu.move(1)
            elif k == "enter":
                scan_menu.press_selected()
                if wlan.isconnected():
                    return
        time.sleep_ms(20)

def run(oled):
    wifi_menu = ButtonStack([
        Button("Scan Networks", 0, 0, on_click=lambda: _scan_networks(oled)),
        Button("Disconnect", 0, 0, on_click=lambda: wlan.disconnect()),
    ], x=0, y=24, spacing=3)

    while True:
        oled.fill(0)
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            oled.text("Wi-Fi: ON", 0, 0)
            oled.text(ip, 0, 11)
        else:
            oled.text("Wi-Fi: OFF", 0, 0)
            oled.text("Not connected", 0, 11)

        oled.hline(0, 20, oled.width, 1)
        wifi_menu.draw(oled)
        oled.show()

        key = keypad.get_key()
        if key:
            k = key.lower()
            if k == "esc":
                return
            elif k in ("w", "up"):
                wifi_menu.move(-1)
            elif k in ("s", "down"):
                wifi_menu.move(1)
            elif k == "enter":
                wifi_menu.press_selected()

        time.sleep_ms(20)
