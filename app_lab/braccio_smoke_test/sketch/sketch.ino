#include <Braccio.h>
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_ver;
Servo wrist_rot;
Servo gripper;

bool moved = false;

void setup() {
  Braccio.begin();
  Braccio.ServoMovement(30, 90, 45, 180, 180, 90, 10);
}

void loop() {
  if (!moved) {
    delay(2000);
    Braccio.ServoMovement(30, 90, 80, 120, 120, 90, 25);
    delay(2000);
    Braccio.ServoMovement(30, 90, 45, 180, 180, 90, 10);
    moved = true;
  }
  delay(1000);
}
