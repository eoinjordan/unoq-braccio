# Platform Setup

This project targets ROS 2 Jazzy and Gazebo on Ubuntu 24.04. Linux is the
reference environment. Windows is supported through WSL2 for ROS 2 and Gazebo,
with native Windows used for Arduino flashing if preferred. macOS is best used
for firmware and ROS 2 package development; Gazebo simulation should be run in a
Linux VM or container.

There are two hardware control modes:

- USB serial: the ROS 2 host is physically connected to the UNO Q USB port.
- Remote network: an Arduino App Lab app runs on the UNO Q and exposes a TCP
  control port over Wi-Fi or Ethernet.

## Linux: Ubuntu 24.04

Install ROS 2 Jazzy Desktop and developer tools using the official ROS 2 Jazzy
Ubuntu instructions.

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-pip python3-opencv ros-jazzy-cv-bridge v4l-utils
sudo rosdep init || true
rosdep update
```

Install Gazebo/ROS integration packages:

```bash
sudo apt update
sudo apt install -y ros-jazzy-ros-gz ros-jazzy-gazebo-ros-pkgs
```

Build the workspace:

```bash
cd ~/git/unoq-braccio/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
cd ..
```

Flash the UNO Q:

```bash
arduino-cli lib install Braccio
arduino-cli core install arduino:zephyr
arduino-cli board list
arduino-cli compile --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
```

Run hardware:

```bash
source ~/git/unoq-braccio/ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup hardware.launch.py serial_port:=/dev/ttyACM0
```

Run hardware remotely over the network:

1. Install and start `app_lab/braccio_remote_agent` on the UNO Q with App Lab.
2. Find the UNO Q IP address in App Lab or over SSH with `ip addr show`.
3. Run:

```bash
source ~/git/unoq-braccio/ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=<UNO_Q_IP_ADDRESS> port:=8765
```

Run simulation:

```bash
source ~/git/unoq-braccio/ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup sim.launch.py
```

## Windows 11

### Recommended: WSL2 for ROS 2 and Gazebo

Native Windows ROS 2 binary installs exist, but the pre-built Windows package
does not include every ROS 2 package. For this repo, use Ubuntu 24.04 in WSL2
for the ROS 2 workspace and Gazebo simulation.

Install WSL2 from PowerShell:

```powershell
wsl --install -d Ubuntu-24.04
wsl --set-default-version 2
```

Open Ubuntu 24.04 and install ROS 2 Jazzy using the official Ubuntu
instructions, then install workspace tools:

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-pip python3-opencv ros-jazzy-cv-bridge v4l-utils
sudo rosdep init || true
rosdep update
```

Clone and build:

```bash
mkdir -p ~/git
cd ~/git
git clone git@github.com:eoinjordan/unoq-braccio.git
cd unoq-braccio/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
cd ..
```

