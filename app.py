import socketio
import time
import tkinter as tk
import pygame
import os

# Initialize pygame mixer
pygame.mixer.init()

# Create a Socket.IO client instance
sio = socketio.Client()

class EmergencyAlertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Alerts")
        self.root.attributes('-fullscreen', True)  # Set full-screen mode
        self.root.configure(bg='black')
        
        self.frame = tk.Frame(root, bg="black")
        self.frame.pack(expand=True, fill=tk.BOTH)
        
        self.time_label = tk.Label(self.frame, font=("Arial", 100), fg="white", bg="black")
        self.time_label.pack(pady=20)
        
        self.date_label = tk.Label(self.frame, font=("Arial", 50), fg="white", bg="black")
        self.date_label.pack(pady=10)
        
        self.alert_label = tk.Label(self.frame, text="", font=("Arial", 200, "bold"), bg="black", anchor="center")
        self.alert_label.pack(expand=True, fill=tk.BOTH)
        
        self.alert_active = False
        self.current_alert = ""
        self.is_flashing = False
        self.current_sound = None
        
        self.alert_colors = {
            "FIRE ALARM": "red",
            "TORNADO WARNING": "orange",
            "LOCKDOWN": "blue",
            "EARTHQUAKE ALERT": "purple",
            "CHEMICAL SPILL": "yellow",
            "BOMB THREAT": "darkred",
            "INTRUDER ALERT": "brown",
            "POWER OUTAGE": "gray",
            "HAZARDOUS WEATHER": "cyan"
        }

        self.alert_sounds = {
            "FIRE ALARM": "sounds/fire.mp3",
            "TORNADO WARNING": "sounds/tornado.mp3",
            "LOCKDOWN": "sounds/lockdown.mp3",
            "EARTHQUAKE ALERT": "sounds/earthquake.mp3",
            "CHEMICAL SPILL": "sounds/chemical.mp3",
            "BOMB THREAT": "sounds/bomb.mp3",
            "INTRUDER ALERT": "sounds/intruder.mp3",
            "POWER OUTAGE": "sounds/power.mp3",
            "HAZARDOUS WEATHER": "sounds/weather.mp3"
        }

        # Connect to the Flask app
        try:
            sio.connect('http://127.0.0.1:5001', transports=['websocket'])
            sio.on('update_alert', self.update_alert)
            sio.on('play_bell', self.play_bell)
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.alert_label.config(text="Server Connection Failed", fg="red")

        self.root.bind('<Escape>', self.exit_fullscreen)  # Press 'Esc' to exit full-screen
        self.root.bind('<f>', lambda e: self.toggle_alert("FIRE ALARM"))
        self.root.bind('<t>', lambda e: self.toggle_alert("TORNADO WARNING"))
        self.root.bind('<l>', lambda e: self.toggle_alert("LOCKDOWN"))
        self.root.bind('<e>', lambda e: self.toggle_alert("EARTHQUAKE ALERT"))
        self.root.bind('<c>', lambda e: self.toggle_alert("CHEMICAL SPILL"))
        self.root.bind('<b>', lambda e: self.toggle_alert("BOMB THREAT"))
        self.root.bind('<i>', lambda e: self.toggle_alert("INTRUDER ALERT"))
        self.root.bind('<p>', lambda e: self.toggle_alert("POWER OUTAGE"))
        self.root.bind('<h>', lambda e: self.toggle_alert("HAZARDOUS WEATHER"))
        
        self.root.bind("<Configure>", self.resize_text)
        
        self.update_time()
    
    def update_time(self):
        if not self.alert_active:
            now = time.strftime("%I:%M:%S %p")
            date = time.strftime("%A, %B %d, %Y")
            self.time_label.config(text=now)
            self.date_label.config(text=date)
        self.root.after(1000, self.update_time)
    
    def play_alert_sound(self, alert_type):
        # Stop any currently playing sound
        if self.current_sound:
            self.current_sound.stop()
        
        # Get the sound file path
        sound_file = self.alert_sounds.get(alert_type)
        if sound_file and os.path.exists(sound_file):
            try:
                self.current_sound = pygame.mixer.Sound(sound_file)
                self.current_sound.play(-1)  # -1 means loop indefinitely
            except Exception as e:
                print(f"Error playing sound: {e}")
    
    def play_bell(self):
        # Stop any currently playing sound
        if self.current_sound:
            self.current_sound.stop()
        
        # Play the bell sound
        bell_file = "sounds/bell.mp3"
        if os.path.exists(bell_file):
            try:
                self.current_sound = pygame.mixer.Sound(bell_file)
                self.current_sound.play()  # Play once
            except Exception as e:
                print(f"Error playing bell sound: {e}")
    
    def stop_alert_sound(self):
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None
    
    def update_alert(self, data):
        self.current_alert = data['alert']
        self.alert_active = data['active']
        
        if self.alert_active:
            self.alert_label.config(fg=data['color'], text=self.current_alert)
            self.is_flashing = True
            self.play_alert_sound(self.current_alert)
            self.flash_text()
        else:
            self.alert_active = False
            self.is_flashing = False
            self.stop_alert_sound()
            self.alert_label.config(text="")
            self.time_label.config(text=time.strftime("%I:%M:%S %p"))
            self.date_label.config(text=time.strftime("%A, %B %d, %Y"))
    
    def toggle_alert(self, alert_text):
        if self.alert_active and self.current_alert == alert_text:
            self.alert_active = False
            self.is_flashing = False
            self.current_alert = ""
            self.alert_label.config(text="")
            self.time_label.config(text=time.strftime("%I:%M:%S %p"))
            self.date_label.config(text=time.strftime("%A, %B %d, %Y"))
        else:
            self.alert_active = True
            self.is_flashing = True
            self.current_alert = alert_text
            self.alert_label.config(fg=self.alert_colors.get(alert_text, "white"))
            self.flash_text()
    
    def flash_text(self):
        if self.alert_active and self.is_flashing:
            current_text = self.alert_label.cget("text")
            if current_text == "":
                self.alert_label.config(text=self.current_alert)
                self.time_label.config(text="")
                self.date_label.config(text="")
            else:
                self.alert_label.config(text="")
            self.root.after(500, self.flash_text)
    
    def resize_text(self, event):
        new_size = max(50, event.height // 5)
        self.alert_label.config(font=("Arial", new_size, "bold"))
    
    def exit_fullscreen(self, event):
        self.root.attributes('-fullscreen', False)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyAlertApp(root)
    root.mainloop()
