const socket = io("http://localhost:5000");

const orderForm = document.getElementById("orderForm");
const fileUpload = document.getElementById("fileUpload");
const fileName = document.getElementById("fileName");

const processStatus = document.getElementById("processStatus");
const predictedLabel = document.getElementById("predictedLabel");
const assignedVehicle = document.getElementById("assignedVehicle");
const processedTime = document.getElementById("processedTime");

const totalOrders = document.getElementById("totalOrders");
const lightOrders = document.getElementById("lightOrders");
const heavyOrders = document.getElementById("heavyOrders");
const trackingOrders = document.getElementById("trackingOrders");
const tableBody = document.getElementById("tableBody");

let orders = [];

// =========================
// HÀM PHỤ
// =========================
function safeValue(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : "";
}

function toNumber(value) {
  const n = parseFloat(value);
  return Number.isNaN(n) ? 0 : n;
}

function buildPayloadFromForm() {
  return {
    order_id: safeValue("orderId"),
    customer_name: safeValue("customerName"),
    phone: safeValue("phone"),
    email: safeValue("email"),
    address: safeValue("address"),
    product_type: safeValue("productType"),
    weight: toNumber(safeValue("weight")),
    length: toNumber(safeValue("length")),
    width: toNumber(safeValue("width")),
    height: toNumber(safeValue("height")),
    distance: toNumber(safeValue("distance")),
    priority: safeValue("priority"),
    note: safeValue("note")
  };
}

function updateResultBox(data) {
  if (processStatus) {
    processStatus.textContent =
      data.process_status || "Đã xử lý";
  }

  if (predictedLabel) {
    predictedLabel.textContent =
      data.label || "--";
  }

  if (assignedVehicle) {
    assignedVehicle.textContent =
      data.assigned_vehicle || data.vehicle || "--";
  }

  if (processedTime) {
    processedTime.textContent =
      data.processing_time || data.processed_at || "--";
  }
}

function renderTableRow(data) {
  if (!tableBody) return;

  const tr = document.createElement("tr");

  const label = data.label || "--";
  const badgeClass =
    label === "Nhẹ" ? "badge badge-light" :
    label === "Nặng" ? "badge badge-heavy" :
    "badge";

  tr.innerHTML = `
    <td>${data.order_id || "--"}</td>
    <td>${data.customer_name || "--"}</td>
    <td>${data.product_type || "--"}</td>
    <td>${data.weight ?? "--"}${data.weight !== undefined ? " kg" : ""}</td>
    <td>${data.distance ?? "--"}${data.distance !== undefined ? " km" : ""}</td>
    <td><span class="${badgeClass}">${label}</span></td>
    <td>${data.assigned_vehicle || data.vehicle || "--"}</td>
    <td>${data.priority || "--"}</td>
    <td>${data.processing_time || data.processed_at || "--"}</td>
  `;

  tableBody.prepend(tr);
}

function updateSummary() {
  if (totalOrders) totalOrders.textContent = orders.length;

  const light = orders.filter(order => order.label === "Nhẹ").length;
  const heavy = orders.filter(order => order.label === "Nặng").length;

  if (lightOrders) lightOrders.textContent = light;
  if (heavyOrders) heavyOrders.textContent = heavy;
  if (trackingOrders) trackingOrders.textContent = orders.length;
}

function addOrderToDashboard(data) {
  const normalized = {
    order_id: data.order_id || "--",
    customer_name:
      data.customer_name ||
      data.input_features?.customer_name ||
      "--",
    product_type:
      data.product_type ||
      data.input_features?.product_type ||
      data.input_features?.type ||
      "--",
    weight:
      data.weight ??
      data.input_features?.weight,
    distance:
      data.distance ??
      data.input_features?.distance,
    priority:
      data.priority ||
      data.input_features?.priority ||
      "--",
    label: data.label || "--",
    assigned_vehicle:
      data.assigned_vehicle ||
      data.vehicle ||
      "--",
    processing_time:
      data.processing_time || "--",
    processed_at:
      data.processed_at || "--",
    process_status:
      data.process_status || "Đã xử lý"
  };

  orders.unshift(normalized);
  updateResultBox(normalized);
  renderTableRow(normalized);
  updateSummary();
}

function clearDashboard() {
  orders = [];
  if (tableBody) tableBody.innerHTML = "";
  updateSummary();

  if (processStatus) processStatus.textContent = "Chờ xử lý";
  if (predictedLabel) predictedLabel.textContent = "--";
  if (assignedVehicle) assignedVehicle.textContent = "--";
  if (processedTime) processedTime.textContent = "--";
}

// =========================
// FORM SUBMIT
// =========================
if (orderForm) {
  orderForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const payload = buildPayloadFromForm();

    if (!payload.order_id || !payload.customer_name) {
      alert("Vui lòng nhập ít nhất mã đơn và tên khách hàng.");
      return;
    }

    if (processStatus) {
      processStatus.textContent = "Đang xử lý...";
    }

    socket.emit("submit_order", payload);
  });
}

// =========================
// FILE UPLOAD UI
// =========================
if (fileUpload && fileName) {
  fileUpload.addEventListener("change", function () {
    if (this.files && this.files.length > 0) {
      fileName.textContent = this.files[0].name;
    } else {
      fileName.textContent = "Chưa chọn file";
    }
  });
}

// =========================
// SOCKET EVENTS
// =========================
socket.on("connect", () => {
  console.log("Đã kết nối socket server");
  socket.emit("get_history", { limit: 20 });
});

socket.on("connection_ack", (data) => {
  console.log("Server ACK:", data);

  if (Array.isArray(data.history)) {
    clearDashboard();
    data.history.forEach(item => addOrderToDashboard(item));
  }
});

socket.on("order_received", (data) => {
  console.log("Đã nhận đơn:", data);
  if (processStatus) {
    processStatus.textContent = "Đã nhận đơn, đang xử lý...";
  }
});

socket.on("prediction_result", (data) => {
  console.log("Kết quả xử lý:", data);
  addOrderToDashboard(data);
});

socket.on("dashboard_update", (data) => {
  console.log("Cập nhật dashboard:", data);

  if (data?.action === "clear_history" || data?.type === "clear") {
    clearDashboard();
    return;
  }

  addOrderToDashboard(data);
});

socket.on("history_response", (data) => {
  console.log("Lịch sử:", data);

  if (Array.isArray(data.orders)) {
    clearDashboard();
    data.orders.forEach(item => addOrderToDashboard(item));
  }
});

socket.on("history_cleared", (data) => {
  console.log(data?.message || "Đã xóa lịch sử");
  clearDashboard();
});

socket.on("disconnect", () => {
  console.log("Mất kết nối socket server");
  if (processStatus) {
    processStatus.textContent = "Mất kết nối server";
  }
});
socket.on("order_error", (data) => {
  console.error("Lỗi gửi đơn:", data);

  if (processStatus) {
    processStatus.textContent = data.error || "Lỗi dữ liệu";
  }

  alert(data.error || "Dữ liệu không hợp lệ");
});
