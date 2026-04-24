# Project Context: RAG Chatbot System

Tài liệu này cung cấp ngữ cảnh kỹ thuật và kiến trúc của dự án cho các AI Assistant khác hoặc để tham khảo sau này.

## 1. Tổng quan dự án
Một hệ thống chatbot RAG (Retrieval-Augmented Generation) hoàn chỉnh, miễn phí, chạy trên nền tảng Python. Hệ thống cho phép người dùng hỏi đáp dựa trên dữ liệu tài liệu cá nhân thông qua Telegram hoặc API.

## 2. Công nghệ chính (Tech Stack)
- **Backend**: FastAPI (REST API).
- **Admin UI**: Streamlit (Quản lý tài liệu & cấu hình).
- **Bot**: Aiogram (Telegram Bot).
- **RAG Framework**: LangChain.
- **Vector Database**: ChromaDB (Lưu trữ local tại `./chroma_db`).
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (Chạy local, miễn phí).
- **LLM API**: OpenRouter (Ưu tiên các model `:free`).

## 3. Cấu trúc thư mục & Vai trò
```text
/
├── data/               # Chứa tài liệu gốc (PDF, TXT, MD)
├── chroma_db/          # Cơ sở dữ liệu Vector (sau khi index)
├── src/
│   ├── core/
│   │   └── rag_engine.py # Logic cốt lõi: Load data, Chunking, Query
│   ├── api/
│   │   └── server.py     # FastAPI Server (Port 8000)
│   ├── bot/
│   │   └── telegram_bot.py # Telegram Bot handler
│   └── admin/
│       └── app.py        # Giao diện Streamlit (Port 8501)
├── run.py              # Script khởi chạy đồng thời cả 3 thành phần
├── requirements.txt    # Thư viện phụ thuộc
└── .env                # Biến môi trường (API Keys, Config)
```

## 4. Luồng hoạt động (Data Flow)
1. **Ingestion**: Admin upload file qua Streamlit -> Lưu vào `data/` -> Gọi `rag_engine.ingest_data()` -> Chia nhỏ văn bản -> Tạo vector embedding -> Lưu vào `chroma_db/`.
2. **Query**:
   - Người dùng gửi tin nhắn (Telegram hoặc API).
   - Hệ thống tìm kiếm 3 đoạn văn bản liên quan nhất từ `chroma_db/`.
   - Gửi Context + Câu hỏi tới OpenRouter LLM.
   - Trả kết quả về cho người dùng.

## 5. Lưu ý cho AI Assistant khác
- **Mở rộng Model**: Có thể thay đổi `DEFAULT_MODEL` trong `.env`. Hệ thống được thiết kế để tương thích với mọi model hỗ trợ OpenAI API định dạng (qua OpenRouter).
- **Xử lý file**: Hiện hỗ trợ PDF, TXT, MD. Nếu muốn thêm định dạng khác, cần bổ sung Loader trong `src/core/rag_engine.py`.
- **Database**: Đang dùng local ChromaDB. Nếu muốn scale lên cloud, có thể thay bằng Pinecone hoặc MongoDB Atlas Vector Search.
- **Port**: 
  - API: 8000
  - Admin UI: 8501

## 6. Trạng thái hiện tại
Dự án đã hoàn thành khung cơ bản và có thể chạy được ngay sau khi cấu hình API Key.
