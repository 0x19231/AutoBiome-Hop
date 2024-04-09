import cv2
import pyautogui
import numpy as np
import pytesseract
import tkinter as tk
import difflib
import psutil
from selenium import webdriver
from subprocess import Popen, check_call
import time

dr = webdriver.Chrome()

pytesseract.pytesseract.tesseract_cmd = r'D:\OCR\tesseract.exe'

top_left = None
bottom_right = None
drawing = False
selected_triggers = []
unchecked_triggers = []
last_trigger_time = None

def draw_rectangle(event, x, y, flags, params):
    global top_left, bottom_right, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        top_left = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            bottom_right = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        bottom_right = (x, y)
        drawing = False

def trigger_detected_function():
    for proc in psutil.process_iter():
        if proc.name() == "RobloxPlayerBeta.exe":
            proc.kill()
            print("roblox closed")
            time.sleep(2)
            dr.execute_script("window.open()")
            time.sleep(2)
            try:
                dr.switch_to.window(dr.window_handles[-1])
            except IndexError:
                print("no dr handler")
                return
            dr.get('https://www.roblox.com/share?code=0016448613cb88499db9635efedee2b3&type=Server')
            dr.close()
            time.sleep(20)
            dr.switch_to.window(dr.window_handles[0])

def set_detection_area():
    global top_left, bottom_right

    screen = pyautogui.screenshot()
    screen = np.array(screen)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

    cv2.namedWindow('Set Detection Area')
    cv2.setMouseCallback('Set Detection Area', draw_rectangle)

    while True:
        temp_screen = screen.copy()

        if top_left and bottom_right:
            cv2.rectangle(temp_screen, top_left, bottom_right, (0, 255, 0), 2)

        cv2.imshow('Set Detection Area', temp_screen)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if drawing == False and top_left and bottom_right:
            break

    cv2.destroyAllWindows()
    main(top_left, bottom_right)

def check_trigger_text(text):
    global selected_triggers, unchecked_triggers, last_trigger_time

    if not selected_triggers:
        print("Error: No trigger texts selected.")
        return

    for trigger in selected_triggers:
        similarity_ratio = difflib.SequenceMatcher(None, trigger.lower(), text.lower()).ratio()
        if similarity_ratio >= 0.5:
            print("Trigger detected:", trigger)
            last_trigger_time = time.time()
            trigger_detected_function()
            return

    print("0 - continue")

def handle_selection():
    global selected_triggers, unchecked_triggers
    selected_triggers = [text.get() for text in trigger_vars if text.get()]
    unchecked_triggers = [text.get() for text in trigger_vars if not text.get()]
    root.destroy()

def main(top_left, bottom_right):
    global last_trigger_time

    while True:
        if top_left is None or bottom_right is None:
            print("Error: Detection area coordinates are not properly defined.")
            break

        if bottom_right[0] <= top_left[0] or bottom_right[1] <= top_left[1]:
            print("Error: Invalid detection area coordinates.")
            break

        screenshot = pyautogui.screenshot(region=(
            top_left[0],
            top_left[1],
            bottom_right[0] - top_left[0],
            bottom_right[1] - top_left[1]
        ))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        resized_height = 700
        aspect_ratio = screenshot.shape[1] / screenshot.shape[0]
        resized_width = int(resized_height * aspect_ratio)
        resized = cv2.resize(screenshot, (resized_width, resized_height))

        detected_text = pytesseract.image_to_string(resized)

        check_trigger_text(detected_text)

        if last_trigger_time is not None and time.time() - last_trigger_time >= 480:
            print("No triggers detected for 5 minutes. Triggering function...")
            trigger_detected_function()
            last_trigger_time = None

        cv2.imshow('Detected Text', resized)

        if cv2.waitKey(500) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    trigger_texts = [
        "The moon is rising!",
        "An incredibly strong blizzard is freezing the island!",
        "The wind is sweeping life energy...",
        "A powerful stormsurge has engulfed the island!",
        "Magical Flames have warped this island!",
        "The war between holy and unholy has started!",
        "The war between pure and corrupt has started!",
        "The island has been irradiated by an unknown wave of energy...",
        "The angels of the sky are descending!",
        "A bright blue moon illuminates the night along with countless shooting stars..."
    ]

    root = tk.Tk()
    root.title("Select Trigger Texts")

    trigger_vars = []
    for text in trigger_texts:
        var = tk.StringVar(value=text)
        checkbox = tk.Checkbutton(root, text=text, variable=var)
        checkbox.pack(anchor='w')
        trigger_vars.append(var)

    select_button = tk.Button(root, text="SELECT", command=lambda: handle_selection())
    select_button.pack()

    root.mainloop()

    set_detection_area()
