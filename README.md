# 🚀 RAG Chatbot vPro System

Hệ thống Chatbot RAG (Retrieval-Augmented Generation) chuyên nghiệp, tối ưu hóa cho Windows, tích hợp đa kênh (Web Hub & Telegram) với giao diện quản trị Admin Premium.

## ✨ Tính năng nổi bật
- **🧠 Bộ não vPro (Strict RAG)**: Sử dụng engine BM25 siêu nhẹ, tìm kiếm tài liệu chính xác. AI được cấu hình nghiêm ngặt: **Chỉ trả lời dựa trên tài liệu, tuyệt đối không bịa đặt thông tin**. Nếu không có trong tài liệu, bot sẽ báo không biết.
- **💬 Hội thoại có bộ nhớ**: Bot nhớ được ngữ cảnh cuộc trò chuyện (Chat Memory) thông qua hệ thống cơ sở dữ liệu nội bộ.
- **🛡️ Admin Premium xịn xò**: 
  - Giao diện quản trị Dark Mode hiện đại.
  - Hỗ trợ **Kéo & Thả (Drag & Drop)** tải lên file với tính năng File Preview chuyên nghiệp.
  - Tích hợp xem trực tiếp hệ thống Logs (nhật ký) theo thời gian thực để dễ dàng debug.
- **🤖 Đa kênh**: Chat trực tiếp trên Web Hub hoặc thông qua Telegram Bot.
- **📂 Đa dạng Dữ liệu**: Hỗ trợ PDF, DOCX, XLSX, CSV, JPG, PNG, TXT, MD. Tải lên và Re-index dữ liệu chỉ với 1 cú click.

## 🔒 Vấn đề Bảo mật Dữ liệu
- **Dữ liệu được lưu ở đâu?** Toàn bộ file gốc của bạn (Excel, PDF...) và database tìm kiếm (BM25 Index) được lưu **hoàn toàn cục bộ trên máy tính/máy chủ của bạn**.
- **Dữ liệu gửi đi API (OpenRouter)**: Khi chat, hệ thống chỉ trích xuất **một vài đoạn văn bản nhỏ** có liên quan nhất đến câu hỏi để gửi sang API nhằm mục đích tạo câu trả lời mạch lạc. Hệ thống **KHÔNG** upload toàn bộ file của bạn lên mạng.
- *Lưu ý:* Để bảo mật 100% đối với các dữ liệu tuyệt mật, bạn có thể dễ dàng đổi cấu hình `base_url` để kết nối với các Local LLM (như Ollama) thay vì dùng OpenRouter.

## 🛠️ Yêu cầu hệ thống
- Python 3.10 trở lên (Đã test tốt trên 3.14)
- OpenRouter API Key (Khuyên dùng `google/gemma-2-9b-it:free` hoặc `anthropic/claude-3-haiku`)
- Telegram Bot Token (Tạo từ @BotFather)
- (Tùy chọn) Cài đặt Tesseract OCR nếu muốn AI đọc văn bản trong file ảnh (JPG/PNG).

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
1. Truy cập trang **Admin**, đăng nhập bằng tài khoản được cấu hình trong `.env`.
2. Trải nghiệm giao diện **Kéo & Thả** để tải tài liệu của bạn lên hệ thống.
3. Nhấn **"🔄 Bắt đầu Re-index dữ liệu"** để bot học và lập chỉ mục kiến thức mới.
4. Bắt đầu chat trên Web hoặc Telegram và trải nghiệm bot RAG trả lời chính xác dựa trên tài liệu!

---
Thiết kế bởi **Antigravity AI** với tình yêu dành cho cộng đồng vPro.
