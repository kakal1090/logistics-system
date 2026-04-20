"""
socket_server.py
Người 3 – Realtime / kết nối hệ thống
Nhiệm vụ:
  - Khởi chạy Flask + Socket.IO server
  - Nhận đơn hàng từ frontend qua socket event
  - Gọi sang main.py để xử lý KNN + Rule-Based
  - Phát kết quả realtime về dashboard (không cần reload trang)
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime
import json
import sys
import os

# ── Cho phép import main.py cùng thư mục backend ──────────────────────────────
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import process_order          # hàm chính do Người 2 viết
    MAIN_AVAILABLE = True
except ImportError:
    MAIN_AVAILABLE = False
    print("[WARNING] main.py chưa sẵn sàng – server vẫn chạy ở chế độ mock.")

# ── Khởi tạo app ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "logistics_secret_2025"

CORS(app, resources={r"/*": {"origins": "*"}})          # cho phép frontend local
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",                              # tương thích mọi môi trường
    ping_timeout=60,
    ping_interval=25,
)

# ── Lưu lịch sử các đơn đã xử lý trong session (RAM) ─────────────────────────
processed_orders: list[dict] = []


# ══════════════════════════════════════════════════════════════════════════════
# REST endpoint – kiểm tra server còn sống không
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status"     : "ok",
        "server_time": _now(),
        "main_ready" : MAIN_AVAILABLE,
        "orders_done": len(processed_orders),
    })


# ══════════════════════════════════════════════════════════════════════════════
# REST endpoint – nhận đơn hàng qua HTTP POST (phụ, để test bằng Postman/curl)
# ══════════════════════════════════════════════════════════════════════════════
@app.route("/api/order", methods=["POST"])
def api_receive_order():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Dữ liệu JSON không hợp lệ"}), 400

    result = _handle_order(data)
    # Sau khi xử lý, broadcast kết quả cho tất cả client đang kết nối
    socketio.emit("prediction_result", result)
    return jsonify(result), 200


# ══════════════════════════════════════════════════════════════════════════════
# SOCKET EVENTS
# ══════════════════════════════════════════════════════════════════════════════

@socketio.on("connect")
def on_connect():
    """Client vừa kết nối – gửi lại toàn bộ lịch sử gần đây."""
    print(f"[+] Client kết nối: {request.sid}")
    emit("connection_ack", {
        "message"   : "Kết nối thành công đến Logistics Realtime Server",
        "server_time": _now(),
        "history"   : processed_orders[-20:],    # 20 đơn gần nhất
    })


@socketio.on("disconnect")
def on_disconnect():
    print(f"[-] Client ngắt kết nối: {request.sid}")


@socketio.on("submit_order")
def on_submit_order(data):
    """
    Frontend gửi đơn hàng lên.
    Payload mẫu:
    {
        "order_id" : "ORD001",
        "weight"   : 12.5,       # kg
        "length"   : 30,         # cm
        "width"    : 20,         # cm
        "height"   : 15,         # cm
        "type"     : "Dễ vỡ",
        "priority" : "Nhanh",
        "distance" : 8           # km (tùy chọn – dùng cho rule-based)
    }
    """
    print(f"[>] Nhận đơn từ {request.sid}: {data}")

    # Xác nhận đã nhận ngay lập tức (UX tốt hơn)
    emit("order_received", {
        "order_id"  : data.get("order_id", "UNKNOWN"),
        "received_at": _now(),
        "status"    : "processing",
    })

    # Xử lý KNN + Rule-Based
    result = _handle_order(data)

    # Gửi kết quả về đúng client gửi lên
    emit("prediction_result", result)

    # Đồng thời broadcast cho tất cả client (dashboard theo dõi chung)
    socketio.emit("dashboard_update", result, include_self=False)


@socketio.on("get_history")
def on_get_history(data):
    """Client yêu cầu lấy lịch sử xử lý."""
    limit = int(data.get("limit", 20)) if isinstance(data, dict) else 20
    emit("history_response", {
        "orders": processed_orders[-limit:],
        "total" : len(processed_orders),
    })


@socketio.on("clear_history")
def on_clear_history():
    """Xóa lịch sử trong RAM (dùng khi demo/test)."""
    processed_orders.clear()
    emit("history_cleared", {"message": "Đã xóa lịch sử", "time": _now()})
    socketio.emit("dashboard_update", {"type": "clear"})


# ══════════════════════════════════════════════════════════════════════════════
# HÀM NỘI BỘ
# ══════════════════════════════════════════════════════════════════════════════

def _handle_order(data: dict) -> dict:
    """
    Gọi main.process_order() nếu Người 2 đã merge,
    ngược lại dùng mock để server vẫn chạy được độc lập.
    """
    order_id = data.get("order_id", f"ORD{len(processed_orders)+1:04}")

    if MAIN_AVAILABLE:
        try:
            label, vehicle = process_order(data)
        except Exception as e:
            label, vehicle = "Lỗi", str(e)
    else:
        # ── MOCK: dùng khi main.py chưa sẵn sàng ────────────────────────────
        weight   = float(data.get("weight", 0))
        distance = float(data.get("distance", 0))
        label, vehicle = _mock_classify(weight, distance)

    result = {
        "order_id"        : order_id,
        "label"           : label,          # "Nặng" | "Nhẹ"
        "assigned_vehicle": vehicle,        # "Xe máy", "Xe tải 1.5 tấn", …
        "input_features"  : data,
        "processed_at"    : _now(),
        "source"          : "main.py" if MAIN_AVAILABLE else "mock",
    }

    processed_orders.append(result)
    print(f"[✓] {order_id} → {label} / {vehicle}")
    return result


def _mock_classify(weight: float, distance: float) -> tuple[str, str]:
    """
    Rule-Based tối giản – chỉ dùng khi main.py chưa có.
    Cùng logic với rule_engine.py của Người 2.
    """
    if weight < 200:
        label = "Nhẹ"
        vehicle = "Xe máy" if (weight < 15 and distance < 10) else "Xe Tải Van"
    else:
        label = "Nặng"
        if weight <= 1500:
            vehicle = "Xe tải 1.5 tấn"
        elif weight <= 5000:
            vehicle = "Xe tải 5 tấn"
        else:
            vehicle = "Xe Đầu kéo / Container"
    return label, vehicle


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 55)
    print("  Logistics Realtime Server  –  Người 3")
    print("  Socket.IO  |  Flask  |  Python")
    print("=" * 55)
    print(f"  main.py sẵn sàng : {MAIN_AVAILABLE}")
    print(f"  Khởi chạy tại    : http://localhost:5000")
    print(f"  Health check     : http://localhost:5000/health")
    print("=" * 55)

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,     # tắt reloader tránh chạy 2 lần khi debug
    )
