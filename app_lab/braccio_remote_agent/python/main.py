from arduino.app_utils import App, Bridge
import socket
import time


HOST = "0.0.0.0"
PORT = 8765


def handle_command(command):
    parts = command.strip().split()
    if len(parts) != 7 or parts[0] != "M":
        return "ERR"

    try:
        values = [int(value) for value in parts[1:]]
    except ValueError:
        return "ERR"

    result = Bridge.call("move_braccio", *values)
    return "OK" if result is None or result is True else str(result)


def loop():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)
        server.settimeout(1.0)
        print(f"Braccio remote agent listening on {PORT}")

        while True:
            try:
                client, address = server.accept()
            except socket.timeout:
                time.sleep(0.05)
                continue

            with client:
                data = client.recv(128).decode("ascii", errors="replace")
                response = handle_command(data)
                client.sendall((response + "\n").encode("ascii"))
                print(f"{address[0]}: {data.strip()} -> {response}")


App.run(user_loop=loop)
