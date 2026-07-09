import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Hệ thống tính tiền dãy trọ",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 HỆ THỐNG TÍNH TIỀN DÃY NHÀ TRỌ")
st.write("Nhập chỉ số điện, nước của từng phòng để tính hóa đơn tự động.")
st.divider()

# =========================
# PHẦN 1: CẤU HÌNH BẢNG GIÁ
# =========================
st.sidebar.header("⚙️ CẤU HÌNH BẢNG GIÁ")

so_phong = st.sidebar.number_input(
    "Số lượng phòng trong dãy:",
    min_value=1,
    max_value=100,
    value=10,
    step=1
)

gia_phong = st.sidebar.number_input(
    "Tiền phòng cố định / phòng (VNĐ):",
    min_value=0,
    value=2500000,
    step=100000
)

gia_dien = st.sidebar.number_input(
    "Giá điện (VNĐ/kWh):",
    min_value=0,
    value=3500,
    step=100
)

gia_nuoc = st.sidebar.number_input(
    "Giá nước (VNĐ/khối):",
    min_value=0,
    value=15000,
    step=500
)

gia_wifi = st.sidebar.number_input(
    "Tiền Wifi / phòng (VNĐ):",
    min_value=0,
    value=100000,
    step=10000
)

gia_rac = st.sidebar.number_input(
    "Tiền rác & dịch vụ / phòng (VNĐ):",
    min_value=0,
    value=50000,
    step=5000
)

st.sidebar.divider()
st.sidebar.info("Nhập bảng giá một lần, hệ thống sẽ áp dụng cho toàn bộ các phòng.")

# =========================
# PHẦN 2: TẠO DỮ LIỆU BAN ĐẦU
# =========================
if "so_phong_cu" not in st.session_state:
    st.session_state.so_phong_cu = so_phong

if "du_lieu_phong" not in st.session_state or st.session_state.so_phong_cu != so_phong:
    st.session_state.du_lieu_phong = pd.DataFrame({
        "Phòng": [f"Phòng {i}" for i in range(1, so_phong + 1)],
        "Số điện cũ": [0] * so_phong,
        "Số điện mới": [0] * so_phong,
        "Số nước cũ": [0] * so_phong,
        "Số nước mới": [0] * so_phong,
        "Số người": [1] * so_phong
    })
    st.session_state.so_phong_cu = so_phong

# =========================
# PHẦN 3: NHẬP DỮ LIỆU
# =========================
st.header("📝 Nhập chỉ số điện nước từng phòng")

st.write("Nhập số điện/nước cũ và mới cho từng phòng. Có thể bấm trực tiếp vào ô để sửa.")

du_lieu_nhap = st.data_editor(
    st.session_state.du_lieu_phong,
    num_rows="fixed",
    use_container_width=True,
    column_config={
        "Phòng": st.column_config.TextColumn("Phòng", disabled=True),
        "Số điện cũ": st.column_config.NumberColumn("Số điện cũ", min_value=0, step=1),
        "Số điện mới": st.column_config.NumberColumn("Số điện mới", min_value=0, step=1),
        "Số nước cũ": st.column_config.NumberColumn("Số nước cũ", min_value=0, step=1),
        "Số nước mới": st.column_config.NumberColumn("Số nước mới", min_value=0, step=1),
        "Số người": st.column_config.NumberColumn("Số người", min_value=1, step=1)
    },
    key="bang_nhap_phong"
)

st.session_state.du_lieu_phong = du_lieu_nhap

# =========================
# PHẦN 4: TÍNH TOÁN
# =========================
ket_qua = du_lieu_nhap.copy()

ket_qua["Số điện dùng"] = ket_qua["Số điện mới"] - ket_qua["Số điện cũ"]
ket_qua["Số nước dùng"] = ket_qua["Số nước mới"] - ket_qua["Số nước cũ"]

# Không cho ra số âm nếu nhập sai
ket_qua["Số điện dùng"] = ket_qua["Số điện dùng"].clip(lower=0)
ket_qua["Số nước dùng"] = ket_qua["Số nước dùng"].clip(lower=0)

ket_qua["Tiền điện"] = ket_qua["Số điện dùng"] * gia_dien
ket_qua["Tiền nước"] = ket_qua["Số nước dùng"] * gia_nuoc

ket_qua["Tiền phòng"] = gia_phong
ket_qua["Wifi"] = gia_wifi
ket_qua["Rác & DV"] = gia_rac

