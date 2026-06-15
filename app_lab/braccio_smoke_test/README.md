# Braccio Smoke Test for Arduino App Lab

This is a minimal Arduino App Lab project for validating that the Braccio shield
is seated on the UNO Q and that the MCU can drive the servos.

The sketch moves the arm to a conservative rest pose, waits, then moves to a
small ready pose. Keep the arm clear before starting the app.

## Files

```text
app.yaml                 App Lab manifest
python/main.py           Linux-side keepalive loop
python/requirements.txt  Python dependencies
sketch/sketch.ino        MCU-side Braccio test
sketch/sketch.yaml       UNO Q FQBN and library list
```