Run simulation from WSL2:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup sim.launch.py
```

### Flashing from native Windows

Install Arduino CLI for Windows, then use PowerShell from the repo root:

```powershell
arduino-cli lib install Braccio
arduino-cli core install arduino:zephyr
arduino-cli board list
arduino-cli compile --fqbn arduino:zephyr:unoq .\firmware\unoq_braccio_firmware
arduino-cli upload -p COM3 --fqbn arduino:zephyr:unoq .\firmware\unoq_braccio_firmware
```

Replace `COM3` with the port shown by `arduino-cli board list`.
Do not use `arduino:avr:uno`; the UNO Q MCU uses the Zephyr board package.

Serial monitor test after upload:

```powershell
arduino-cli board list
arduino-cli monitor -p COM4 --fqbn arduino:zephyr:unoq --config baudrate=115200
```

Replace `COM4` with the UNO Q port. The firmware starts serial at `115200`
baud, so the default monitor baud rate is not correct for this sketch.

Send:

```text
M 90 90 90 90 90 25
```

Expected response:

```text
OK
```

If upload fails with:

```text
adb.exe: device offline
```

Android tooling may be installed, but the UNO Q is not accepting ADB commands.
Check with Arduino's packaged ADB:

```powershell
& "$env:LOCALAPPDATA\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe" devices -l
```

If the UNO Q is listed as `offline`:

1. Close Arduino App Lab, Arduino IDE, serial monitors, and Android emulators.
2. Unplug and reconnect the UNO Q USB-C cable.
3. Unlock or wake the UNO Q if it shows an authorization prompt.
4. Restart ADB:

```powershell
& "$env:LOCALAPPDATA\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe" kill-server
& "$env:LOCALAPPDATA\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe" start-server
& "$env:LOCALAPPDATA\Arduino15\packages\arduino\tools\adb\32.0.0\adb.exe" devices -l
```

Retry upload only when the UNO Q status changes from `offline` to `device`.

If Arduino CLI also lists a network port, for example `192.168.1.64`, you can
use network upload instead of USB ADB upload. This is the validated Windows
upload path for this project:

```powershell
arduino-cli board list
arduino-cli upload -p 192.168.1.64 --fqbn arduino:zephyr:unoq .\firmware\unoq_braccio_firmware --upload-field password=arduino123
```

Expected successful upload output includes OpenOCD messages and ends with:

```text
shutdown command invoked
New upload port: 192.168.1.64 (network)
```

Replace `192.168.1.64` and `arduino123` with your UNO Q network address and
upload password. If the command asks for upload credentials, rerun it with the
App Lab or UNO Q upload password:

```powershell
arduino-cli upload -p 192.168.1.64 --fqbn arduino:zephyr:unoq .\firmware\unoq_braccio_firmware --upload-field password=<UPLOAD_PASSWORD>
```

Use `COM4` only for USB upload on Windows. Do not use `/dev/ttyACM0` from
PowerShell; that path is for Linux/WSL.

### Hardware bridge from WSL2

For ROS 2 in WSL2 to talk to the Arduino over USB, attach the serial device to
WSL with `usbipd-win` from an elevated PowerShell:

```powershell
winget install --id dorssel.usbipd-win
usbipd list
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

Then in WSL2:

```bash
ls /dev/ttyACM* /dev/ttyUSB*
source ~/git/unoq-braccio/ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup hardware.launch.py serial_port:=/dev/ttyACM0
```

If the board appears as `/dev/ttyUSB0`, pass that path instead.

### Remote hardware bridge from WSL2

This is usually easier than USB forwarding on Windows. Keep the UNO Q on the
same network as the Windows/WSL2 machine, run `app_lab/braccio_remote_agent` on
the UNO Q, then launch:

```bash
source ~/git/unoq-braccio/ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=<UNO_Q_IP_ADDRESS> port:=8765
```

Send a test pose:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
```

### Native Windows ROS 2

Native Windows ROS 2 is useful for experimentation, but it is not the validated
path for this repo's Gazebo simulation. Use WSL2 if you want the commands in
this repo to match the Linux launch files exactly.

### Flashing a Test from Arduino App Lab

Use this path when you want to validate the UNO Q + Braccio shield from App Lab
before involving ROS 2.

1. Power the Braccio shield from its servo power input.
2. Connect the UNO Q to the PC over USB-C.
3. Open Arduino App Lab and connect to the UNO Q.
4. Let App Lab update the board if it prompts for firmware or runtime updates.
5. Create a new app named `braccio_smoke_test`.
6. Add the `Braccio` and `Servo` libraries in the App Lab library panel.
7. Replace the generated files with the files in
   `app_lab/braccio_smoke_test`.
8. Click App Lab's run/start button.

Expected result: the arm moves to rest, waits for about two seconds, moves to a
small ready pose, then returns to rest.

If you prefer the App Lab CLI route after the board is configured, copy the app
folder to the UNO Q and start it over SSH:

```powershell
scp -r .\app_lab\braccio_smoke_test arduino@<UNO_Q_IP_ADDRESS>:~/ArduinoApps/
ssh arduino@<UNO_Q_IP_ADDRESS>
arduino-app-cli app start ~/ArduinoApps/braccio_smoke_test
arduino-app-cli app logs ~/ArduinoApps/braccio_smoke_test
```

Stop the test app:

```bash
arduino-app-cli app stop ~/ArduinoApps/braccio_smoke_test
```

### Running the Remote Agent from Arduino App Lab

Use this path when you want the robot arm to be controlled over the network
instead of a USB serial cable.

1. Power the Braccio shield from its servo power input.
2. Connect the UNO Q to the same Wi-Fi/Ethernet network as the ROS 2 host.
3. Open Arduino App Lab and connect to the UNO Q.
4. Create a new app named `braccio_remote_agent`.
5. Add the `Braccio`, `Servo`, and `Arduino_RouterBridge` libraries.
6. Replace the generated files with the files in
   `app_lab/braccio_remote_agent`.
7. Run the app.
8. Find the UNO Q IP address.

Then from the ROS 2 host:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=<UNO_Q_IP_ADDRESS> port:=8765
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
```

