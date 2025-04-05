#!/usr/bin/env python3
import socket
import json

SOCKET_PATH = '/tmp/time_service.sock'

def get_time_update():
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    data = b""
    while True:
        chunk = client.recv(4096)
        if not chunk:
            break
        data += chunk
    client.close()
    try:
        response = json.loads(data.decode('utf-8'))
        return response
    except Exception as e:
        print("Failed to parse response:", e)
        return None

if __name__ == "__main__":
    response = get_time_update()
    if response:
        print("Current Time:", response["current_time"])
        print("Connection Updates:")
        for name, info in response["connections"].items():
            print(f" - {name}: Last Update: {info['last_update']}, Active: {info['active']}, Likelihood: {info['likelihood']}%")
