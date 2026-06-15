# Braccio Web Agent

Run this single App Lab app on the UNO Q for the web dashboard.

It combines:

- TCP arm control on port `8765`
- USB camera MJPEG stream on port `8080`

Use this app instead of running `braccio_remote_agent` and
`usb_camera_streamer` separately.

Endpoints:

```text
tcp://<UNO_Q_IP_ADDRESS>:8765
http://<UNO_Q_IP_ADDRESS>:8080/stream
```

## Start It

`app_lab/braccio_web_agent` is a folder, not a PowerShell command. Do not run
this from PowerShell:

```powershell
app_lab/braccio_web_agent
```

Use Arduino App Lab:

1. Open Arduino App Lab.
2. Connect to the UNO Q.
3. Create or open an app named `braccio_web_agent`.
4. Replace the generated files with this folder's contents.
5. Add the `Braccio`, `Servo`, `Arduino_RouterBridge`, and `opencv-python`
   dependencies if App Lab asks.
6. Run the app.

Then test from PowerShell:

```powershell
python -c "import socket; s=socket.create_connection(('192.168.1.64',8765),timeout=3); s.sendall(b'S\n'); print(s.recv(512).decode()); s.close()"
Invoke-WebRequest -UseBasicParsing http://192.168.1.64:8080/
```

Expected:

```text
STAT uptime_ms=...
UNO Q Braccio web agent. Use /stream
```

If you have SSH and `arduino-app-cli` enabled on the UNO Q, you can copy the
folder and start it remotely:

```powershell
scp -r .\app_lab\braccio_web_agent arduino@192.168.1.64:~/ArduinoApps/
ssh arduino@192.168.1.64
arduino-app-cli app start ~/ArduinoApps/braccio_web_agent
arduino-app-cli app logs ~/ArduinoApps/braccio_web_agent
```
