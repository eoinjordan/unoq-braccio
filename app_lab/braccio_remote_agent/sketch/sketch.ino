#include <Arduino_RouterBridge.h>
#include <Braccio.h>
#include <Servo.h>

Servo base;
Servo shoulder;
Servo elbow;
Servo wrist_ver;
Servo wrist_rot;
Servo gripper;

const int JOINTS = 6;
const int MIN_LIMITS[JOINTS] = {0, 15, 0, 0, 0, 10};
const int MAX_LIMITS[JOINTS] = {180, 165, 180, 180, 180, 73};

int clampJoint(int index, int value) {
  if (value < MIN_LIMITS[index]) {
    return MIN_LIMITS[index];
  }
  if (value > MAX_LIMITS[index]) {
    return MAX_LIMITS[index];
  }
  return value;
}

bool move_braccio(
  int base_angle,
  int shoulder_angle,
  int elbow_angle,
  int wrist_vertical_angle,
  int wrist_rotation_angle,
  int gripper_angle
) {
  Braccio.ServoMovement(
    20,
    clampJoint(0, base_angle),
    clampJoint(1, shoulder_angle),
    clampJoint(2, elbow_angle),
    clampJoint(3, wrist_vertical_angle),
    clampJoint(4, wrist_rotation_angle),
    clampJoint(5, gripper_angle)
  );
  return true;
}

void setup() {
  Bridge.begin();
  Bridge.provide("move_braccio", move_braccio);
  Braccio.begin();
  move_braccio(90, 45, 180, 180, 90, 10);
}

void loop() {
  delay(1000);
}
