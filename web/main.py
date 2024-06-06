import json
from flask import Flask, render_template, Response, request

TEST = False
if not TEST:
    from utils.VideoCamera import VideoCamera

import joblib
model_text = joblib.load(open("../model/model_text.pkl", "rb"))



app = Flask(__name__)

class ShareData(object):
    stats = None
shareData = ShareData()


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
    if TEST:
        return Response(b"test", mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response(generate(VideoCamera(shareData=shareData)), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.get("/stats")
def stats():
    if TEST:
        return json.dumps({"happy": {"percentage": "83.22", "title": "Mutlu"},
                    "neutral": {"percentage": "5.66", "title": "Normal"},
                    "sad": {"percentage": "7.91", "title": "Üzgün"},
                    "angry": {"percentage": "0.33", "title": "Kızgın"},
                    "disgust": {"percentage": "1.74", "title": "İğrenmiş"}})
    return json.dumps(shareData.stats)


@app.route("/speech", methods=["POST"])
def speech():
    jsonData = request.json
    text = jsonData.get("text", "")
    result = model_text.predict([text])
    result = result[0] if len(result) > 0 else "Bilinmiyor"
    if result == "joy":
        result = "happy"
    elif result == "anger":
        result = "angry"
    elif result == "sadness":
        result = "sad"

    return {"text": text, "result": result}

if __name__ == '__main__':
    app.run(debug=False)
