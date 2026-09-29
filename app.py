from flask import Flask, render_template, Response
import cv2
import datetime
from ultralytics import YOLO

app = Flask(__name__)

# Cargamos el modelo de IA pre-entrenado
modelo_yolo = YOLO('yolov8n.pt')

def generar_frames(nombre_tablero):
    # Tablero A usa la cámara de la laptop (0), Tablero B usa la USB externa (1)
    if nombre_tablero == 'A':
        cam_index = 0
    elif nombre_tablero == 'B':
        cam_index = 1
    else:
        cam_index = 0
        
    camera = cv2.VideoCapture(cam_index)

    try:
        while True:
            success, frame = camera.read()
            
            if not success:
                # Si la cámara no está conectada, sale de la transmisión
                break
            else:
                # 1. Pasamos la imagen a YOLO para detectar objetos
                resultados = modelo_yolo(frame)
                
                # 2. Obtenemos el frame dibujado con los recuadros
                frame_procesado = resultados[0].plot()
                
                # 3. Dibujamos la fecha y hora
                ahora = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
                cv2.putText(frame_procesado, ahora, (10, frame_procesado.shape[0] - 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # 4. Codificamos a formato JPEG y enviamos
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
    app.run(host='0.0.0.0', port=5000, debug=True)