import socket
import threading
import time
def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = ""  
    PORT = 0    
    server.bind((HOST, PORT))
    server.listen()
    print("Server dang chay")
    conn, addr = server.accept()
    # conn: dùng để gửi dữ liệu
    print("Client da ket noi:", addr)
    while True:
        message = "ORDER_1 - CONFIRMED"
        conn.send(message.encode())
        # encode(): socket gửi dạng byte nên cần encode
        time.sleep(2)
# CLIENT
def run_client():
    time.sleep(1)
    # đợi server chạy trước, tránh lỗi connect
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # tạo client để kết nối server
    HOST = ""   
    PORT = 0    
    client.connect((HOST, PORT))
    print("Client da ket noi server")
    while True:
        data = client.recv(1024).decode()
        # nhận dữ liệu từ server
        # decode(): để đọc được chữ
        if not data:
            break
        print("Nhan duoc:", data)
        # hiển thị dữ liệu (giống dashboard)
threading.Thread(target=run_server).start()
threading.Thread(target=run_client).start()
