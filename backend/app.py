import socket
import threading
import time
def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tạo server dùng TCP để giao tiếp
    HOST = ""   
    PORT = 0    
    server.bind((HOST, PORT))
    # gán địa chỉ cho server, thiếu dòng này server không chạy đúng
    server.listen()
    print("Server dang chay")
    conn, addr = server.accept()
    # conn: dùng để gửi dữ liệu
    print("Client da ket noi:", addr)
    while True:
        message = "ORDER_1 - CONFIRMED"
        conn.send(message.encode())
        # gửi dữ liệu sang client
        # encode(): bắt buộc vì socket chỉ gửi được dạng byte
        time.sleep(2)
        # gửi mỗi 2 giây (giả lập realtime)
# CLIENT
def run_client():
    time.sleep(1)
    # đợi server chạy trước, tránh lỗi connect
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tạo client để kết nối server
    HOST = ""  
    PORT = 0    
    client.connect((HOST, PORT))
    # dòng quan trọng nhất của client: kết nối tới server
    print("Client da ket noi server")
    while True:
        data = client.recv(1024).decode()
        # nhận dữ liệu từ server
        if not data:
            break
        print("Nhan duoc:", data)
        # hiển thị dữ liệu (giống dashboard)
# MAIN
threading.Thread(target=run_server).start()
threading.Thread(target=run_client).start()
# chạy server và client cùng lúc trong 1 file
