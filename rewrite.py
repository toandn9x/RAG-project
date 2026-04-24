import sys

with open('src/api/server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith('@app.get("/admin", response_class=HTMLResponse)'):
        start_idx = i
    if line.strip() == '# --- API ACTIONS ---':
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_code = """
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

"""
    
    new_lines = lines[:start_idx] + [new_code + "\n"] + lines[end_idx:]
    with open('src/api/server.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Replaced successfully.")
else:
    print("Markers not found.")
