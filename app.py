import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# 設定網頁標題與圖標
st.set_page_config(page_title="Home Cafe Invoice Generator", page_icon="☕", layout="wide")

st.title("☕ Home Cafe 輕量化智能開單系統")
st.markdown("填寫以下客戶與商品資料，即可實時預覽並生成 PDF 發票/收據。")

# --- 預設產品資料庫 (可自行修改價格) ---
PRODUCT_DATABASE = {
    "Colombia El Diviso Sidra (100g)": 45.00,
    "Colombia El Diviso Sidra (200g)": 89.00,
    "Peru SL9 (100g)": 55.00,
    "Peru SL9 (200g)": 99.00,
    "其他自訂單品/外賣餐點": 0.00
}

# 欄位版面配置：左邊輸入資料，右邊實時預覽與導出
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 1. 填寫基本資料")
    
    # 發票詳情
    c1, c2 = st.columns(2)
    with c1:
        invoice_no = st.text_input("發票/收據編號", f"INV-{datetime.now().strftime('%Y%m%d')}-01")
    with c2:
        invoice_date = st.date_input("開單日期", datetime.now())

    # 客戶詳情
    customer_name = st.text_input("客戶姓名 / 公司名稱 (B2B 報銷用)")
    customer_phone = st.text_input("聯絡電話 (選填)")
    customer_addr = st.text_area("送貨地址 / 備註 (選填)", height=70)
    
    st.write("---")
    st.subheader("🛒 2. 選擇商品與數量")
    
    # 商品選擇清單
    if 'items' not in st.session_state:
        st.session_state.items = []

    selected_prod = st.selectbox("選擇咖啡豆 / 品項", list(PRODUCT_DATABASE.keys()))
    
    # 如果選擇自訂品項，允許手動輸入價格
    if selected_prod == "其他自訂單品/外賣餐點":
        custom_name = st.text_input("請輸入自訂品項名稱", "手工精品黑咖啡")
        unit_price = st.number_input("單價 (RM)", min_value=0.0, value=15.0, step=0.5)
        prod_name = custom_name
    else:
        unit_price = PRODUCT_DATABASE[selected_prod]
        st.info(f"系統預設單價: RM {unit_price:.2f}")
        prod_name = selected_prod

    quantity = st.number_input("數量", min_value=1, value=1, step=1)
    
    if st.button("➕ 新增至清單"):
        st.session_state.items.append({
            "品項": prod_name,
            "單價 (RM)": unit_price,
            "數量": quantity,
            "總額 (RM)": unit_price * quantity
        })
        st.success(f"已成功新增: {prod_name} x{quantity}")

    # 清空清單按鈕
    if st.button("🗑️ 清空所有品項"):
        st.session_state.items = []
        st.rerun()

# 右側：清單顯示、總額計算與 PDF 生成
with col2:
    st.subheader("📄 3. 發票明細與預覽")
    
    if st.session_state.items:
        df = pd.DataFrame(st.session_state.items)
        st.table(df)
        
        # 計算總金額
        subtotal = df["總額 (RM)"].sum()
        st.metric(label="💰 應付總金額 (Total Amount)", value=f"RM {subtotal:.2f}")
        
        # --- PDF 生成邏輯 ---
        class PDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 16)
                self.cell(0, 10, 'INVOICE / RECEIPT', ln=True, align='R')
                self.set_font('Helvetica', '', 10)
                self.cell(0, 5, '☕ HOME CAFE ROASTERY', ln=True, align='L')
                self.cell(0, 5, f"Date: {invoice_date.strftime('%Y-%m-%d')}", ln=True, align='R')
                self.cell(0, 5, f"Invoice No: {invoice_no}", ln=True, align='R')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.cell(0, 10, 'Thank you for your business! Freshly roasted, freshly brewed.', align='C')

        if st.button("🚀 生成並下載 PDF 發票"):
            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=10)
            
            # 寫入客戶資料
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(0, 6, "BILL TO:", ln=True)
            pdf.set_font("Helvetica", size=10)
            pdf.cell(0, 6, f"Customer: {customer_name}", ln=True)
            if customer_phone:
                pdf.cell(0, 6, f"Phone: {customer_phone}", ln=True)
            if customer_addr:
                pdf.cell(0, 6, f"Address/Note: {customer_addr}", ln=True)
            pdf.ln(10)
            
            # 寫入表格表頭
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(90, 8, "Item Description", border=1, fill=True)
            pdf.cell(30, 8, "Unit Price", border=1, fill=True, align='C')
            pdf.cell(30, 8, "Qty", border=1, fill=True, align='C')
            pdf.cell(40, 8, "Total (RM)", border=1, fill=True, align='C')
            pdf.ln()
            
            # 寫入表格內容
            pdf.set_font("Helvetica", size=10)
            for item in st.session_state.items:
                pdf.cell(90, 8, str(item["品項"]), border=1)
                pdf.cell(30, 8, f"{item['單價 (RM)']:.2f}", border=1, align='C')
                pdf.cell(30, 8, str(item["數量"]), border=1, align='C')
                pdf.cell(40, 8, f"{item['總額 (RM)']:.2f}", border=1, align='C')
                pdf.ln()
                
            # 寫入總計
            pdf.ln(5)
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(150, 8, "TOTAL AMOUNT DUE:", align='R')
            pdf.cell(40, 8, f"RM {subtotal:.2f}", border=1, align='C')
            
            # 導出 PDF 數據流
            pdf_output = pdf.output(dest='S')
            
            st.download_button(
                label="📥 點擊下載 PDF 檔案",
                data=bytes(pdf_output),
                file_name=f"{invoice_no}_{customer_name}.pdf",
                mime="application/pdf"
            )
    else:
        st.info("💡 暫無商品明細。請在左側選擇商品並點擊『新增至清單』。")
