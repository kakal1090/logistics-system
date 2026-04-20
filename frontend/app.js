import socket
import threading
import time
import json
def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = ""
    PORT = ""  
    server.bind((HOST, PORT))
    server.listen()
    print("Server dang chay")
    conn, addr = server.accept()
    print("Client da ket noi:", addr)
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        order = json.loads(data)
        result = {
            "order_id": order["order_id"],
            "label": "Nhẹ" if order["weight"] < 10 else "Nặng",
            "vehicle": "Xe máy" if order["distance"] < 10 else "Xe tải",
            "processed_time": "0.02s",
            "process_status": "Đã xử lý"
        }
        conn.send(json.dumps(result).encode())
# CLIENT (đọc dữ liệu từ file)
def run_client():
    time.sleep(1)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = ""
    PORT = ""  # phải giống server
    client.connect((HOST, PORT))
    print("Dang doc du lieu tu file...\n")
    # ===== ĐỌC FILE JSON =====
    with open("order.json", "r", encoding="utf-8") as f:
        order_data = json.load(f)
    print("Du lieu doc duoc:", order_data)
    # gửi lên server
    client.send(json.dumps(order_data).encode())
    # nhận kết quả
    data = client.recv(1024).decode()
    result = json.loads(data)
    print("\n===== KET QUA =====")
    print("Ma don:", result["order_id"])
    print("Phan loai:", result["label"])
    print("Phuong tien:", result["vehicle"])
    print("Thoi gian:", result["processed_time"])
    print("Trang thai:", result["process_status"])
    print("===================")
threading.Thread(target=run_server).start()
threading.Thread(target=run_client).start()
