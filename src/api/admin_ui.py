def get_admin_layout(title: str, content: str, active_menu: str = "files"):
    menu_items = [
        {"id": "files", "url": "/admin", "icon": "📁", "label": "Quản lý File & Dữ liệu"},
        {"id": "config", "url": "/admin/config", "icon": "🤖", "label": "Cấu hình Model AI"},
        {"id": "logs", "url": "/admin/logs", "icon": "📜", "label": "Nhật ký hệ thống"},
    ]
    
    nav_html = '<a href="/" style="display:flex; align-items:center; gap:10px; color: white; margin-bottom: 25px; text-decoration: none; padding: 10px; border-radius: 8px; transition: 0.3s;" onmouseover="this.style.background=\'#334155\'" onmouseout="this.style.background=\'transparent\'">🏠 Quay lại Chat</a>'
    
    for item in menu_items:
        is_active = item["id"] == active_menu
        color = "#6366f1" if is_active else "#94a3b8"
        bg = "rgba(99, 102, 241, 0.1)" if is_active else "transparent"
        weight = "600" if is_active else "400"
        
        nav_html += f"""
        <a href="{item['url']}" style="display:flex; align-items:center; gap:10px; color: {color}; background: {bg}; margin-bottom: 10px; padding: 12px 15px; text-decoration: none; font-weight: {weight}; border-radius: 10px; transition: 0.3s;" onmouseover="if('{item['id']}' !== '{active_menu}') this.style.background='rgba(255,255,255,0.05)'" onmouseout="if('{item['id']}' !== '{active_menu}') this.style.background='transparent'">
            <span style="font-size: 1.2rem;">{item['icon']}</span> {item['label']}
        </a>
        """
        
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>{title} - Admin vPro</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {{ --primary: #6366f1; --bg: #0f172a; --card-bg: #1e293b; --text: #f8fafc; --text-muted: #94a3b8; }}
            body {{ font-family: 'Outfit', sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; height: 100vh; overflow: hidden; }}
            .sidebar {{ width: 280px; background: var(--card-bg); padding: 25px; border-right: 1px solid #334155; display: flex; flex-direction: column; }}
            .sidebar h2 {{ margin-top: 0; margin-bottom: 30px; font-weight: 600; font-size: 1.5rem; display: flex; align-items: center; gap: 10px; }}
            .sidebar nav {{ flex: 1; }}
            .logout {{ color: #ef4444; text-decoration: none; font-weight: 600; padding: 12px; border-radius: 10px; display: flex; align-items: center; gap: 10px; transition: 0.3s; }}
            .logout:hover {{ background: rgba(239, 68, 68, 0.1); }}
            
            .content-wrapper {{ flex: 1; overflow-y: auto; padding: 40px; background: radial-gradient(circle at top right, #1e1b4b, var(--bg)); }}
            .header-title {{ font-size: 2rem; font-weight: 600; margin-bottom: 30px; border-bottom: 1px solid #334155; padding-bottom: 15px; display: flex; align-items: center; gap: 15px; }}
            
            .card {{ background: var(--card-bg); padding: 30px; border-radius: 16px; border: 1px solid #334155; margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
            .card h3 {{ margin-top: 0; display: flex; align-items: center; gap: 10px; font-size: 1.25rem; margin-bottom: 20px; }}
            
            .btn {{ padding: 10px 20px; border-radius: 8px; border: none; font-weight: 600; cursor: pointer; transition: 0.3s; color: white; display: inline-flex; align-items: center; justify-content: center; gap: 8px; font-family: 'Outfit', sans-serif; font-size: 0.95rem; text-decoration: none; box-sizing: border-box; }}
            .btn-primary {{ background: var(--primary); }}
            .btn-primary:hover {{ background: #4f46e5; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); }}
            .btn-success {{ background: #10b981; }}
            .btn-success:hover {{ background: #059669; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }}
            .btn-danger {{ background: #ef4444; color: white; padding: 6px 12px; font-size: 0.85rem; border-radius: 6px; }}
            .btn-danger:hover {{ background: #dc2626; }}
            
            /* File List */
            .file-list {{ list-style: none; padding: 0; margin: 0; }}
            .file-list li {{ display: flex; justify-content: space-between; align-items: center; padding: 15px; background: rgba(15, 23, 42, 0.4); border-radius: 10px; margin-bottom: 10px; border: 1px solid #334155; transition: 0.2s; }}
            .file-list li:hover {{ background: rgba(255,255,255,0.05); }}
            
            /* Drag Drop */
            .drop-zone {{ border: 2px dashed #475569; padding: 40px; text-align: center; border-radius: 12px; background: rgba(15, 23, 42, 0.5); cursor: pointer; transition: 0.3s; margin-bottom: 20px; }}
            .drop-zone:hover, .drop-zone.drag-over {{ border-color: var(--primary); background: rgba(99, 102, 241, 0.05); transform: translateY(-2px); }}
            .drop-zone .icon {{ font-size: 3rem; margin-bottom: 15px; display: block; }}
            
            .file-preview {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; max-height: 200px; overflow-y: auto; }}
            .file-chip {{ background: #0f172a; padding: 8px 12px; border-radius: 8px; font-size: 0.85rem; display: flex; align-items: center; gap: 8px; border: 1px solid #334155; }}
            .file-chip span {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h2><span style="color: var(--primary);">⚡</span> vPro Admin</h2>
            <nav>{nav_html}</nav>
            <a href="/logout" class="logout">🚪 Đăng xuất</a>
        </div>
        <div class="content-wrapper">
            <h1 class="header-title">{title}</h1>
            {content}
        </div>
    </body>
    </html>
    """
