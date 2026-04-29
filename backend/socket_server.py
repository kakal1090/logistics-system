from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import datetime
import time
import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import process_order
    MAIN_AVAILABLE = True
except Exception as e:
    MAIN_AVAILABLE = False
    print(f"[WARNING] Không import được main.py: {e}")
    print("[WARNING] Server vẫn chạy ở chế độ mock.")


VALID_PRIORITIES = {"thuong", "nhanh", "hoa_toc"}

VALID_PRODUCT_TYPES = {
    "tieu_chuan",
    "de_vo",
    "dong_lanh",
    "nguy_hiem",
    "cong_kenh",
    "nong_san",
    "linh_kien_dien_tu",
    "my_pham",
    "hang_tieu_dung",
    "do_gia_dung",
}


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

processed_orders: list[dict] = []


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "server_time": _now(),
        "main_ready": MAIN_AVAILABLE,
        "orders_done": len(processed_orders),
    })


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


@socketio.on("connect")
def on_connect():
    print(f"[+] Client kết nối: {request.sid}")

    emit("connection_ack", {
        "message": "Kết nối thành công đến Logistics Realtime Server",
        "server_time": _now(),
        "history": processed_orders[-20:],
    })


@socketio.on("disconnect")
def on_disconnect():
    print(f"[-] Client ngắt kết nối: {request.sid}")


@socketio.on("submit_order")
def on_submit_order(data):
    print(f"[>] Nhận đơn từ {request.sid}: {data}")

    err = _validate(data)
    if err:
        emit("order_error", {
            "order_id": data.get("order_id", "UNKNOWN") if isinstance(data, dict) else "UNKNOWN",
            "error": err,
        })
        return

    emit("order_received", {
        "order_id": data.get("order_id", "UNKNOWN"),
        "received_at": _now(),
        "status": "processing",
    })

    result = _handle_order(data)

    emit("prediction_result", result)
    socketio.emit("dashboard_update", result, include_self=False)


@socketio.on("get_history")
def on_get_history(data):
    limit = int(data.get("limit", 20)) if isinstance(data, dict) else 20

    emit("history_response", {
        "orders": processed_orders[-limit:],
        "total": len(processed_orders),
    })


@socketio.on("clear_history")
def on_clear_history():
    processed_orders.clear()

    emit("history_cleared", {
        "message": "Đã xóa lịch sử",
        "time": _now(),
    })

    socketio.emit("dashboard_update", {
        "action": "clear_history",
    })


def _validate(data: dict) -> str | None:
    if not isinstance(data, dict):
        return "Dữ liệu gửi lên phải là object JSON."

    required = [
        "order_id",
        "customer_name",
        "phone",
        "address",
        "product_type",
        "weight",
        "quantity",
        "length",
        "width",
        "height",
        "distance",
        "priority",
    ]

    for field in required:
        if field not in data or data[field] in (None, ""):
            return f"Thiếu hoặc rỗng field bắt buộc: '{field}'"

    product_type = str(data["product_type"]).strip().lower()
    if product_type not in VALID_PRODUCT_TYPES:
        return (
            f"product_type '{product_type}' không hợp lệ. "
            f"Chỉ chấp nhận: {sorted(VALID_PRODUCT_TYPES)}"
        )

    priority = str(data["priority"]).strip().lower()
    if priority not in VALID_PRIORITIES:
        return (
            f"priority '{priority}' không hợp lệ. "
            f"Chỉ chấp nhận: {sorted(VALID_PRIORITIES)}"
        )

    for num_field in ["weight", "length", "width", "height", "distance"]:
        try:
            value = float(data[num_field])
            if value < 0:
                return f"Field '{num_field}' không được âm."
        except (ValueError, TypeError):
            return f"Field '{num_field}' phải là số."

    try:
        quantity = int(float(data.get("quantity", 1)))
        if quantity <= 0:
            return "Field 'quantity' phải lớn hơn 0."
    except (ValueError, TypeError):
        return "Field 'quantity' phải là số nguyên."

    return None


def _handle_order(data: dict) -> dict:
    order_id = str(data.get("order_id", f"ORD{len(processed_orders) + 1:04}")).strip()

    weight = float(data.get("weight", 0))
    quantity = int(float(data.get("quantity", 1)))
    total_weight = weight * quantity
    distance = float(data.get("distance", 0))

    t_start = time.perf_counter()

    # Không đọc label/vehicle_type từ file import nữa.
    # Mọi đơn đều chạy lại qua main.py để đảm bảo Trung bình không bị sai.
    if MAIN_AVAILABLE:
        try:
            label, vehicle = process_order(data)
            source = "main.py"
        except Exception as e:
            print(f"[ERROR] main.py xử lý lỗi: {e}")
            label, vehicle = _mock_classify(
                weight=weight,
                quantity=quantity,
                total_weight=total_weight,
                length=float(data.get("length", 0)),
                width=float(data.get("width", 0)),
                height=float(data.get("height", 0)),
            )
            source = "mock_after_main_error"
    else:
        label, vehicle = _mock_classify(
            weight=weight,
            quantity=quantity,
            total_weight=total_weight,
            length=float(data.get("length", 0)),
            width=float(data.get("width", 0)),
            height=float(data.get("height", 0)),
        )
        source = "mock"

    elapsed = time.perf_counter() - t_start

    result = {
        "order_id": order_id,
        "customer_name": data.get("customer_name", ""),
        "product_type": str(data.get("product_type", "")).strip().lower(),

        "weight": weight,
        "quantity": quantity,
        "total_weight": total_weight,

        "distance": distance,
        "priority": str(data.get("priority", "")).strip().lower(),

        "label": label,
        "assigned_vehicle": vehicle,

        "process_status": "done",
        "processed_at": _now(),
        "processing_time": f"{elapsed:.3f}s",
        "source": source,
    }

    processed_orders.append(result)

    print(
        f"[✓] {order_id} | qty={quantity} | total={total_weight:.2f}kg "
        f"| source={source} → {label} / {vehicle} ({result['processing_time']})"
    )

    return result


def _mock_classify(
    weight: float,
    quantity: int,
    total_weight: float,
    length: float,
    width: float,
    height: float,
) -> tuple[str, str]:

    if total_weight < 200:
        label = "Nhẹ"
        if length <= 80 and width <= 80 and height <= 80 and total_weight < 100:
            vehicle = "Xe máy"
        else:
            vehicle = "Xe tải"

    elif total_weight <= 1500:
        label = "Trung bình"
        vehicle = "Xe tải"

    else:
        label = "Nặng"
        if total_weight <= 5000:
            vehicle = "Xe dưới 5 tấn"
        else:
            vehicle = "Xe đầu kéo / Container"

    return label, vehicle


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    print("=" * 60)
    print("  Logistics Realtime Server")
    print("  Socket.IO | Flask | Python")
    print("=" * 60)
    print(f"  main.py sẵn sàng : {MAIN_AVAILABLE}")
    print("  Khởi chạy tại    : http://localhost:5000")
    print("  Health check     : http://localhost:5000/health")
    print("=" * 60)

    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
    )
