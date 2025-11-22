import platform
import tkinter as tk
from threading import Thread
import time
import random
import os
import pyautogui
try:
    from pynput.mouse import Controller, Button
    PYNPUT_OK = True
    mouse = Controller()
except:
    PYNPUT_OK = False

import keyboard  # for global hotkey

running = False
hotkey_trigger = "insert"

# Folder for Spectate button templates
template_folder = "button_templates"
if not os.path.exists(template_folder):
    os.makedirs(template_folder)

# Function to press mouse button
def press_mouse(button, backend):
    osname = platform.system().lower()
    if osname == "windows" or (osname == "linux" and backend == "pynput" and PYNPUT_OK):
        mouse.press(button)
        mouse.release(button)
    elif backend == "xdotool" or backend == "wtype":
        xbtn = "1" if button == Button.left else "3"
        os.system(f"xdotool click {xbtn}")

# Function to scroll mouse 2 times with delay
def scroll_mouse(delay):
    if PYNPUT_OK:
        for _ in range(2):
            mouse.scroll(0, 1)  # scroll up
            time.sleep(delay)
    else:
        for _ in range(2):
            os.system("xdotool click 4")  # scroll up X11
            time.sleep(delay)

# Auto-click macro loop
def macro_loop(interval_min, interval_max, mouse_button, backend, scroll_delay):
    global running
    running = True
    osname = platform.system().lower()
    mouse_btn = Button.left if mouse_button == "left" else Button.right

    # Load all Spectate templates
    templates = [os.path.join(template_folder, f) for f in os.listdir(template_folder) if f.endswith(('.png','.jpg'))]

    while running:
        # Press mouse button
        press_mouse(mouse_btn, backend)

        # Check for Spectate button
        clicked = False
        for template_path in templates:
            loc = pyautogui.locateOnScreen(template_path, confidence=0.8)
            if loc:
                x, y = pyautogui.center(loc)
                pyautogui.moveTo(x, y)
                pyautogui.click()
                clicked = True
                break

        # Scroll mouse 2 times
        scroll_mouse(scroll_delay)

        wait = random.uniform(interval_min, interval_max)
        status_label.config(text=f"Pressed {mouse_button} — next in {wait:.2f}s")
        time.sleep(wait)

# GUI start/stop functions
def start_macro():
    interval_min = float(min_entry.get())
    interval_max = float(max_entry.get())
    mouse_button = mouse_choice.get()
    backend = backend_choice.get()
    scroll_delay = float(scroll_entry.get())
    thread = Thread(target=macro_loop, args=(interval_min, interval_max, mouse_button, backend, scroll_delay), daemon=True)
    thread.start()

def stop_macro():
    global running
    running = False
    status_label.config(text="Stopped")

def set_hotkey():
    global hotkey_trigger
    hotkey_trigger = hotkey_entry.get().lower().strip()
    status_label.config(text=f"Hotkey set to: {hotkey_trigger.upper()}")

def hotkey_listener():
    global running
    while True:
        keyboard.wait(hotkey_trigger)
        if not running:
            start_macro()
        else:
            stop_macro()

# ---- GUI ----
app = tk.Tk()
app.title("Deathmatch Protector - Full Automation")
app.geometry("450x500")

tk.Label(app, text="Min interval (sec):").pack()
min_entry = tk.Entry(app); min_entry.insert(0,"1"); min_entry.pack()

tk.Label(app, text="Max interval (sec):").pack()
max_entry = tk.Entry(app); max_entry.insert(0,"2"); max_entry.pack()

mouse_choice = tk.StringVar(value="left")
tk.Radiobutton(app, text="Left Click", variable=mouse_choice, value="left").pack()
tk.Radiobutton(app, text="Right Click", variable=mouse_choice, value="right").pack()

tk.Label(app, text="Linux Backend:").pack()
backend_choice = tk.StringVar(value="pynput")
tk.Radiobutton(app, text="pynput", variable=backend_choice, value="pynput").pack()
tk.Radiobutton(app, text="xdotool", variable=backend_choice, value="xdotool").pack()
tk.Radiobutton(app, text="wtype", variable=backend_choice, value="wtype").pack()

tk.Label(app, text="Scroll Delay (sec, between 2 scrolls):").pack()
scroll_entry = tk.Entry(app); scroll_entry.insert(0,"0.2"); scroll_entry.pack()

tk.Label(app, text="Global Hotkey (default: INSERT):").pack()
hotkey_entry = tk.Entry(app); hotkey_entry.insert(0,"insert"); hotkey_entry.pack()
tk.Button(app, text="Set Hotkey", command=set_hotkey).pack(pady=5)

tk.Button(app, text="START", width=20, command=start_macro).pack(pady=10)
tk.Button(app, text="STOP", width=20, command=stop_macro).pack()

status_label = tk.Label(app, text="Idle")
status_label.pack(pady=10)

# Start hotkey listener
hotkey_thread = Thread(target=hotkey_listener, daemon=True)
hotkey_thread.start()

app.mainloop()
