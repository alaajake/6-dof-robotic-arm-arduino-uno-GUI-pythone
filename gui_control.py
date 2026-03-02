import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import time

# Configuration
BAUD_RATE = 115200

# Limits derived from test.ino [Min, Max, Home]
# Note: Base and Shoulder have inverted Min/Max in test.ino (Min=180, Max=0)
JOINT_CONFIG = [
    {"name": "Base Yaw",       "min": 180, "max": 0,   "home": 90, "key_inc": "Right", "key_dec": "Left"},
    {"name": "Shoulder Pitch", "min": 180, "max": 0,   "home": 90, "key_inc": "Up",    "key_dec": "Down"},
    {"name": "Elbow Pitch",    "min": 0,   "max": 180, "home": 90, "key_inc": "t",     "key_dec": "r"},
    {"name": "Wrist Pitch",    "min": 0,   "max": 180, "home": 90, "key_inc": "w",     "key_dec": "s"},
    {"name": "Wrist Roll",     "min": 0,   "max": 145, "home": 48, "key_inc": "d",     "key_dec": "a"},
    {"name": "Gripper",        "min": 0,   "max": 160, "home": 90, "key_inc": "e",     "key_dec": "q"}
]

class RobotArmGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("6-DOF Robot Arm Controller")
        
        # Serial Connection
        self.ser = None
        self.connected = False
        
        # State
        self.target_angles = [j["home"] for j in JOINT_CONFIG]
        self.current_angles = [j["home"] for j in JOINT_CONFIG] # Default to home until update
        self.step_size = 5
        
        # GUI Layout
        self.create_widgets()
        
        # Keyboard Bindings
        self.root.bind("<KeyPress>", self.on_key_press)
        
        # Start Polling Loop
        self.root.after(100, self.serial_poll)

    def create_widgets(self):
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection")
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        self.port_combo = ttk.Combobox(conn_frame)
        self.update_ports()
        self.port_combo.pack(side="left", padx=5, pady=5)
        
        self.btn_connect = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.btn_connect.pack(side="left", padx=5, pady=5)
        
        ttk.Button(conn_frame, text="Refresh", command=self.update_ports).pack(side="left", padx=5)

        # Status Frame
        status_frame = ttk.LabelFrame(self.root, text="Joint Status")
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.labels = []
        self.progress_bars = []
        
        for i, config in enumerate(JOINT_CONFIG):
            row = ttk.Frame(status_frame)
            row.pack(fill="x", pady=2)
            
            # Label
            lbl = ttk.Label(row, text=self.get_label_text(i), width=30, font=("Consolas", 10))
            lbl.pack(side="left", padx=5)
            self.labels.append(lbl)
            
            # Progress Bar (Visual Feedback)
            phys_min = min(config["min"], config["max"])
            phys_max = max(config["min"], config["max"])
            pb = ttk.Progressbar(row, maximum=phys_max, value=self.target_angles[i])
            pb.pack(side="left", fill="x", expand=True, padx=5)
            self.progress_bars.append(pb)
            
            # Key Hint
            keys = f"[{config['key_inc']}/{config['key_dec']}]"
            # Map special keys to readable names
            keys = keys.replace("Prior", "PgUp").replace("Next", "PgDn")
            ttk.Label(row, text=keys, width=15).pack(side="right")

        # Instructions
        ttk.Label(self.root, text="Controls: Arrows, R/T, W/S, A/D, Q/E").pack(pady=5)

    def get_label_text(self, index):
        name = JOINT_CONFIG[index]['name']
        tgt = self.target_angles[index]
        act = self.current_angles[index]
        return f"{name}: Tgt {tgt}° | Act {act}°"

    def update_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)

    def toggle_connection(self):
        if not self.connected:
            try:
                port = self.port_combo.get()
                if not port: return
                self.ser = serial.Serial(port, BAUD_RATE, timeout=0.1)
                self.connected = True
                self.btn_connect.config(text="Disconnect")
                print(f"Connected to {port}")
            except Exception as e:
                print(f"Connection Error: {e}")
        else:
            if self.ser:
                self.ser.close()
            self.connected = False
            self.btn_connect.config(text="Connect")
            print("Disconnected")

    def serial_poll(self):
        if self.connected and self.ser:
            try:
                while self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("POS:"):
                        # Parse feedback: POS:90,90,90,90,48,90
                        try:
                            parts = line.split(":")[1].split(",")
                            if len(parts) == 6:
                                self.current_angles = [int(p) for p in parts]
                                self.update_gui_feedback()
                        except ValueError:
                            pass
            except Exception as e:
                print(f"Serial Error: {e}")
                self.toggle_connection() # Disconnect on error
        
        # Schedule next poll
        self.root.after(50, self.serial_poll)

    def update_gui_feedback(self):
        for i in range(6):
            self.labels[i].config(text=self.get_label_text(i))
            # Optional: We could show 'actual' on progress bar, but target is better for control feeling.
            # self.progress_bars[i]["value"] = self.current_angles[i] 

    def send_command(self):
        if self.connected and self.ser:
            # Format: <a,b,c,d,e,f>
            cmd = "<" + ",".join(map(str, self.target_angles)) + ">"
            try:
                self.ser.write(cmd.encode('utf-8'))
            except Exception as e:
                print(f"Write Error: {e}")

    def on_key_press(self, event):
        key = event.keysym
        updated = False
        
        for i, config in enumerate(JOINT_CONFIG):
            new_angle = self.target_angles[i]
            
            # Check for both mapped key and lowercase version for letters
            key_inc = config["key_inc"]
            key_dec = config["key_dec"]
            
            # Determine direction: 
            # If min < max (Normal): Inc -> +Step, Dec -> -Step
            # If min > max (Inverted): Inc -> -Step (Towards 0), Dec -> +Step (Towards 180)
            inverted = config["min"] > config["max"]
            
            step_val = self.step_size
            if inverted:
                step_val = -step_val

            if key == key_inc or key.lower() == key_inc:
                new_angle += step_val
            elif key == key_dec or key.lower() == key_dec:
                new_angle -= step_val
            
            # Bounds check (handle min/max order)
            phys_min = min(config["min"], config["max"])
            phys_max = max(config["min"], config["max"])
            new_angle = max(phys_min, min(phys_max, new_angle))
            
            if new_angle != self.target_angles[i]:
                self.target_angles[i] = new_angle
                updated = True
                
                # Update GUI immediately (Target)
                self.labels[i].config(text=self.get_label_text(i))
                self.progress_bars[i]["value"] = new_angle
        
        if updated:
            self.send_command()

    def on_close(self):
        if self.ser:
            self.ser.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotArmGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
