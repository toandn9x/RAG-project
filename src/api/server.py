from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from src.core.rag_engine import rag_engine
import uvicorn
import os
import shutil

app = FastAPI(title="RAG Chatbot vPro System")

# --- AUTH LOGIC ---
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

def is_authenticated(request: Request):
    return request.cookies.get("admin_session") == "authenticated"

class ChatRequest(BaseModel):
    message: str
    session_id: str = "web_default"

class ChatResponse(BaseModel):
    answer: str

# --- WEB UI ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8"><title>RAG Chatbot Hub</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root { --primary: #6366f1; --primary-hover: #4f46e5; --bg: #0f172a; --card-bg: #1e293b; --text: #f8fafc; --text-muted: #94a3b8; }
            body { font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
            header { background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid #334155; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; z-index: 100; }
            .nav-links a { margin-left: 1.5rem; text-decoration: none; color: var(--text-muted); font-weight: 500; transition: 0.3s; }
            .nav-links a:hover { color: var(--primary); }
            main { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; background: radial-gradient(circle at top right, #1e1b4b, var(--bg)); }
            .chat-container { width: 100%; max-width: 800px; background: var(--card-bg); border-radius: 20px; border: 1px solid #334155; display: flex; flex-direction: column; height: 70vh; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); }
            #chat-window { flex: 1; overflow-y: auto; padding: 2rem; scrollbar-width: thin; }
            .input-area { padding: 1.5rem; display: flex; gap: 1rem; border-top: 1px solid #334155; }
            input { flex: 1; padding: 1rem; background: #0f172a; border: 1px solid #334155; border-radius: 12px; color: white; outline: none; transition: 0.3s; }
            input:focus { border-color: var(--primary); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2); }
            button { background: var(--primary); color: white; border: none; padding: 0 2rem; border-radius: 12px; cursor: pointer; font-weight: 600; transition: 0.3s; }
            button:hover { background: var(--primary-hover); transform: translateY(-1px); }
            .msg { margin-bottom: 1.5rem; padding: 1rem 1.25rem; border-radius: 15px; max-width: 80%; line-height: 1.6; animation: fadeIn 0.3s ease; }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            .user { align-self: flex-end; background: var(--primary); color: white; margin-left: auto; border-bottom-right-radius: 2px; }
            .bot { align-self: flex-start; background: #334155; border-bottom-left-radius: 2px; }
        </style>
    </head>
    <body>
        <header>
            <h2 style="margin:0; background: linear-gradient(to right, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">RAG vPro Hub</h2>
            <div class="nav-links"><a href="/docs">API Docs</a><a href="/admin">⚙️ Quản trị</a></div>
        </header>
        <main>
            <div class="chat-container">
                <div id="chat-window"><div class="msg bot">Chào bạn! Tôi là trợ lý AI vPro. Tôi đã sẵn sàng hỗ trợ bạn với kiến thức từ tài liệu.</div></div>
                <div class="input-area">
                    <input type="text" id="user-input" placeholder="Nhập câu hỏi của bạn...">
                    <button onclick="sendMessage()">Gửi</button>
                </div>
            </div>
        </main>
        <script>
            async function sendMessage() {
                const input = document.getElementById('user-input');
                const chatWindow = document.getElementById('chat-window');
                const message = input.value.trim();
                if (!message) return;
                chatWindow.innerHTML += `<div class="msg user">${message}</div>`;
                input.value = '';
                chatWindow.scrollTop = chatWindow.scrollHeight;
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                chatWindow.innerHTML += `<div class="msg bot">${data.answer}</div>`;
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
            document.getElementById('user-input').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
        </script>
    </body>
    </html>
    """

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, error: str = None):
    if not is_authenticated(request):
        error_html = '<p style="color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 20px;">❌ Sai tài khoản hoặc mật khẩu!</p>' if error else ''
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - Admin vPro</title>
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Outfit', sans-serif; background: #0f172a; display: flex; align-items: center; justify-content: center; height: 100vh; margin:0; }}
                .login-card {{ background: #1e293b; padding: 40px; border-radius: 20px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); width: 350px; text-align: center; border: 1px solid #334155; }}
                h2 {{ color: white; margin-bottom: 30px; }}
                input {{ width: 100%; padding: 12px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; outline: none; }}
                input:focus {{ border-color: #6366f1; }}
                button {{ width: 100%; padding: 12px; background: #6366f1; border: none; color: white; font-weight: 600; border-radius: 8px; cursor: pointer; transition: 0.3s; }}
                button:hover {{ background: #4f46e5; }}
            </style>
        </head>
        <body>
            <div class="login-card">
                <h2>🔒 Admin Login</h2>
                {error_html}
                <form action="/login" method="post">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Đăng nhập</button>
                </form>
            </div>
        </body>
        </html>
        """
    # ... rest of the admin page logic (already handled)

    data_dir = os.getenv("DATA_DIR", "./data")
    files = os.listdir(data_dir) if os.path.exists(data_dir) else []
    files_html = "".join([f"<li><span>📄 {f}</span><a href='/delete-file?name={f}' style='color:#ef4444; font-weight:600; text-decoration:none;'>Xóa</a></li>" for f in files])

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Panel - RAG vPro</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Outfit', sans-serif; background: #0f172a; color: #f8fafc; margin: 0; display: flex; }}
            .sidebar {{ width: 280px; background: #1e293b; height: 100vh; padding: 30px; box-sizing: border-box; border-right: 1px solid #334155; }}
            .content {{ flex: 1; padding: 40px; overflow-y: auto; }}
            .card {{ background: #1e293b; padding: 30px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 30px; }}
            h1, h3 {{ margin-top: 0; }}
            .btn {{ padding: 12px 24px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; text-decoration: none; transition: 0.3s; }}
            .btn-primary {{ background: #6366f1; color: white; }}
            .btn-danger {{ background: #ef4444; color: white; }}
            .btn-success {{ background: #10b981; color: white; width: 100%; font-size: 1.1rem; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ padding: 15px; background: #0f172a; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }}
            .logout {{ margin-top: 50px; display: block; color: #94a3b8; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2 style="color: #6366f1">vPro Admin</h2>
            <nav>
                <a href="/" style="display:block; color: white; margin-bottom: 20px; text-decoration: none;">🏠 Quay lại Chat</a>
                <a href="/admin" style="display:block; color: #6366f1; margin-bottom: 20px; text-decoration: none; font-weight: 600;">📁 Quản lý File</a>
                <a href="/docs" style="display:block; color: white; margin-bottom: 20px; text-decoration: none;">📄 API Docs</a>
            </nav>
            <a href="/logout" class="logout">🚪 Đăng xuất</a>
        </div>
        <div class="content">
            <h1>⚙️ Hệ thống Quản trị vPro</h1>
            
            <div class="card">
                <h3>📤 Tải lên tài liệu mới</h3>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="files" multiple style="margin-bottom: 20px; display: block;">
                    <button type="submit" class="btn btn-primary">Tải lên ngay</button>
                </form>
            </div>

            <div class="card">
                <h3>📚 Thư viện tài liệu ({len(files)})</h3>
                <ul>{files_html or "<li>Chưa có tài liệu nào.</li>"}</ul>
            </div>

            <div class="card" style="border-color: #10b981;">
                <h3>🧠 Cập nhật kiến thức</h3>
                <p style="color: #94a3b8;">Nhấn nút dưới đây để bot học lại toàn bộ dữ liệu mới nhất.</p>
                <form action="/reindex" method="post">
                    <button type="submit" class="btn btn-success">🔄 Bắt đầu Re-index dữ liệu</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# --- API ACTIONS ---

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_session", value="authenticated")
        return response
    return RedirectResponse(url="/admin?error=1", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie("admin_session")
    return response

@app.post("/upload")
async def upload_files(request: Request, files: list[UploadFile] = File(...)):
    if not is_authenticated(request): return RedirectResponse(url="/admin", status_code=303)
    data_dir = os.getenv("DATA_DIR", "./data")
    os.makedirs(data_dir, exist_ok=True)
    for file in files:
        with open(os.path.join(data_dir, file.filename), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/delete-file")
async def delete_file(request: Request, name: str):
    if not is_authenticated(request): return RedirectResponse(url="/admin", status_code=303)
    data_dir = os.getenv("DATA_DIR", "./data")
    file_path = os.path.join(data_dir, name)
    if os.path.exists(file_path): os.remove(file_path)
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/reindex")
async def reindex(request: Request):
    if not is_authenticated(request): return RedirectResponse(url="/admin", status_code=303)
    rag_engine.ingest_data()
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = rag_engine.query(request.message, session_id=request.session_id)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
