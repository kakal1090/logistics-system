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

function toNumber(v) {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

function toInt(v) {
  const n = parseInt(v, 10);
  return isNaN(n) ? 1 : n;
}

function normalizeProductType(value) {
  const v = String(value || "").trim().toLowerCase();

  const map = {
    "tiêu chuẩn": "tieu_chuan",
    "tieu chuan": "tieu_chuan",
    "tieu_chuan": "tieu_chuan",

    "dễ vỡ": "de_vo",
    "de vo": "de_vo",
    "de_vo": "de_vo",

    "đông lạnh": "dong_lanh",
    "dong lanh": "dong_lanh",
    "dong_lanh": "dong_lanh",

    "nguy hiểm": "nguy_hiem",
    "nguy hiem": "nguy_hiem",
    "nguy_hiem": "nguy_hiem",

    "cồng kềnh": "cong_kenh",
    "cong kenh": "cong_kenh",
    "cong_kenh": "cong_kenh",

    "nông sản": "nong_san",
    "nong san": "nong_san",
    "nong_san": "nong_san",

    "linh kiện điện tử": "linh_kien_dien_tu",
    "linh kien dien tu": "linh_kien_dien_tu",
    "linh_kien_dien_tu": "linh_kien_dien_tu",

    "mỹ phẩm": "my_pham",
    "my pham": "my_pham",
    "my_pham": "my_pham",

    "hàng tiêu dùng": "hang_tieu_dung",
    "hang tieu dung": "hang_tieu_dung",
    "hang_tieu_dung": "hang_tieu_dung",
    "do_gia_dung": "hang_tieu_dung",
  };

  return map[v] || v;
}

function normalizePriority(value) {
  const v = String(value || "").trim().toLowerCase();

  const map = {
    "thường": "thuong",
    "thuong": "thuong",
    "normal": "thuong",

    "nhanh": "nhanh",
    "fast": "nhanh",

    "hỏa tốc": "hoa_toc",
    "hoa toc": "hoa_toc",
    "hoa_toc": "hoa_toc",
    "express": "hoa_toc",
  };

  return map[v] || v;
}

function buildPayloadFromForm() {
  const weight   = toNumber(safeValue("weight"));
  const quantity = toInt(safeValue("quantity"));
  const totalWeight = weight * quantity;

  return {
    order_id:      safeValue("orderId"),
    customer_name: safeValue("customerName"),
    phone:         safeValue("phone"),
    email:         safeValue("email"),
    address:       safeValue("address"),
    product_type:  normalizeProductType(safeValue("productType")),

    weight:        weight,
    quantity:      quantity,
    total_weight:  totalWeight,

    length:        toNumber(safeValue("length")),
    width:         toNumber(safeValue("width")),
    height:        toNumber(safeValue("height")),
    distance:      toNumber(safeValue("distance")),
    priority:      normalizePriority(safeValue("priority")),
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
  if (processStatus) {
    processStatus.textContent = data.process_status || "Đã xử lý";
  }

  if (predictedLabel) {
    predictedLabel.textContent = data.label || "--";
  }

  if (assignedVehicle) {
    assignedVehicle.textContent = data.assigned_vehicle || "--";
  }

  if (processedTime) {
    processedTime.textContent = data.processing_time || data.processed_at || "--";
  }

  if (totalWeightBox) {
    totalWeightBox.textContent =
      data.total_weight != null ? Number(data.total_weight).toFixed(2) + " kg" : "--";
  }
}

function normalizeLabel(label) {
  const r = String(label || "").trim().toLowerCase();

  if (["nhẹ", "nhe", "light"].includes(r)) {
    return "Nhẹ";
  }

  if (["trung bình", "trung_binh", "trung binh", "medium"].includes(r)) {
    return "Trung bình";
  }

  if (["nặng", "nang", "heavy"].includes(r)) {
    return "Nặng";
  }

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
  const tw         = data.total_weight != null ? Number(data.total_weight).toFixed(2) : "--";

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
  if (data.action === "clear_history") return;

  const w = data.weight ?? 0;
  const q = data.quantity ?? 1;

  const normalized = {
    order_id:         data.order_id || "--",
    customer_name:    data.customer_name || "--",
    product_type:     data.product_type || "--",

    weight:           w,
    quantity:         q,
    total_weight:     data.total_weight != null ? data.total_weight : w * q,

    distance:         data.distance ?? "--",
    priority:         data.priority || "--",

    label:            normalizeLabel(data.label),
    assigned_vehicle: data.assigned_vehicle || data.vehicle || "--",

    processing_time:  data.processing_time || "--",
    processed_at:     data.processed_at || "--",
    process_status:   data.process_status || "Đã xử lý",
  };

  orders.unshift(normalized);

  updateResultBox(normalized);
  renderTableRow(normalized);
  updateSummary();
}

function clearDashboard() {
  orders = [];

  if (tableBody)       tableBody.innerHTML         = "";
  if (processStatus)   processStatus.textContent   = "Chờ xử lý";
  if (predictedLabel)  predictedLabel.textContent  = "--";
  if (assignedVehicle) assignedVehicle.textContent = "--";
  if (processedTime)   processedTime.textContent   = "--";
  if (totalWeightBox)  totalWeightBox.textContent  = "--";

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

  if (!checked.length) {
    alert("Chưa chọn dòng nào.");
    return;
  }

  const ids = Array.from(checked).map(cb => cb.dataset.orderId);

  orders = orders.filter(o => !ids.includes(o.order_id));

  ids.forEach(id => {
    const row = tableBody.querySelector(`tr[data-order-id="${id}"]`);
    if (row) row.remove();
  });

  updateSummary();
}


// ── Buttons ──────────────────────────────────────────────────

if (resetFormBtn) {
  resetFormBtn.addEventListener("click", resetFormFields);
}

if (deleteSelectedBtn) {
  deleteSelectedBtn.addEventListener("click", deleteSelectedRows);
}

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

    if (!payload.product_type) {
      alert("Vui lòng chọn loại hàng hóa.");
      return;
    }

    if (!payload.priority) {
      alert("Vui lòng chọn mức độ ưu tiên.");
      return;
    }

    if (payload.weight <= 0) {
      alert("Khối lượng phải lớn hơn 0.");
      return;
    }

    if (payload.quantity <= 0) {
      alert("Số lượng phải lớn hơn 0.");
      return;
    }

    console.log("Payload nhập tay gửi lên backend:", payload);

    if (processStatus) {
      processStatus.textContent = "Đang xử lý...";
    }

    socket.emit("submit_order", payload);
  });
}


