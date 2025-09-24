#!/usr/bin/env python3
"""
Простой тестовый веб-сервер
"""

import http.server
import socketserver
import webbrowser
import threading
import time

PORT = 8080

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Crypto Portfolio Manager - Тест</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: white; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
                    .status { background: #2d3748; padding: 20px; border-radius: 10px; margin: 20px 0; }
                    .success { color: #48bb78; }
                    .info { color: #4299e1; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Crypto Portfolio Manager</h1>
                        <p>Тестовый сервер работает!</p>
                    </div>
                    
                    <div class="status">
                        <h2>✅ Статус системы</h2>
                        <p class="success">Python работает корректно</p>
                        <p class="success">Веб-сервер запущен на порту 8080</p>
                        <p class="info">Время запуска: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """</p>
                    </div>
                    
                    <div class="status">
                        <h2>🔧 Следующие шаги</h2>
                        <p>1. Если вы видите эту страницу, значит Python и веб-сервер работают</p>
                        <p>2. Теперь можно запустить основное приложение</p>
                        <p>3. Используйте команду: <code>python app/main.py</code></p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

def open_browser():
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

def main():
    print(f"🚀 Запуск тестового сервера на порту {PORT}...")
    
    with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
        print(f"✅ Сервер запущен: http://localhost:{PORT}")
        print("⏹️  Для остановки нажмите Ctrl+C")
        
        # Открываем браузер в отдельном потоке
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Сервер остановлен")

if __name__ == "__main__":
    main()
