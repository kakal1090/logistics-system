const socket = io("http://localhost:5000");
socket.on("connect", () => {
  console.log("Đã kết nối socket server");
  socket.emit("get_history", { limit: 20 });
});

// ── DOM refs ──────────────────────────────────────────────────
const orderForm       = document.getElementById("orderForm");
const fileUpload      = document.getElementById("fileUpload");
const fileName        = document.getElementById("fileName");

const processStatus   = document.getElementById("processStatus");
const predictedLabel  = document.getElementById("predictedLabel");
const assignedVehicle = document.getElementById("assignedVehicle");
const processedTime   = document.getElementById("processedTime");
const totalWeightBox  = document.getElementById("totalWeightBox");

const totalOrders    = document.getElementById("totalOrders");
const lightOrders    = document.getElementById("lightOrders");
const mediumOrders   = document.getElementById("mediumOrders");
const heavyOrders    = document.getElementById("heavyOrders");
const trackingOrders = document.getElementById("trackingOrders");

const tableBody         = document.getElementById("tableBody");
const deleteSelectedBtn = document.getElementById("deleteSelectedBtn");
const clearAllBtn       = document.getElementById("clearAllBtn");
const resetFormBtn      = document.getElementById("resetFormBtn");

let orders = [];

// =========================
// HÀM PHỤ
// =========================
function safeValue(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : "";
}
function toNumber(v) { const n = parseFloat(v); return isNaN(n) ? 0 : n; }
function toInt(v)    { const n = parseInt(v, 10); return isNaN(n) ? 1 : n; }

function buildPayloadFromForm() {
  const weight   = toNumber(safeValue("weight"));
  const quantity = toInt(safeValue("quantity"));
  return {
    order_id:      safeValue("orderId"),
    customer_name: safeValue("customerName"),
    phone:         safeValue("phone"),
    email:         safeValue("email"),
    address:       safeValue("address"),
    product_type:  safeValue("productType"),
    weight,
    quantity,
    total_weight:  weight * quantity,
    length:        toNumber(safeValue("length")),
    width:         toNumber(safeValue("width")),
    height:        toNumber(safeValue("height")),
    distance:      toNumber(safeValue("distance")),
    priority:      safeValue("priority"),
    note:          safeValue("note"),
  };
}

// ── Live preview tổng KL + gợi ý nhãn ────────────────────────
function getLabelHint(tw) {
  if (tw <= 0)    return "";
  if (tw < 200)   return "→ Dự kiến: Nhẹ";
  if (tw <= 1500) return "→ Dự kiến: Trung bình";
  return "→ Dự kiến: Nặng";
}

["weight", "quantity"].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener("input", () => {
    const w  = toNumber(safeValue("weight"));
    const q  = toInt(safeValue("quantity")) || 1;
    const tw = w * q;
    const preview = document.getElementById("totalWeightPreview");
    const hint    = document.getElementById("labelHint");
    if (preview) preview.textContent = tw.toFixed(2) + " kg";
    if (hint)    hint.textContent    = getLabelHint(tw);
  });
});

// ── Kết quả ──────────────────────────────────────────────────
function updateResultBox(data) {
  if (processStatus)   processStatus.textContent  = data.process_status || "Đã xử lý";
  if (predictedLabel)  predictedLabel.textContent  = data.label || "--";
  if (assignedVehicle) assignedVehicle.textContent = data.assigned_vehicle || "--";
  if (processedTime)   processedTime.textContent   = data.processing_time || data.processed_at || "--";
  if (totalWeightBox)  totalWeightBox.textContent  =
    data.total_weight != null ? (+data.total_weight).toFixed(2) + " kg" : "--";
}

function normalizeLabel(label) {
  const r = String(label || "").trim().toLowerCase();
  if (["nhẹ","nhe","light"].includes(r))                                  return "Nhẹ";
  if (["trung bình","trung_binh","trung binh","medium"].includes(r))      return "Trung bình";
  if (["nặng","nang","heavy"].includes(r))                                return "Nặng";
  return label || "--";
}

