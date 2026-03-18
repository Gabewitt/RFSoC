import socket
import struct
import json
import numpy as np
import matplotlib.pyplot as plt





def recv_exact(conn, nbytes):
    data = b""
    while len(data) < nbytes:
        packet = conn.recv(nbytes - len(data))
        if not packet:
            raise ConnectionError("Connection closed before full data was received.")
        data += packet
    return data

def receive_array(conn):
    meta_len = struct.unpack("!Q", recv_exact(conn, 8))[0]
    metadata = json.loads(recv_exact(conn, meta_len).decode("utf-8"))

    dtype = np.dtype(metadata["dtype"])
    shape = tuple(metadata["shape"])

    raw_len = struct.unpack("!Q", recv_exact(conn, 8))[0]
    raw = recv_exact(conn, raw_len)

    arr = np.frombuffer(raw, dtype=dtype).reshape(shape)

    print("Received successfully")
    print("shape:", arr.shape)
    print("dtype:", arr.dtype)
    print("first 10 values:", arr[:10])

    conn.sendall(b"OK")
    return arr

def run_server_once(host="0.0.0.0", port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)

        print(f"Listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            arr = receive_array(conn)
            return arr
        

def run_server_forever(host="0.0.0.0", port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(5)

        print(f"Listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                arr = receive_array(conn)
                plt.figure()
                plt.plot(arr[:200])
                plt.show()

def receive_data(host="0.0.0.0", port=65432, points_per_waveform=16, amount_of_waveforms=1_000_000):
    chunks = []
    received_waveforms = 0

    while received_waveforms < amount_of_waveforms:
        print(f"Waiting... currently have {received_waveforms}/{amount_of_waveforms} waveforms")

        arr = run_server_once(host=host, port=port)

        chunks.append(arr)

        chunk_waveforms = len(arr) // points_per_waveform
        received_waveforms += chunk_waveforms

        print(
            f"Received chunk: points={len(arr)}, "
            f"waveforms={chunk_waveforms}, "
            f"total received={received_waveforms}"
        )

    data = np.concatenate(chunks)

    expected_points = amount_of_waveforms * points_per_waveform
    data = data[:expected_points]

    print("Final number of chunks:", len(chunks))
    print("Final total points:", len(data))
    print("Final total waveforms:", len(data) // points_per_waveform)

    return data


if __name__ == "__main__":
    arr = run_server_once(host="0.0.0.0", port=65432)
    plt.plot(arr[:200])
    plt.show()
    print("Array is now available as variable: arr")
