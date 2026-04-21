

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime
import time
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

# ── Giá trị hợp lệ – đồng bộ với Người 1, 2, 5 ───────────────────────────────
VALID_PRIORITIES = {"thuong", "nhanh", "hoa_toc"}
VALID_PRODUCT_TYPES = {
    "tieu_chuan", "de_vo", "dong_lanh", "nguy_hiem", "cong_kenh",
    "nong_san", "linh_kien_dien_tu", "my_pham", "hang_tieu_dung"
}

# ── Khởi tạo app ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "logistics_secret_2025"

CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
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

    err = _validate(data)
    if err:
        return jsonify({"error": err}), 400

    result = _handle_order(data)
    socketio.emit("prediction_result", result)
    socketio.emit("dashboard_update", result)
    return jsonify(result), 200


# ══════════════════════════════════════════════════════════════════════════════
# SOCKET EVENTS
# ══════════════════════════════════════════════════════════════════════════════

@socketio.on("connect")
def on_connect():
    """Client vừa kết nối – gửi lại lịch sử 20 đơn gần nhất."""
    print(f"[+] Client kết nối: {request.sid}")
    emit("connection_ack", {
        "message"    : "Kết nối thành công đến Logistics Realtime Server",
        "server_time": _now(),
        "history"    : processed_orders[-20:],
    })


@socketio.on("disconnect")
def on_disconnect():
    print(f"[-] Client ngắt kết nối: {request.sid}")


@socketio.on("submit_order")
def on_submit_order(data):
    """
    Người 5 gửi đơn hàng lên theo đúng format CONTRACT ở đầu file.
    Flow: validate → ack → xử lý → gửi kết quả về người gửi → broadcast dashboard.
    """
    print(f"[>] Nhận đơn từ {request.sid}: {data}")

    # 1. Validate trước – báo lỗi ngay nếu sai field
    err = _validate(data)
    if err:
        emit("order_error", {
            "order_id": data.get("order_id", "UNKNOWN"),
            "error"   : err,
        })
        return

    # 2. Xác nhận đã nhận (UX: spinner trên UI)
    emit("order_received", {
        "order_id"   : data.get("order_id", "UNKNOWN"),
        "received_at": _now(),
        "status"     : "processing",
    })

    # 3. Xử lý KNN + Rule-Based
    result = _handle_order(data)

    # 4. Trả kết quả về đúng client gửi lên
    emit("prediction_result", result)

    # 5. Broadcast cho tất cả client còn lại (bảng dashboard chung)
    socketio.emit("dashboard_update", result, include_self=False)


@socketio.on("get_history")
def on_get_history(data):
    """Người 5 yêu cầu lấy lịch sử. Gửi kèm limit nếu muốn."""
    limit = int(data.get("limit", 20)) if isinstance(data, dict) else 20
    emit("history_response", {
        "orders": processed_orders[-limit:],
        "total" : len(processed_orders),
    })


@socketio.on("clear_history")
def on_clear_history():
    """Xóa lịch sử RAM – dùng khi reset demo."""
    processed_orders.clear()
    # Báo cho người gọi
    emit("history_cleared", {"message": "Đã xóa lịch sử", "time": _now()})
    # Báo cho tất cả dashboard reset bảng
    socketio.emit("dashboard_update", {"action": "clear_history"})


# ══════════════════════════════════════════════════════════════════════════════
# HÀM NỘI BỘ
# ══════════════════════════════════════════════════════════════════════════════

def _validate(data: dict) -> str | None:
    """
    Kiểm tra các field bắt buộc và giá trị hợp lệ.
    Trả về chuỗi lỗi nếu có vấn đề, None nếu hợp lệ.
    """
    required = ["order_id", "customer_name", "phone", "address",
                "product_type", "weight", "length", "width",
                "height", "distance", "priority"]
    for field in required:
        if field not in data or data[field] in (None, ""):
            return f"Thiếu hoặc rỗng field bắt buộc: '{field}'"

    pt = str(data["product_type"]).strip().lower()
    if pt not in VALID_PRODUCT_TYPES:
        return (f"product_type '{pt}' không hợp lệ. "
                f"Chỉ chấp nhận: {sorted(VALID_PRODUCT_TYPES)}")

    pr = str(data["priority"]).strip().lower()
    if pr not in VALID_PRIORITIES:
        return (f"priority '{pr}' không hợp lệ. "
                f"Chỉ chấp nhận: {sorted(VALID_PRIORITIES)}")

    for num_field in ["weight", "length", "width", "height", "distance"]:
        try:
            float(data[num_field])
        except (ValueError, TypeError):
            return f"Field '{num_field}' phải là số."

    return None


def _handle_order(data: dict) -> dict:
    """
    Gọi main.process_order() nếu Người 2 đã merge,
    ngược lại dùng mock để server vẫn chạy độc lập.
    Trả về dict đầy đủ để Người 5 đổ thẳng vào bảng dashboard.
    """
    order_id = data.get("order_id", f"ORD{len(processed_orders)+1:04}")
    weight   = float(data.get("weight", 0))
    distance = float(data.get("distance", 0))

    t_start = time.perf_counter()

    if MAIN_AVAILABLE:
        try:
            label, vehicle = process_order(data)
        except Exception as e:
            label, vehicle = "Lỗi", str(e)
    else:
        label, vehicle = _mock_classify(weight, distance)

    elapsed = time.perf_counter() - t_start

    result = {
        # ── Thông tin đơn hàng (để dashboard render trực tiếp) ──
        "order_id"        : order_id,
        "customer_name"   : data.get("customer_name", ""),
        "product_type"    : str(data.get("product_type", "")).strip().lower(),
        "weight"          : weight,
        "distance"        : distance,
        "priority"        : str(data.get("priority", "")).strip().lower(),
        # ── Kết quả xử lý ───────────────────────────────────────
        "label"           : label,              # "Nặng" | "Nhẹ"
        "assigned_vehicle": vehicle,
        "process_status"  : "done",
        "processed_at"    : _now(),
        "processing_time" : f"{elapsed:.3f}s",
        "source"          : "main.py" if MAIN_AVAILABLE else "mock",
    }

    processed_orders.append(result)
    print(f"[✓] {order_id} → {label} / {vehicle} ({result['processing_time']})")
    return result


def _mock_classify(weight: float, distance: float) -> tuple[str, str]:
    """
    Rule-Based tối giản – chỉ dùng khi main.py chưa có.
    Cùng logic với rule_engine.py của Người 2.
    """
    if weight < 200:
        label   = "Nhẹ"
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