function getBadgeClass(label) {
  if (label === "Nhẹ")        return "badge badge-light";
  if (label === "Trung bình") return "badge badge-medium";
  if (label === "Nặng")       return "badge badge-heavy";
  return "badge";
}

function renderTableRow(data) {
  if (!tableBody) return;
  const label      = data.label || "--";
  const badgeClass = getBadgeClass(label);
  const tw         = data.total_weight != null ? (+data.total_weight).toFixed(2) : "--";

  const tr = document.createElement("tr");
  tr.dataset.orderId = data.order_id || "";
  tr.innerHTML = `
    <td><input type="checkbox" class="row-checkbox" data-order-id="${data.order_id || ""}"></td>
    <td>${data.order_id || "--"}</td>
    <td>${data.customer_name || "--"}</td>
    <td>${data.product_type || "--"}</td>
    <td>${data.weight != null ? data.weight : "--"}</td>
    <td>${data.quantity != null ? data.quantity : "--"}</td>
    <td>${tw}</td>
    <td>${data.distance != null ? data.distance + " km" : "--"}</td>
    <td><span class="${badgeClass}">${label}</span></td>
    <td>${data.assigned_vehicle || "--"}</td>
    <td>${data.priority || "--"}</td>
    <td>${data.processing_time || data.processed_at || "--"}</td>
  `;
  tableBody.prepend(tr);
}

function updateSummary() {
  const light  = orders.filter(o => o.label === "Nhẹ").length;
  const medium = orders.filter(o => o.label === "Trung bình").length;
  const heavy  = orders.filter(o => o.label === "Nặng").length;
  if (totalOrders)    totalOrders.textContent    = orders.length;
  if (lightOrders)    lightOrders.textContent    = light;
  if (mediumOrders)   mediumOrders.textContent   = medium;
  if (heavyOrders)    heavyOrders.textContent    = heavy;
  if (trackingOrders) trackingOrders.textContent = orders.length;
}

function addOrderToDashboard(data) {
  if (!data || typeof data !== "object") return;
  const w = data.weight   ?? 0;
  const q = data.quantity ?? 1;
  const normalized = {
    order_id:         data.order_id || "--",
    customer_name:    data.customer_name || "--",
    product_type:     data.product_type  || "--",
    weight:           w,
    quantity:         q,
    total_weight:     data.total_weight != null ? data.total_weight : w * q,
    distance:         data.distance ?? "--",
    priority:         data.priority  || "--",
    label:            normalizeLabel(data.label),
    assigned_vehicle: data.assigned_vehicle || data.vehicle || "--",
    processing_time:  data.processing_time || "--",
    processed_at:     data.processed_at    || "--",
    process_status:   data.process_status  || "Đã xử lý",
  };
  orders.unshift(normalized);
  updateResultBox(normalized);
  renderTableRow(normalized);
  updateSummary();
}

function clearDashboard() {
  orders = [];
  if (tableBody)       tableBody.innerHTML          = "";
  if (processStatus)   processStatus.textContent    = "Chờ xử lý";
  if (predictedLabel)  predictedLabel.textContent   = "--";
  if (assignedVehicle) assignedVehicle.textContent  = "--";
  if (processedTime)   processedTime.textContent    = "--";
  if (totalWeightBox)  totalWeightBox.textContent   = "--";
  updateSummary();
}

function resetFormFields() {
  if (orderForm)  orderForm.reset();
  if (fileUpload) fileUpload.value = "";
  if (fileName)   fileName.textContent = "Chưa chọn file";
  const preview = document.getElementById("totalWeightPreview");
  const hint    = document.getElementById("labelHint");
  if (preview) preview.textContent = "0 kg";
  if (hint)    hint.textContent    = "";
  if (processStatus)   processStatus.textContent   = "Chờ xử lý";
  if (predictedLabel)  predictedLabel.textContent  = "--";
  if (assignedVehicle) assignedVehicle.textContent = "--";
  if (processedTime)   processedTime.textContent   = "--";
  if (totalWeightBox)  totalWeightBox.textContent  = "--";
}

