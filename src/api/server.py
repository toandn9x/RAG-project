from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from src.core.rag_engine import rag_engine
from src.api.admin_ui import get_admin_layout
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
            .typing-indicator { display: flex; gap: 5px; align-items: center; justify-content: center; height: 15px; }
            .typing-indicator span { width: 8px; height: 8px; background-color: var(--text-muted); border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; }
            .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
            .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes typing { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
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
                const btn = document.querySelector('.input-area button');
                const chatWindow = document.getElementById('chat-window');
                const message = input.value.trim();
                
                if (!message) return;
                
                chatWindow.insertAdjacentHTML('beforeend', `<div class="msg user">${message}</div>`);
                input.value = '';
                
                input.disabled = true;
                btn.disabled = true;
                
                const loadingId = 'loading-' + Date.now();
                chatWindow.insertAdjacentHTML('beforeend', `
                    <div id="${loadingId}" class="msg bot" style="padding: 12px 20px; width: fit-content; min-width: 60px;">
                        <div class="typing-indicator"><span></span><span></span><span></span></div>
                    </div>`);
                
                chatWindow.scrollTop = chatWindow.scrollHeight;
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });
                    const data = await response.json();
                    
                    const loadingElement = document.getElementById(loadingId);
                    if (loadingElement) loadingElement.remove();
                    
                    chatWindow.insertAdjacentHTML('beforeend', `<div class="msg bot">${data.answer}</div>`);
                } catch (error) {
                    const loadingElement = document.getElementById(loadingId);
                    if (loadingElement) loadingElement.remove();
                    chatWindow.insertAdjacentHTML('beforeend', `<div class="msg bot" style="color:#ef4444;">Lỗi kết nối tới server.</div>`);
                }
                
                input.disabled = false;
                btn.disabled = false;
                input.focus();
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
            document.getElementById('user-input').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
        </script>
    </body>
    </html>
    """


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, error: str = None):
    error_html = '<p style="color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 20px;">❌ Sai tài khoản hoặc mật khẩu!</p>' if error else ''
    return f'''
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
    '''

@app.get("/admin", response_class=HTMLResponse)
async def admin_files(request: Request):
    if not is_authenticated(request): return RedirectResponse(url="/admin/login", status_code=303)
    
    data_dir = os.getenv("DATA_DIR", "./data")
    files = os.listdir(data_dir) if os.path.exists(data_dir) else []
    files_html = "".join([f"<li><span>📄 {f}</span><a href='/delete-file?name={f}' class='btn btn-danger'>Xóa</a></li>" for f in files])
    
    content = f'''
        <div class="card">
            <h3>📤 Tải lên tài liệu mới</h3>
            <form id="upload-form" action="/upload" method="post" enctype="multipart/form-data">
                <div class="upload-container">
                    <div id="drop-zone" class="drop-zone">
                        <span class="icon">✨</span>
                        <p>Kéo thả file vào đây hoặc <b style="color:var(--primary)">click để chọn</b></p>
                        <input type="file" name="files" id="file-input" multiple hidden>
                    </div>
                    <div id="file-preview" class="file-preview"></div>
                </div>
                <p style="color: #94a3b8; font-size: 0.85rem; margin: 15px 0;">Hỗ trợ: PDF, DOCX, XLSX, CSV, Ảnh, TXT, MD</p>
                <button type="submit" id="upload-btn" class="btn btn-primary" style="width: 100%; display: none;">Tải lên ngay</button>
            </form>
        </div>

        <div class="card">
            <h3>📚 Thư viện tài liệu ({len(files)})</h3>
            <ul class="file-list">{files_html or "<li>Chưa có tài liệu nào.</li>"}</ul>
        </div>
        
        <div class="card" style="border-color: #10b981;">
            <h3>🧠 Cập nhật kiến thức</h3>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px;">Nhấn nút dưới đây để bot học lại toàn bộ dữ liệu mới nhất.</p>
            <form action="/reindex" method="post">
                <button type="submit" class="btn btn-success" style="width:100%">🔄 Bắt đầu Re-index dữ liệu</button>
            </form>
        </div>
        
        <script>
            // Drag and Drop Logic
            const dropZone = document.getElementById('drop-zone');
            const fileInput = document.getElementById('file-input');
            const filePreview = document.getElementById('file-preview');
            const uploadBtn = document.getElementById('upload-btn');

            dropZone.addEventListener('click', () => fileInput.click());

            dropZone.addEventListener('dragover', (e) => {{
                e.preventDefault();
                dropZone.classList.add('drag-over');
            }});

            ['dragleave', 'dragend'].forEach(type => {{
                dropZone.addEventListener(type, () => {{
                    dropZone.classList.remove('drag-over');
                }});
            }});

            dropZone.addEventListener('drop', (e) => {{
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                if (e.dataTransfer.files.length) {{
                    fileInput.files = e.dataTransfer.files;
                    updatePreview();
                }}
            }});

            fileInput.addEventListener('change', updatePreview);

            function updatePreview() {{
                filePreview.innerHTML = '';
                if (fileInput.files.length > 0) {{
                    Array.from(fileInput.files).forEach(file => {{
                        const chip = document.createElement('div');
                        chip.className = 'file-chip';
                        chip.innerHTML = `<span>📄 ${{file.name}}</span>`;
                        filePreview.appendChild(chip);
                    }});
                    uploadBtn.style.display = 'flex';
                }} else {{
                    uploadBtn.style.display = 'none';
                }}
            }}
        </script>
    '''
    return get_admin_layout("Quản lý File & Dữ liệu", content, "files")

@app.get("/admin/config", response_class=HTMLResponse)
async def admin_config(request: Request):
    if not is_authenticated(request): return RedirectResponse(url="/admin/login", status_code=303)
    
    content = f'''
    <div class="card" style="border-color: #8b5cf6;">
        <h3>🤖 Cấu hình Model AI</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 20px; line-height: 1.5;">Nhập tên Model trên OpenRouter (VD: google/gemma-2-9b-it:free, anthropic/claude-3-haiku, ...). Việc cập nhật sẽ được áp dụng ngay lập tức mà không cần khởi động lại.</p>
        <form action="/update-model" method="post" style="display: flex; gap: 15px;">
            <input type="text" class="form-control" name="model_name" value="{rag_engine.model_name}" required>
            <button type="submit" class="btn btn-primary" style="background: #8b5cf6; border-color: #8b5cf6; white-space: nowrap;">💾 Lưu Model</button>
        </form>
    </div>
    '''
    return get_admin_layout("Cấu hình Model AI", content, "config")

@app.get("/admin/logs", response_class=HTMLResponse)
async def admin_logs(request: Request):
    if not is_authenticated(request): return RedirectResponse(url="/admin/login", status_code=303)
    
    content = '''
    <div class="card" id="logs-section">
        <h3>📜 Nhật ký hệ thống (Live Logs)</h3>
        <div id="log-content" style="background: #0f172a; color: #10b981; padding: 20px; border-radius: 12px; height: 500px; overflow-y: auto; font-family: monospace; font-size: 0.9rem; border: 1px solid #334155; line-height: 1.5;">
            Đang tải nhật ký...
        </div>
        <button onclick="fetchLogs()" class="btn btn-primary" style="margin-top:20px; width:100%">🔄 Làm mới Log</button>
    </div>
    <script>
        async function fetchLogs() {
            const response = await fetch('/api/logs');
            const text = await response.text();
            const logDiv = document.getElementById('log-content');
            logDiv.innerText = text;
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        fetchLogs();
        setInterval(fetchLogs, 5000); // Tự động cập nhật mỗi 5 giây
    </script>
    '''
    return get_admin_layout("Nhật ký hệ thống", content, "logs")


# --- API ACTIONS ---

@app.get("/api/logs")
async def get_logs(request: Request):
    if not is_authenticated(request): return Response("Unauthorized", status_code=401)
    if os.path.exists("app.log"):
        with open("app.log", "r", encoding="utf-8") as f:
            # Lấy 100 dòng cuối cùng
            lines = f.readlines()
            return "".join(lines[-100:])
    return "Chưa có dữ liệu nhật ký."

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_session", value="authenticated")
        return response
    return RedirectResponse(url="/admin/login?error=1", status_code=303)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response

@app.post("/upload")
async def upload_files(request: Request, files: list[UploadFile] = File(...)):
    if not is_authenticated(request): return RedirectResponse(url="/admin", status_code=303)
    data_dir = os.getenv("DATA_DIR", "./data")
    try:
        os.makedirs(data_dir, exist_ok=True)
        for file in files:
            if not file.filename:
                continue
            file_path = os.path.join(data_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        return RedirectResponse(url="/admin", status_code=303)
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return HTMLResponse(f"<h2>Loi khi upload: {str(e)}</h2><a href='/admin'>Quay lai</a>")

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

@app.post("/update-model")
async def update_model(request: Request, model_name: str = Form(...)):
    if not is_authenticated(request): return RedirectResponse(url="/admin/login", status_code=303)
    
    rag_engine.model_name = model_name
    
    try:
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                model_updated = False
                for line in lines:
                    if line.startswith("DEFAULT_MODEL="):
                        f.write(f"DEFAULT_MODEL={model_name}\n")
                        model_updated = True
                    else:
                        f.write(line)
                
                if not model_updated:
                    f.write(f"\nDEFAULT_MODEL={model_name}\n")
    except Exception as e:
        print(f"Could not update .env: {e}")
        
    return RedirectResponse(url="/admin/config", status_code=303)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        answer = rag_engine.query(request.message, session_id=request.session_id)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
