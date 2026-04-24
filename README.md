# 🚀 RAG Chatbot vPro System

Hệ thống Chatbot RAG (Retrieval-Augmented Generation) chuyên nghiệp, tối ưu hóa cho Windows, tích hợp đa kênh (Web Hub & Telegram) với giao diện quản trị Admin Premium.

## ✨ Tính năng nổi bật
- **🧠 Bộ não vPro**: Sử dụng engine BM25 siêu nhẹ, tìm kiếm tài liệu chính xác mà không cần GPU hay thư viện nặng.
- **💬 Hội thoại có bộ nhớ**: Bot nhớ được ngữ cảnh cuộc trò chuyện (Chat Memory) thông qua SQLite.
- **🛡️ Admin Premium**: Giao diện quản trị Dark Mode hiện đại, tích hợp ngay trên cổng 8000 với hệ thống đăng nhập bảo mật.
- **🤖 Đa kênh**: Chat trực tiếp trên Web Hub hoặc thông qua Telegram Bot.
- **📂 Quản lý dữ liệu**: Hỗ trợ PDF, DOCX, XLSX, CSV, JPG, PNG, TXT, MD. Tải lên và Re-index dữ liệu chỉ với 1 cú click.
- **⚡ Tối ưu Windows**: Không lỗi DLL, khởi động cực nhanh với Python 3.14.

## 🛠️ Yêu cầu hệ thống
- Python 3.10 trở lên (Đã test tốt trên 3.14)
- OpenRouter API Key (Dùng các model miễn phí)
- Telegram Bot Token (Tạo từ @BotFather)
- (Tùy chọn) Cài đặt Tesseract OCR nếu muốn đọc file ảnh tốt hơn.

## 📦 Cài đặt

1. **Clone dự án:**
   ```bash
   git clone <link-repo-cua-ban>
   cd <ten-thu-muc>
   ```

2. **Cài đặt thư viện:**
   ```bash
   pip install fastapi uvicorn openai python-dotenv rank_bm25 pypdf aiogram python-multipart docx2txt pandas openpyxl pytesseract Pillow
   ```

3. **Cấu hình môi trường:**
   - Copy file `.env.example` thành `.env`
   - Điền các thông số API Key và Token của bạn vào file `.env`

## 🚀 Khởi chạy

Chạy lệnh duy nhất để khởi động toàn bộ hệ thống (API, Web UI, Bot):
```bash
python run.py
```

## 📍 Địa chỉ truy cập
- **Chat Hub (Dành cho người dùng):** `http://localhost:8000`
- **Admin Panel (Quản trị viên):** `http://localhost:8000/admin`
- **API Documentation (Swagger):** `http://localhost:8000/docs`

## 📘 Hướng dẫn sử dụng
1. Truy cập trang **Admin**, đăng nhập bằng tài khoản trong `.env`.
2. Tải tài liệu của bạn lên thư mục dữ liệu.
3. Nhấn **"🔄 Bắt đầu Re-index dữ liệu"** để bot học kiến thức mới.
4. Bắt đầu chat trên Web hoặc Telegram!

---
Thiết kế bởi **Antigravity AI** với tình yêu dành cho cộng đồng vPro.
