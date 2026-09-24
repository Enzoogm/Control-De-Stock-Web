from flask import Flask, render_template, Response
import cv2
import datetime

app = Flask(__name__)

def generar_frames(numero_aula):
    # Asignamos el índice de la cámara según el aula seleccionada
    if numero_aula == '212':
        cam_index = 0  # Cámara web integrada de la laptop
    elif numero_aula == '213':
        cam_index = 1  # Cámara web USB externa
    else:
        cam_index = 0  # Fallback por defecto
        
    camera = cv2.VideoCapture(cam_index)

    try:
        while True:
            success, frame = camera.read()
            
            if not success:
                # Si la cámara no está conectada (ej. la 1 aún no está enchufada), cortamos la transmisión
                break
            else:
                # Obtenemos la fecha y hora actual
                ahora = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
                
                # Dibujamos el texto sobre el frame
                cv2.putText(frame, ahora, (10, frame.shape[0] - 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        # Liberamos el uso de la cámara cuando cambias de página o cerrás el navegador
        camera.release()

@app.route('/')
def index():
    return render_template('lobby.html')

@app.route('/aula/<numero_aula>')
def ver_aula(numero_aula):
    return render_template('aula.html', aula=numero_aula)

# Ahora esta ruta recibe el número de aula para saber qué cámara encender
@app.route('/video_feed/<numero_aula>')
def video_feed(numero_aula):
    return Response(generar_frames(numero_aula), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)