The remote agent listens on TCP port `8765` and accepts the same `M ...` command
format as the USB serial firmware.

## macOS

ROS 2 Jazzy on macOS is a source-build workflow in the official ROS 2 docs. For
this repo, macOS is reasonable for firmware work and Python node development,
but Linux is still the recommended simulation runtime.

Install Arduino CLI:

```bash
brew install arduino-cli
arduino-cli lib install Braccio
arduino-cli core install arduino:zephyr
arduino-cli board list
arduino-cli compile --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
arduino-cli upload -p /dev/cu.usbmodem1101 --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
```

Replace `/dev/cu.usbmodem1101` with the port shown by `arduino-cli board list`.

For ROS 2 development, follow the official macOS source-build instructions,
then build this workspace:

```bash
cd ~/git/unoq-braccio/ros2_ws
colcon build --symlink-install
source install/setup.zsh
```

For Gazebo, prefer an Ubuntu 24.04 VM, container, or a separate Linux machine.

## Validation Commands

Use these commands after setup:

```bash
ros2 pkg list | grep unoq_braccio
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
ros2 topic echo /braccio/joint_command
```

Firmware serial smoke test:

```text
M 90 90 90 90 90 25
```

The board should respond with `OK`.

On Windows, open the serial monitor with the firmware baud rate:

```powershell
arduino-cli monitor -p COM4 --fqbn arduino:zephyr:unoq --config baudrate=115200
```

Remote agent smoke test from the ROS 2 host:

```bash
python3 - <<'PY'
import socket
host = "<UNO_Q_IP_ADDRESS>"
with socket.create_connection((host, 8765), timeout=2) as sock:
    sock.sendall(b"M 90 90 90 90 90 25\n")
    print(sock.recv(128).decode().strip())
PY
```

The remote agent should respond with `OK`.

## Troubleshooting: `rosdep`, `colcon`, or `apt` Not Found

If you see errors like:

```text
rosdep: not found
colcon: not found
apt: not found
source: can't open install/setup.bash
```

you are not in a ROS 2 Ubuntu environment. Do not build the ROS 2 workspace from
the UNO Q App Lab shell, a minimal container shell, or any shell where `apt` is
missing.

This shell prompt is not a valid ROS 2 build environment for the setup steps:

```text
home:/mnt/host/c/Users/Eoin/git/unoq-braccio#
```

In that shell, commands such as `sudo apt update`, `rosdep update`, and
`colcon build` are expected to fail if `sudo`, `apt`, `rosdep`, or `colcon` are
not installed.

Use Ubuntu 24.04 directly, or on Windows open the Ubuntu 24.04 WSL terminal.
Then install ROS 2 Jazzy and the build tools before running `colcon`.

Also check your current directory. If `pwd` already ends in `ros2_ws`, do not
run `cd ros2_ws` again.

Correct sequence from the repo root:

```bash
cd /mnt/c/Users/Eoin/git/unoq-braccio
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

If `rosdep` or `colcon` are missing on Ubuntu:

```bash
sudo apt update
sudo apt install -y python3-rosdep python3-colcon-common-extensions python3-pip python3-opencv ros-jazzy-cv-bridge v4l-utils
sudo rosdep init || true
rosdep update
```