// =========================
// FILE UPLOAD
// =========================

function normalizeImportKey(key) {
  return String(key || "")
    .replace(/^\uFEFF/, "")
    .trim()
    .toLowerCase();
}

function normalizeImportRow(row) {
  const fixed = {};

  Object.keys(row || {}).forEach((key) => {
    const cleanKey = normalizeImportKey(key);
    fixed[cleanKey] = row[key];
  });

  return fixed;
}

if (fileUpload && fileName) {
  fileUpload.addEventListener("change", async function () {
    if (!this.files || !this.files.length) {
      fileName.textContent = "Chưa chọn file";
      return;
    }

    const file = this.files[0];
    fileName.textContent = file.name;

    const ext = file.name.split(".").pop().toLowerCase();

    try {
      let rows = [];

      if (ext === "json") {
        rows = JSON.parse(await file.text());
      } else if (ext === "csv") {
        const text = await file.text();

        if (typeof XLSX === "undefined") {
          alert("Thiếu thư viện XLSX để đọc CSV/Excel.");
          return;
        }

        const wb = XLSX.read(text, { type: "string" });
        rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], {
          defval: ""
        });
      } else if (["xlsx", "xls"].includes(ext)) {
        if (typeof XLSX === "undefined") {
          alert("Thiếu thư viện XLSX để đọc CSV/Excel.");
          return;
        }

        const buffer = await file.arrayBuffer();
        const wb = XLSX.read(buffer, { type: "array" });
        rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], {
          defval: ""
        });
      } else {
        alert("Định dạng file chưa hỗ trợ.");
        return;
      }

      if (!Array.isArray(rows) || !rows.length) {
        alert("File không có dữ liệu hợp lệ.");
        return;
      }

      console.log("Dòng đầu đọc từ file:", rows[0]);

      let sentCount = 0;
      let skippedCount = 0;

      for (const rawRow of rows) {
        const row = normalizeImportRow(rawRow);

        const weight = Number(row.weight || 0);
        const quantity = Number(row.quantity || 1);

        const payload = {
          order_id:      String(row.order_id || "").trim(),
          customer_name: String(row.customer_name || "").trim(),
          phone:         String(row.phone || "").trim(),
          email:         String(row.email || "").trim(),
          address:       String(row.address || "").trim(),
          product_type:  normalizeProductType(row.product_type),

          weight:        weight,
          quantity:      quantity,

          // QUAN TRỌNG:
          // Không lấy total_weight cũ, label cũ, vehicle_type cũ từ file.
          // Backend sẽ tự tính lại total_weight và chạy KNN/rule.
          total_weight:  weight * quantity,

          length:        Number(row.length || 0),
          width:         Number(row.width || 0),
          height:        Number(row.height || 0),
          distance:      Number(row.distance || 0),
          priority:      normalizePriority(row.priority),
          note:          String(row.note || "").trim(),
        };

        if (
          !payload.order_id ||
          !payload.customer_name ||
          !payload.phone ||
          !payload.address ||
          !payload.product_type ||
          !payload.priority ||
          payload.weight <= 0 ||
          payload.quantity <= 0
        ) {
          console.warn("Bỏ qua dòng lỗi:", payload);
          skippedCount++;
          continue;
        }

        console.log("Payload import gửi lên backend:", payload);

        socket.emit("submit_order", payload);
        sentCount++;
      }

      alert(`Đã gửi ${sentCount} đơn hàng từ file lên hệ thống. Bỏ qua ${skippedCount} dòng lỗi.`);
    } catch (err) {
      console.error(err);
      alert("Không đọc được file hoặc file sai cấu trúc.");
    }
  });
}


// =========================
// SOCKET RESPONSE
// =========================

socket.on("order_received", (data) => {
  console.log("Server đã nhận đơn:", data);

  if (processStatus) {
    processStatus.textContent = "Đang xử lý...";
  }
});

socket.on("prediction_result", (data) => {
  console.log("Kết quả phân loại:", data);
  addOrderToDashboard(data);
});

socket.on("dashboard_update", (data) => {
  console.log("Dashboard update:", data);

  if (data && data.action === "clear_history") {
    clearDashboard();
  }
});

socket.on("history_response", (data) => {
  console.log("History:", data);

  clearDashboard();

  const history = Array.isArray(data.orders) ? data.orders : [];

  history.forEach(order => {
    addOrderToDashboard(order);
  });
});

socket.on("history_cleared", (data) => {
  console.log("Đã xóa history:", data);
  clearDashboard();
});

socket.on("order_error", (data) => {
  console.error("Lỗi xử lý đơn:", data);

  if (processStatus) {
    processStatus.textContent = "Lỗi";
  }

  alert(`Lỗi đơn ${data.order_id || ""}: ${data.error || "Không xác định"}`);
});

socket.on("connect_error", (err) => {
  console.error("Không kết nối được socket server:", err);

  if (processStatus) {
    processStatus.textContent = "Mất kết nối server";
  }
});
