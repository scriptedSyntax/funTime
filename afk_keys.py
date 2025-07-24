import tkinter as tk
from tkinter import messagebox
import threading
import time
from pynput.keyboard import Controller, Key

class KeyAutomatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Key Automator")
        master.geometry("400x280")  # Adjusted height for new field
        master.resizable(False, False)

        self.keyboard = Controller()
        self.automation_thread = None
        self.stop_event = threading.Event()

        # --- Delay Input (Cycle) ---
        self.delay_label = tk.Label(master, text="Delay after each cycle (seconds):", font=('Arial', 10))
        self.delay_label.pack(pady=(20, 5))
        self.delay_entry = tk.Entry(master, width=30, font=('Arial', 10))
        self.delay_entry.insert(0, "1")  # Default cycle delay
        self.delay_entry.pack(pady=5)

        # --- Delay Input (Between Keys) ---
        self.key_delay_label = tk.Label(master, text="Delay between individual key presses (seconds):", font=('Arial', 10))
        self.key_delay_label.pack(pady=(5, 5))
        self.key_delay_entry = tk.Entry(master, width=30, font=('Arial', 10))
        self.key_delay_entry.insert(0, "0.05")  # Default inter-key delay
        self.key_delay_entry.pack(pady=5)

        # --- Keys Input ---
        self.keys_label = tk.Label(master, text="Keys to press (comma-separated, e.g., a,b,enter,f5):", font=('Arial', 10))
        self.keys_label.pack(pady=5)
        self.keys_entry = tk.Entry(master, width=40, font=('Arial', 10))
        self.keys_entry.insert(0, "hello,world,enter")  # Default keys
        self.keys_entry.pack(pady=5)

        # --- Control Buttons ---
        self.start_button = tk.Button(master, text="Start Automation", command=self.start_automation, font=('Arial', 10, 'bold'))
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop Automation", command=self.stop_automation, font=('Arial', 10), state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(master, text="Ready", font=('Arial', 9), fg='blue')
        self.status_label.pack(pady=5)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def parse_keys(self, keys_string):
        parsed_keys = []
        key_map = {
            'enter': Key.enter, 'space': Key.space, 'tab': Key.tab, 'esc': Key.esc,
            'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right,
            'shift': Key.shift, 'ctrl': Key.ctrl, 'alt': Key.alt_l, 'backspace': Key.backspace,
            'delete': Key.delete, 'caps_lock': Key.caps_lock, 'f1': Key.f1, 'f2': Key.f2,
            'f3': Key.f3, 'f4': Key.f4, 'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7,
            'f8': Key.f8, 'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12
        }
        for key_name in keys_string.split(','):
            key_name = key_name.strip().lower()
            if key_name in key_map:
                parsed_keys.append(key_map[key_name])
            elif len(key_name) == 1:
                parsed_keys.append(key_name)
            else:
                for char in key_name:
                    parsed_keys.append(char)
        return parsed_keys

    def automate_keys(self, cycle_delay, inter_key_delay, keys_to_press):
        self.status_label.config(text="Automation Running...", fg='green')
        while not self.stop_event.is_set():
            for key in keys_to_press:
                try:
                    if isinstance(key, Key):
                        self.keyboard.press(key)
                        self.keyboard.release(key)
                    else:
                        self.keyboard.type(key)
                    time.sleep(inter_key_delay)
                except Exception as e:
                    print(f"Error pressing key {key}: {e}")
                    self.status_label.config(text=f"Error: {e}", fg='red')
                    self.stop_automation_internal()
                    return
            self.status_label.config(text=f"Cycle complete. Waiting {cycle_delay}s...", fg='green')
            self.stop_event.wait(cycle_delay)
            if self.stop_event.is_set():
                break
        self.status_label.config(text="Automation Stopped.", fg='red')
        self.reset_buttons()

    def start_automation(self):
        try:
            cycle_delay = float(self.delay_entry.get())
            inter_key_delay = float(self.key_delay_entry.get())
            if cycle_delay < 0 or inter_key_delay < 0:
                raise ValueError("Delays cannot be negative.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numbers for delay. {e}")
            return

        keys_string = self.keys_entry.get()
        if not keys_string:
            messagebox.showerror("Invalid Input", "Please enter keys to press.")
            return

        self.stop_event.clear()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.delay_entry.config(state=tk.DISABLED)
        self.key_delay_entry.config(state=tk.DISABLED)
        self.keys_entry.config(state=tk.DISABLED)

        keys_to_press = self.parse_keys(keys_string)
        self.automation_thread = threading.Thread(
            target=self.automate_keys,
            args=(cycle_delay, inter_key_delay, keys_to_press)
        )
        self.automation_thread.daemon = True
        self.automation_thread.start()

    def stop_automation(self):
        self.stop_event.set()
        self.status_label.config(text="Stopping automation...", fg='orange')
        if self.automation_thread and self.automation_thread.is_alive():
            self.automation_thread.join(timeout=1)
        self.stop_automation_internal()

    def stop_automation_internal(self):
        self.reset_buttons()
        self.status_label.config(text="Automation Stopped.", fg='red')

    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.delay_entry.config(state=tk.NORMAL)
        self.key_delay_entry.config(state=tk.NORMAL)
        self.keys_entry.config(state=tk.NORMAL)

    def on_closing(self):
        if self.automation_thread and self.automation_thread.is_alive():
            if messagebox.askokcancel("Quit", "Automation is running. Do you want to stop it and quit?"):
                self.stop_event.set()
                self.automation_thread.join(timeout=2)
                self.master.destroy()
        else:
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyAutomatorGUI(root)
    root.mainloop()


