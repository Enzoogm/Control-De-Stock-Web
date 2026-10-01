import eventlet
eventlet.monkey_patch() # Parchea el sistema para que los sockets fluyan en tiempo real

from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import datetime
from ultralytics import YOLO

app = Flask(__name__)
# Inicializamos Socket.IO permitiendo que se conecten desde otras IPs (tu celular)
socketio = SocketIO(app, cors_allowed_origins="*") 

modelo_yolo = YOLO('yolov8n.pt')

def generar_frames(nombre_tablero):
    if nombre_tablero == 'A':
        cam_index = 0
    else:
        cam_index = 1
        
    camera = cv2.VideoCapture(cam_index)

    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
                
            resultados = modelo_yolo(frame)
            frame_procesado = resultados[0].plot()
            
            # --- LA NOVEDAD: Extraer nombres y enviar al celular ---
            nombres_detectados = []
            for caja in resultados[0].boxes:
                clase_id = int(caja.cls[0])
                nombre_objeto = modelo_yolo.names[clase_id]
                nombres_detectados.append(nombre_objeto)
            
            # Removemos duplicados (si hay 3 pinzas, enviamos ["pinza"])
            nombres_unicos = list(set(nombres_detectados))
            
            # Emitimos por Socket.IO al celular (Canal: 'actualizacion_ia')
            socketio.emit('actualizacion_ia', {'objetos': nombres_unicos})
            
            # --- LA SOLUCIÓN MÁGICA ---
            # Esto pausa el ciclo 0.01 segundos para que el mensaje pueda viajar por Wi-Fi
            socketio.sleep(0.01)
            # ---------------------------------------------------------
            
            ret, buffer = cv2.imencode('.jpg', frame_procesado)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        camera.release()

@app.route('/')
def index():
    return render_template('lobby.html')

@app.route('/tablero/<nombre_tablero>')
def ver_tablero(nombre_tablero):
    return render_template('tablero.html', tablero=nombre_tablero)

@app.route('/video_feed/<nombre_tablero>')
def video_feed(nombre_tablero):
    return Response(generar_frames(nombre_tablero), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SERVIDOR IA INICIADO CORRECTAMENTE")
    print("👉 Entrar al Lobby: http://127.0.0.1:5000")
    print("👉 Ir directo al Tablero A: http://127.0.0.1:5000/tablero/A")
    print("="*50 + "\n")
    
    # Ahora usamos socketio.run en lugar de app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)