ket_qua["Tổng tiền"] = (
    ket_qua["Tiền phòng"]
    + ket_qua["Tiền điện"]
    + ket_qua["Tiền nước"]
    + ket_qua["Wifi"]
    + ket_qua["Rác & DV"]
)

ket_qua["Mỗi người đóng"] = ket_qua["Tổng tiền"] / ket_qua["Số người"]

# =========================
# PHẦN 5: KIỂM TRA LỖI
# =========================
loi_dien = du_lieu_nhap["Số điện mới"] < du_lieu_nhap["Số điện cũ"]
loi_nuoc = du_lieu_nhap["Số nước mới"] < du_lieu_nhap["Số nước cũ"]

if loi_dien.any() or loi_nuoc.any():
    danh_sach_loi = ket_qua.loc[loi_dien | loi_nuoc, "Phòng"].tolist()
    st.error(
        f"❌ Có số mới nhỏ hơn số cũ ở: {', '.join(danh_sach_loi)}. "
        "Hệ thống đang tạm tính mức tiêu thụ là 0 cho các phòng này."
    )

# =========================
# PHẦN 6: HIỂN THỊ KẾT QUẢ
# =========================
st.divider()
st.header("📊 BẢNG TỔNG HỢP TIỀN CẢ DÃY TRỌ")

tong_doanh_thu = ket_qua["Tổng tiền"].sum()
tong_dien = ket_qua["Tiền điện"].sum()
tong_nuoc = ket_qua["Tiền nước"].sum()

c1, c2, c3 = st.columns(3)

c1.metric("💰 Tổng tiền thu cả dãy", f"{tong_doanh_thu:,.0f} VNĐ")
c2.metric("⚡ Tổng tiền điện", f"{tong_dien:,.0f} VNĐ")
c3.metric("💧 Tổng tiền nước", f"{tong_nuoc:,.0f} VNĐ")

# Chọn cột để hiện trong bảng
bang_hien_thi = ket_qua[
    [
        "Phòng",
        "Số điện mới",
        "Số điện cũ",
        "Tiền điện",
        "Số nước mới",
        "Số nước cũ",
        "Tiền nước",
        "Số người",
        "Tổng tiền",
        "Mỗi người đóng"
    ]
].copy()

# Đổi tiền thành dạng dễ nhìn
for cot in ["Tiền điện", "Tiền nước", "Tổng tiền", "Mỗi người đóng"]:
    bang_hien_thi[cot] = bang_hien_thi[cot].apply(lambda x: f"{x:,.0f} VNĐ")

st.dataframe(
    bang_hien_thi,
    use_container_width=True,
    hide_index=True
)

# =========================
# PHẦN 7: XUẤT FILE EXCEL
# =========================
st.divider()
st.header("📥 Xuất bảng hóa đơn")

file_excel = ket_qua.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇️ Tải bảng tiền trọ về máy (CSV)",
    data=file_excel,
    file_name="bang_tien_day_tro.csv",
    mime="text/csv"
)

# =========================
# PHẦN 8: CHỌN 1 PHÒNG ĐỂ XEM HÓA ĐƠN
# =========================
st.divider()
st.header("📱 Xem hóa đơn từng phòng để gửi Zalo")

phong_chon = st.selectbox("Chọn phòng cần gửi hóa đơn:", ket_qua["Phòng"])

thong_tin_phong = ket_qua[ket_qua["Phòng"] == phong_chon].iloc[0]

tin_nhan = f"""THÔNG BÁO TIỀN PHÒNG - {thong_tin_phong["Phòng"]}

- Tiền phòng: {thong_tin_phong["Tiền phòng"]:,.0f}đ
- Điện: {thong_tin_phong["Số điện dùng"]} kWh x {gia_dien:,.0f}đ
  = {thong_tin_phong["Tiền điện"]:,.0f}đ
- Nước: {thong_tin_phong["Số nước dùng"]} khối x {gia_nuoc:,.0f}đ
  = {thong_tin_phong["Tiền nước"]:,.0f}đ
- Wifi: {thong_tin_phong["Wifi"]:,.0f}đ
- Rác & dịch vụ: {thong_tin_phong["Rác & DV"]:,.0f}đ

TỔNG TIỀN: {thong_tin_phong["Tổng tiền"]:,.0f}đ
Số người trong phòng: {thong_tin_phong["Số người"]}
Mỗi người đóng: {thong_tin_phong["Mỗi người đóng"]:,.0f}đ

Vui lòng thanh toán sớm. Cảm ơn!
"""

st.text_area(
    "Copy tin nhắn này để gửi cho khách:",
    value=tin_nhan,
    height=320
)
