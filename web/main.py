from flask import Flask, render_template, Response
from utils.VideoCamera import VideoCamera

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


def generate(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route("/kameradan_goruntu_al")
def kameradan_goruntu_al():
    #return Response(b"test", mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.get("/stats")
def stats():
    return {"happy":0.78, "neutral":0.22 }

if __name__ == '__main__':
    app.run(debug=False)
