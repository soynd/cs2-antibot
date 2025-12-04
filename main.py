import tkinter as tk
from threading import Thread
import time, random, os, platform, pyautogui, json
from pynput import keyboard
try:
    from pynput.mouse import Controller, Button
    PYNPUT_OK = True
    mouse = Controller()
except ImportError:
    PYNPUT_OK = False
    Button = None

running = False
template_folder = "button_templates"
SETTINGS_FILE = "settings.json"

if not os.path.exists(template_folder):
    os.makedirs(template_folder)

# --- Macro logic ---
def press_mouse(button, backend):
    osname = platform.system().lower()
    if PYNPUT_OK and (osname == "windows" or (osname == "linux" and backend == "pynput")):
        mouse.press(button); mouse.release(button)
    elif backend in ("xdotool","wtype"):
        xbtn = "1" if button == Button.left else "3"
        os.system(f"xdotool click {xbtn}")
    else:
        pyautogui.click()

def scroll_mouse(delay, x=None, y=None):
    if x and y:
        pyautogui.moveTo(x, y)
    if PYNPUT_OK:
        for _ in range(2):
            mouse.scroll(0,1); time.sleep(delay)
    else:
        for _ in range(2):
            os.system("xdotool click 4"); time.sleep(delay)

def macro_loop(interval_min, interval_max, mouse_button, backend, scroll_delay, coord):
    global running
    running = True
    mouse_btn = Button.left if (Button and mouse_button=="left") else Button.right if Button else None
    templates = [os.path.join(template_folder,f) for f in os.listdir(template_folder) if f.endswith(('.png','.jpg'))]

    while running:
        if coord:
            x,y = coord
            pyautogui.moveTo(x,y)
            pyautogui.click(x,y)
            for _ in range(2):
                pyautogui.scroll(100)   # scroll up at same position
                time.sleep(scroll_delay)
        elif mouse_btn:
            press_mouse(mouse_btn, backend)
            scroll_mouse(scroll_delay)
        else:
            pyautogui.click()
            scroll_mouse(scroll_delay)

        for template_path in templates:
            loc = pyautogui.locateOnScreen(template_path, confidence=0.8)
            if loc:
                cx,cy = pyautogui.center(loc)
                pyautogui.moveTo(cx,cy)
                pyautogui.click(cx,cy)
                break

        wait = random.uniform(interval_min, interval_max)
        status_label.config(text=f"Pressed {mouse_button} — next in {wait:.2f}s")
        time.sleep(wait)

# --- Settings persistence ---
def save_settings():
    settings = {
        "interval_min": min_entry.get(),
        "interval_max": max_entry.get(),
        "mouse_button": mouse_choice.get(),
        "backend": backend_choice.get(),
        "scroll_delay": scroll_entry.get(),
        "x": x_entry.get(),
        "y": y_entry.get()
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        min_entry.delete(0, tk.END); min_entry.insert(0, settings.get("interval_min","1"))
        max_entry.delete(0, tk.END); max_entry.insert(0, settings.get("interval_max","2"))
        mouse_choice.set(settings.get("mouse_button","left"))
        backend_choice.set(settings.get("backend","pynput"))
        scroll_entry.delete(0, tk.END); scroll_entry.insert(0, settings.get("scroll_delay","0.2"))
        x_entry.delete(0, tk.END); x_entry.insert(0, settings.get("x",""))
        y_entry.delete(0, tk.END); y_entry.insert(0, settings.get("y",""))

# --- GUI actions ---
def start_macro():
    save_settings()  # save settings when starting
    interval_min = float(min_entry.get())
    interval_max = float(max_entry.get())
    mouse_button = mouse_choice.get()
    backend = backend_choice.get()
    scroll_delay = float(scroll_entry.get())
    coord = None
    if x_entry.get() and y_entry.get():
        coord = (int(x_entry.get()), int(y_entry.get()))
    thread = Thread(target=macro_loop, args=(interval_min, interval_max, mouse_button, backend, scroll_delay, coord), daemon=True)
    thread.start()

def stop_macro():
    global running
    running = False
    status_label.config(text="Stopped")
    save_settings()  # save settings when stopping

def set_coordinates():
    x,y = pyautogui.position()
    x_entry.delete(0,tk.END); x_entry.insert(0,str(x))
    y_entry.delete(0,tk.END); y_entry.insert(0,str(y))
    status_label.config(text=f"Coordinates set: ({x},{y})")
    save_settings()

def on_press(key):
    global running
    try:
        if key == keyboard.Key.insert:   # global Insert key
            if not running:
                start_macro()
            else:
                stop_macro()
    except Exception:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

# ---- GUI ----
app = tk.Tk()
app.title("Deathmatch Protector - Tkinter")
app.geometry("450x550")

tk.Label(app,text="Min interval (sec):").pack()
min_entry = tk.Entry(app); min_entry.pack()

tk.Label(app,text="Max interval (sec):").pack()
max_entry = tk.Entry(app); max_entry.pack()

mouse_choice = tk.StringVar(value="left")
tk.Radiobutton(app,text="Left Click",variable=mouse_choice,value="left").pack()
tk.Radiobutton(app,text="Right Click",variable=mouse_choice,value="right").pack()

tk.Label(app,text="Linux Backend:").pack()
backend_choice = tk.StringVar(value="pynput")
tk.Radiobutton(app,text="pynput",variable=backend_choice,value="pynput").pack()
tk.Radiobutton(app,text="xdotool",variable=backend_choice,value="xdotool").pack()
tk.Radiobutton(app,text="wtype",variable=backend_choice,value="wtype").pack()

tk.Label(app,text="Scroll Delay (sec):").pack()
scroll_entry = tk.Entry(app); scroll_entry.pack()

tk.Label(app,text="Coordinates:").pack()
x_entry = tk.Entry(app); x_entry.pack()
y_entry = tk.Entry(app); y_entry.pack()
tk.Button(app,text="Set Coordinates from Mouse",command=set_coordinates).pack(pady=5)

tk.Button(app,text="START",width=20,command=start_macro).pack(pady=10)
tk.Button(app,text="STOP",width=20,command=stop_macro).pack()

status_label = tk.Label(app,text="Idle")
status_label.pack(pady=10)

# Load saved settings at startup
load_settings()

app.mainloop()
