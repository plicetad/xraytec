# Servidor Backend HTTP Python para el Bot de Telegram (@xratecbot) en Render
# Endpoint /api/generar-factura para Telegram Stars (25 XTR)

import os
import urllib.request
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

BOT_TOKEN = "8690438142:AAEA2oJ1xeoQj7bEuWEvqno-sh0Ycrevo9M"

class TelegramStarsBackendHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        # CORS habilitado para GitHub Pages
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path.startswith('/api/generar-factura') or self.path == '/':
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink"
                payload = {
                    "title": "Compendio Radiológico XrayTec PRO",
                    "description": "Guía Clínica Completa en PDF con 25+ proyecciones ilustradas y parámetros base",
                    "payload": f"tx_xraytec_{int(time.time())}",
                    "provider_token": "",  # OBLIGATORIO VACÍO PARA TELEGRAM STARS
                    "currency": "XTR",       # OBLIGATORIO MONEDA DE TELEGRAM STARS
                    "prices": [
                        {"label": "Compendio PRO", "amount": 25} # 25 Estrellas (XTR)
                    ]
                }

                headers = {'Content-Type': 'application/json'}
                req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
                
                with urllib.request.urlopen(req) as resp:
                    res_data = json.loads(resp.read().decode('utf-8'))
                    if res_data.get("ok"):
                        invoice_link = res_data["result"]
                        self._set_headers(200)
                        self.wfile.write(json.dumps({"invoiceLink": invoice_link, "status": "active"}).encode('utf-8'))
                        print(f"[OK] Factura Telegram Stars generada: {invoice_link}")
                    else:
                        self._set_headers(500)
                        self.wfile.write(json.dumps({"error": "Fallo al crear factura", "detail": res_data}).encode('utf-8'))

            except Exception as e:
                print(f"[ERROR] Excepción en backend: {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": "Fallo de comunicación con Telegram", "message": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode('utf-8'))

def run_backend_server():
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, TelegramStarsBackendHandler)
    print(f"[OK] Servidor Backend de Telegram Stars iniciado en el puerto {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_backend_server()
