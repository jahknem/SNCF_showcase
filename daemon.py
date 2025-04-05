#!/usr/bin/env python3
import socket
import json
import os
import threading
import time
import random

# Unix socket file path
SOCKET_PATH = '/tmp/time_service.sock'

# Define connection types and their "active" likelihood ranges.
connections = {
    "GNSS": {"active_range": (98, 100)},
    "Wired PTP": {"active_range": (95, 100)},
    "5G PSS/SSS": {"active_range": (80, 95)},
    "Allouis": {"active_range": (60, 80)},
    "LoRa": {"active_range": (40, 60)},
    "Satellite PTP": {"active_range": (70, 90)}
}

# Initialize state for each connection with current time and random likelihood.
state = {}
current_time = lambda: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
for name, props in connections.items():
    state[name] = {
        "last_update": current_time(),
        "active": True,
        "likelihood": random.randint(*props["active_range"])
    }

def update_states():
    """
    Continuously update each connection's state.
    With an 80% chance, the connection receives an update:
      - Updates 'last_update' to the current time.
      - Sets 'active' to True.
      - Generates a likelihood from its active range.
    Otherwise, it is marked inactive with a low likelihood.
    """
    while True:
        for name, props in connections.items():
            if random.random() < 0.8:
                # Connection is active: update timestamp and likelihood.
                state[name]["last_update"] = current_time()
                state[name]["active"] = True
                state[name]["likelihood"] = random.randint(*props["active_range"])
            else:
                # Connection is inactive: mark as down and assign a low likelihood.
                state[name]["active"] = False
                state[name]["likelihood"] = random.randint(0, 20)
        time.sleep(2)

def handle_client(conn):
    """
    When a client connects, send the current time along with the states of all connections as JSON.
    """
    response = {
        "current_time": current_time(),
        "connections": state
    }
    data = json.dumps(response)
    conn.sendall(data.encode('utf-8'))
    conn.close()

def start_server():
    """
    Set up a Unix domain socket server.
    Remove any previous socket file, then listen for incoming connections.
    """
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)
    print(f"Server listening on {SOCKET_PATH}")
    while True:
        conn, _ = server.accept()
        # Handle each client connection in a separate thread.
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    # Start the update thread
    update_thread = threading.Thread(target=update_states)
    update_thread.daemon = True
    update_thread.start()
    # Start the Unix socket server loop
    start_server()