function deleteSelectedRows() {
  const checked = document.querySelectorAll(".row-checkbox:checked");
  if (!checked.length) { alert("Chưa chọn dòng nào."); return; }
  const ids = Array.from(checked).map(cb => cb.dataset.orderId);
  orders = orders.filter(o => !ids.includes(o.order_id));
  ids.forEach(id => {
    const row = tableBody.querySelector(`tr[data-order-id="${id}"]`);
    if (row) row.remove();
  });
  updateSummary();
}

// ── Event listeners ───────────────────────────────────────────
if (resetFormBtn)      resetFormBtn.addEventListener("click", resetFormFields);
if (deleteSelectedBtn) deleteSelectedBtn.addEventListener("click", deleteSelectedRows);
if (clearAllBtn) {
  clearAllBtn.addEventListener("click", () => {
    if (confirm("Bạn có chắc muốn xóa toàn bộ dữ liệu?")) {
      socket.emit("clear_history");
    }
  });
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
    if (processStatus) processStatus.textContent = "Đang xử lý...";
    socket.emit("submit_order", payload);
  });
}

// =========================
// FILE UPLOAD
// =========================
if (fileUpload && fileName) {
  fileUpload.addEventListener("change", async function () {
    if (!this.files || !this.files.length) { fileName.textContent = "Chưa chọn file"; return; }
    const file = this.files[0];
    fileName.textContent = file.name;
    const ext = file.name.split(".").pop().toLowerCase();
    try {
      let rows = [];
      if (ext === "json") {
        rows = JSON.parse(await file.text());
      } else if (ext === "csv") {
        const wb = XLSX.read(await file.text(), { type: "string" });
        rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
      } else if (["xlsx","xls"].includes(ext)) {
        const wb = XLSX.read(await file.arrayBuffer(), { type: "array" });
        rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
      } else { alert("Định dạng file chưa hỗ trợ."); return; }

      if (!Array.isArray(rows) || !rows.length) { alert("File không có dữ liệu hợp lệ."); return; }

      for (const row of rows) {
        const weight   = Number(row.weight   || 0);
        const quantity = Number(row.quantity || 1);
        socket.emit("submit_order", {
          order_id:      String(row.order_id      || "").trim(),
          customer_name: String(row.customer_name || "").trim(),
          phone:         String(row.phone         || "").trim(),
          email:         String(row.email         || "").trim(),
          address:       String(row.address       || "").trim(),
          product_type:  String(row.product_type  || "").trim().toLowerCase(),
          weight, quantity,
          total_weight:  weight * quantity,
          length:        Number(row.length   || 0),
          width:         Number(row.width    || 0),
          height:        Number(row.height   || 0),
          distance:      Number(row.distance || 0),
          priority:      String(row.priority || "").trim().toLowerCase(),
          note:          String(row.note     || "").trim(),
        });
      }
      alert(`Đã gửi ${rows.length} đơn hàng từ file lên hệ thống.`);
    } catch (err) {
      console.error(err);
      alert("Không đọc được file hoặc file sai cấu trúc.");
    }
  });
}

// =========================
// SOCKET EVENTS
// =========================
socket.on("connection_ack", (data) => {
  if (Array.isArray(data.history)) {
    clearDashboard();
    data.history.forEach(item => addOrderToDashboard(item));
  }
});
socket.on("order_received", () => {
  if (processStatus) processStatus.textContent = "Đã nhận đơn, đang xử lý...";
});
socket.on("prediction_result", (data) => { addOrderToDashboard(data); });
socket.on("dashboard_update",  (data) => {
  if (data?.action === "clear_history") { clearDashboard(); return; }
  addOrderToDashboard(data);
});
socket.on("history_response", (data) => {
  if (Array.isArray(data.orders)) {
    clearDashboard();
    data.orders.forEach(item => addOrderToDashboard(item));
  }
});
socket.on("history_cleared", ()     => { clearDashboard(); });
socket.on("order_error",     (data) => {
  if (processStatus) processStatus.textContent = data.error || "Lỗi dữ liệu";
  alert(data.error || "Dữ liệu không hợp lệ");
});
socket.on("disconnect", () => {
  if (processStatus) processStatus.textContent = "Mất kết nối server";
});
