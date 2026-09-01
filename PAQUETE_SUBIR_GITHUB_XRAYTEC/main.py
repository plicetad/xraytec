# Servidor Backend HTTP Python ultra-robusto para Render, Telegram Stars y Keep-Alive Ping 24/7
import os
import sys
import urllib.request
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# EL TOKEN SE LEE EXCLUSIVAMENTE DE LAS VARIABLES DE ENTORNO EN RENDER (CERO SECRETOS EN GITHUB)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

class TelegramStarsBackendHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))
        sys.stdout.flush()

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_HEAD(self):
        # Soporte para verificadores de estado HEAD (UptimeRobot, Cron-Job)
        self._set_headers(200)

    def do_GET(self):
        url_path = self.path.split('?')[0].rstrip('/')

        # 1. ENDPOINTS DEDICADOS DE DESPERTADOR / KEEP-ALIVE PING 24/7
        if url_path in ['', '/ping', '/health', '/keep-alive', '/status']:
            self._set_headers(200)
            res = {
                "status": "online",
                "service": "XrayTec Render Backend",
                "ping": "pong",
                "message": "Servidor despierto y respondiendo 24/7",
                "timestamp": int(time.time())
            }
            self.wfile.write(json.dumps(res).encode('utf-8'))
            return

        # 2. GENERACIÓN DE FACTURA TELEGRAM STARS (25 ESTRELLAS)
        elif url_path.endswith('/generar-factura') or url_path == '/api/generar-factura':
            try:
                # Obtener token activo del entorno o usar clave de fallback segura
                token_activo = os.environ.get("BOT_TOKEN", "")
                url = f"https://api.telegram.org/bot{token_activo}/createInvoiceLink"
                payload = {
                    "title": "Compendio Radiológico XrayTec PRO",
                    "description": "Guía Clínica Completa en PDF con 25 proyecciones radiológicas, tablas de parámetros base, Fórmula de Sante y Módulo DFI",
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
                        print(f"[OK] Factura Telegram Stars generada exitosamente: {invoice_link}")
                        sys.stdout.flush()
                    else:
                        self._set_headers(500)
                        self.wfile.write(json.dumps({"error": "Fallo al crear factura", "detail": res_data}).encode('utf-8'))
                        sys.stdout.flush()

            except Exception as e:
                print(f"[ERROR] Excepción en backend: {e}")
                sys.stdout.flush()
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": "Fallo de comunicación con Telegram", "message": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Ruta no encontrada"}).encode('utf-8'))

def run_backend_server():
    port_env = os.environ.get('PORT', '8080')
    try:
        port = int(port_env)
    except ValueError:
        port = 8080
        
    print(f"[STARTUP] Iniciando servidor backend HTTP en 0.0.0.0:{port}...")
    sys.stdout.flush()
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, TelegramStarsBackendHandler)
    print(f"[OK] Servidor Backend de Telegram Stars ESCUCHANDO activamente en el puerto {port}")
    sys.stdout.flush()
    httpd.serve_forever()

if __name__ == "__main__":
    run_backend_server()
