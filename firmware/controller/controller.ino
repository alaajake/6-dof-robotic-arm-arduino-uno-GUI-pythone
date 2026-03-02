/*
 * 6 DOF Robotic Arm Controller
 * Listen for serial commands <angle1, angle2, ...> and control servos with smooth ramping.
 * 
 * Based on parameters extracted from test.ino:
 * - Base: Pin 3 (0-180)
 * - Shoulder: Pin 5 (0-180)
 * - Elbow: Pin 6 (0-180)
 * - Wrist Pitch: Pin 9 (0-180)
 * - Wrist Roll: Pin 10 (0-145)
 * - Gripper: Pin 11 (0-160)
 */

#include <Servo.h>

// =======================
// CONFIGURATION
// =======================

// Pin Definitions
#define PIN_BASE        3
#define PIN_SHOULDER    5
#define PIN_ELBOW       6
#define PIN_WRIST_PITCH 9
#define PIN_WRIST_ROLL  10
#define PIN_GRIPPER     11

// Limits (Min, Max, Home)
const int LIMITS[6][3] = {
  {0, 180, 90},   // Base
  {0, 180, 90},   // Shoulder
  {0, 180, 90},   // Elbow
  {0, 180, 90},   // Wrist Pitch
  {0, 145, 48},   // Wrist Roll
  {0, 160, 90}    // Gripper
};

// Servo Objects
Servo servos[6];
int currentAngles[6]; // Current physical angle
int targetAngles[6];  // Desired target angle

// Smoothing
unsigned long lastMoveTime = 0;
const int MOVE_INTERVAL = 15; // ms between steps (controls speed)

// Serial Buffer
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;

// =======================
// SETUP
// =======================

void setup() {
  Serial.begin(115200);
  Serial.println("6 DOF Robotic Arm Controller Started");

  // Attach servos
  servos[0].attach(PIN_BASE);
  servos[1].attach(PIN_SHOULDER);
  servos[2].attach(PIN_ELBOW);
  servos[3].attach(PIN_WRIST_PITCH);
  servos[4].attach(PIN_WRIST_ROLL);
  servos[5].attach(PIN_GRIPPER);

  // Initialize angles
  for (int i = 0; i < 6; i++) {
    currentAngles[i] = LIMITS[i][2]; // Start at Home
    targetAngles[i] = LIMITS[i][2];
    servos[i].write(currentAngles[i]);
  }

  // Self-test routine
  runSelfTest();
}

// =======================
// MAIN LOOP
// =======================

void loop() {
  recvWithStartEndMarkers();
  if (newData) {
    parseData();
    newData = false;
  }
  updateServos();
}

// =======================
// SELF TEST
// =======================

void runSelfTest() {
  Serial.println("Running Self-Test...");
  // Cycle each servo slightly to verify movement
  for (int i = 0; i < 6; i++) {
    int home = LIMITS[i][2];
    int testMin = max(LIMITS[i][0], home - 20);
    int testMax = min(LIMITS[i][1], home + 20);
    
    // Move to test min
    smoothMoveBlocking(i, testMin);
    // Move to test max
    smoothMoveBlocking(i, testMax);
    // Return to home
    smoothMoveBlocking(i, home);
  }
  Serial.println("Self-Test Complete. Ready.");
}

// Blocking move function for startup test only
void smoothMoveBlocking(int servoIdx, int target) {
  int current = servos[servoIdx].read();
  int step = (target > current) ? 1 : -1;
  
  while (current != target) {
    current += step;
    servos[servoIdx].write(current);
    delay(10); 
  }
  currentAngles[servoIdx] = current;
  targetAngles[servoIdx] = current; // Sync target
}

// =======================
// SERIAL COMMUNICATION
// =======================

void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }
    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void parseData() {
  char * strtokIndx; // this is used by strtok() as an index

  strtokIndx = strtok(receivedChars, ",");
  for(int i=0; i<6; i++) {
    if(strtokIndx != NULL) {
      int val = atoi(strtokIndx);
      // Constrain value to limits
      val = constrain(val, LIMITS[i][0], LIMITS[i][1]);
      targetAngles[i] = val;
      strtokIndx = strtok(NULL, ",");
    }
  }
  
  // Echo back targets
  Serial.print("TARGETS:");
  for(int i=0; i<6; i++) {
    Serial.print(targetAngles[i]);
    if(i<5) Serial.print(",");
  }
  Serial.println();
}

// =======================
// MOTION CONTROL
// =======================

void updateServos() {
  if (millis() - lastMoveTime >= MOVE_INTERVAL) {
    lastMoveTime = millis();
    bool moving = false;

    for (int i = 0; i < 6; i++) {
      if (currentAngles[i] != targetAngles[i]) {
        moving = true;
        if (currentAngles[i] < targetAngles[i]) {
          currentAngles[i]++;
        } else {
          currentAngles[i]--;
        }
        servos[i].write(currentAngles[i]);
      }
    }
    
    // Optional: Echo current positions periodically or when moving
    // User asked to "echo the actual achieved angles back".
  }
  
  // Periodic status report (every 100ms)
  static unsigned long lastReportTime = 0;
  if (millis() - lastReportTime > 100) {
    lastReportTime = millis();
    Serial.print("POS:");
    for(int i=0; i<6; i++) {
      Serial.print(currentAngles[i]);
      if(i<5) Serial.print(",");
    }
    Serial.println();
  }
}
