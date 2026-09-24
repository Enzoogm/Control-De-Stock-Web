from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

def generate_frames(camera_index):
    # Enciende la cámara específica
    camera = cv2.VideoCapture(camera_index)
    
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        # Esto asegura que la cámara se libere SÍ O SÍ al salir de la página
        camera.release()

@app.route('/')
def lobby():
    return render_template('lobby.html')

@app.route('/aula/<numero>')
def aula(numero):
    return render_template('aula.html', numero_aula=numero)

@app.route('/video_feed/<numero>')
def video_feed(numero):
    if numero == '212':
        camera_index = 0  
    elif numero == '213':
        camera_index = 1  
    else:
        camera_index = 0
        
    return Response(generate_frames(camera_index), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)