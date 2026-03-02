# 6-DOF Robotic Arm Controller

A complete control system for a 6-Degree-of-Freedom (6-DOF) robotic arm, featuring an Arduino-based firmware controller with smooth motion ramping and a Python-based GUI for real-time control.

![Robot Arm](WhatsApp%20Image%202026-03-02%20at%203.45.18%20PM.jpeg)

## Features

- **6-Axis Control**: Precise control for Base, Shoulder, Elbow, Wrist Pitch, Wrist Roll, and Gripper.
- **Smooth Motion**: Firmware implements smooth acceleration/deceleration to prevent mechanical stress.
- **Real-Time Feedback**: Bi-directional communication (115200 baud) provides live position updates from the arm.
- **Safety Limits**: Hard-coded mechanical constraints prevent over-rotation and stalling.
- **Keyboard Control**: Intuitive key mappings for all joints.

## Gallery

![Arm View 1](WhatsApp%20Image%202026-03-02%20at%203.45.19%20PM.jpeg)
![Arm View 2](WhatsApp%20Image%202026-03-02%20at%203.45.20%20PM%20(1).jpeg)
![Arm View 3](WhatsApp%20Image%202026-03-02%20at%203.45.20%20PM.jpeg)
![Arm View 4](WhatsApp%20Image%202026-03-02%20at%203.45.39%20PM.jpeg)

## Installation

### Hardware
1. Connect the servos to the Arduino Uno as follows:
   - **Base**: Pin 3
   - **Shoulder**: Pin 5
   - **Elbow**: Pin 6
   - **Wrist Pitch**: Pin 9
   - **Wrist Roll**: Pin 10
   - **Gripper**: Pin 11

### Software
1. **Firmware**:
   - Open `firmware/controller/controller.ino` in Arduino IDE.
   - Upload to your Arduino board.

2. **Control App**:
   - Install Python 3.x.
   - Install dependencies:
     ```bash
     pip install pyserial
     ```
   - Run the application:
     ```bash
     python software/gui_control.py
     ```

## Usage

1. Connect the Arduino via USB.
2. Launch the Python application.
3. Select the correct COM port and click **Connect**.
4. Use the following keys to control the arm:

| Joint | Keys | Note |
|-------|------|------|
| **Base** | Left / Right | Inverted logic (Left -> 180°, Right -> 0°) |
| **Shoulder** | Up / Down | Inverted logic (Up -> 0°, Down -> 180°) |
| **Elbow** | PgUp / PgDn | |
| **Wrist Pitch** | W / S | |
| **Wrist Roll** | A / D | |
| **Gripper** | Q / E | |

## License

This project is open source.

---
**Signed by jakelap.com**  
[Instagram: @jak.elap2](https://www.instagram.com/jak.elap2/)
