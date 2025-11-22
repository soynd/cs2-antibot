# CS2-BotDB / Slower

A macro app that allows players to **stop bots from walking** in Deathmatch by automating clicks, scrolls, and spectate detection.

---

## Supported OS

- **Windows:** 10 / 11 (not fully tested)  
- **Linux:**  
  - **X11** (KDE / GNOME) — should be supported  
  - **Wayland** (KDE / GNOME) — tested, should work  
  - **Hyprland / Sway / others** — not tested, may have issues  

---

## Requirements

### Windows
- Python 3 installed  
- Python packages:
  ```bash
  pip install pyautogui pynput keyboard opencv-python
### Linux
- Python 3 installed
- the same python packages as windows
  
Debian/Ubuntu
   ```bash
  sudo apt install python3-tk python3-dev scrot xdotool wmctrl libx11-dev libxtst-dev
   ```
   Fedora
  ```bash
  sudo dnf install python3-tkinter python3-devel scrot xdotool wmctrl libX11-devel libXtst-devel
```
Arch
```bash
sudo pacman -S python-tk python-pip scrot xdotool wmctrl libx11 libxtst
```
###How to run?
- Linux
  ```bash
  sudo python3 <directory where the q.py located>
  ```
  
- Windows
    ```bash
    python q.py
    ```
    or just double tap
