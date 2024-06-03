# -*- coding: utf-8 -*-
import sys, os, cv2, json
from utils.statics import *
from utils import helper
import numpy as np
from tensorflow.keras.models import model_from_json


print("Model yükleniyor...")
model_dir:str = f"{os.getcwd()}{os.sep}..{os.sep}model{os.sep}"
with open(model_dir + "model.json", 'r', encoding='utf-8') as f:
    model = model_from_json(f.read())
model.load_weights(model_dir + "model_weights.h5")
face_haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
print("Model yüklendi.")

class VideoCamera:
    def __init__(self, shareData):
        self.shareData = shareData
        self.video = cv2.VideoCapture(0)
        dir_images:str = f"{os.getcwd()}{os.sep}utils{os.sep}images{os.sep}" # emojilerin olduğu klasör
        for emotion in emotions_as_string:
            # Tüm emojiler yükleniyor
            setattr(self, "image_"+emotion, cv2.imread(dir_images + emotion + ".png", cv2.IMREAD_UNCHANGED))

    def __del__(self):
        '''
        RAM'den silme işlemi
        '''
        self.video.release()

    def merge_image(self, back, front, x, y):
        '''
        İki tane resmi birleştirir ve birleşim sonucunu return eder.
        '''
        if back.shape[2] == 3:
            back = cv2.cvtColor(back, cv2.COLOR_BGR2BGRA)
        if front.shape[2] == 3:
            front = cv2.cvtColor(front, cv2.COLOR_BGR2BGRA)

        bh, bw = back.shape[:2]
        fh, fw = front.shape[:2]
        x1, x2 = max(x, 0), min(x + fw, bw)
        y1, y2 = max(y, 0), min(y + fh, bh)
        front_cropped = front[y1 - y:y2 - y, x1 - x:x2 - x]
        back_cropped = back[y1:y2, x1:x2]

        alpha_front = front_cropped[:, :, 3:4] / 255
        alpha_back = back_cropped[:, :, 3:4] / 255

        result = back.copy()
        result[y1:y2, x1:x2, :3] = alpha_front * front_cropped[:, :, :3] + (1 - alpha_front) * back_cropped[:, :, :3]
        result[y1:y2, x1:x2, 3:4] = (alpha_front + alpha_back) / (1 + alpha_front * alpha_back) * 255

        return result
    def get_frame(self):
        ret, test_img = self.video.read()
        gray_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)

        font = cv2.FONT_HERSHEY_SIMPLEX

        try:
            faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)

            for (x, y, w, h) in faces_detected:
                cv2.rectangle(test_img, (x, y), (x + w, y + h), (240, 240, 240), thickness=2)
                roi_gray = gray_img[y:y + w, x:x + h]
                roi_gray = cv2.resize(roi_gray, (48, 48))
                img = roi_gray.reshape((1, 48, 48, 1))
                img = img / 255.0
                predict_result = model.predict(img.reshape((1, 48, 48, 1)))
                val_angry, val_disgust, val_fear, val_happy, val_sad, val_surprise, val_neutral = predict_result[0]
                val_angry, val_disgust, val_fear, val_happy, val_sad, val_surprise, val_neutral = float(val_angry.item()*100), float(val_disgust.item()*100), float(val_fear.item()*100), float(val_happy.item()*100), float(val_sad.item()*100), float(val_surprise.item()*100), float(val_neutral.item()*100) # .item() ile numpy float32 objesini python float a çeviriyoruz yoksa json dump olmuyor
                max_index = np.argmax(predict_result, axis=-1)[0]
                #print(f"Happy: {val_happy:.2f} - Neutral: {val_neutral:2f}")
                self.shareData.stats = {
                    "happy": {"percentage": round(val_happy, 2), "title": "Mutlu"},
                    "neutral": {"percentage": round(val_neutral, 2), "title": "Normal"},
                    "sad": {"percentage": round(val_sad, 2), "title": "Üzgün"},
                    "angry": {"percentage": round(val_angry, 2), "title": "Kızgın"},
                    "disgust": {"percentage": round(val_disgust, 2), "title": "İğrenmiş"},
                }
                #print("Model çıktısı index: ", max_index)

                enum_emotion = Emotions(max_index)

                hedef_smile = getattr(self, "image_Neutral")
                hedef_yazi = "Normal"
                if enum_emotion == Emotions.HAPPY:
                    hedef_smile = getattr(self, "image_Happy")
                    hedef_yazi = "Mutlu"
                elif enum_emotion == Emotions.SAD:
                    hedef_smile = getattr(self, "image_Sad")
                    hedef_yazi = "Uzgun"
                elif enum_emotion == Emotions.ANGRY:
                    hedef_smile = getattr(self, "image_Angry")
                    hedef_yazi = "Kizgin"
                elif enum_emotion == Emotions.DISGUST:
                    hedef_smile = getattr(self, "image_Disgust")
                    hedef_yazi = "Igrenmis"
                elif enum_emotion == Emotions.FEAR:
                    hedef_smile = getattr(self, "image_Fear")
                    hedef_yazi = "Korkmus"
                elif enum_emotion == Emotions.SURPRISE:
                    hedef_smile = getattr(self, "image_Surprise")
                    hedef_yazi = "Sasirmis"
                elif enum_emotion == Emotions.NEUTRAL:
                    hedef_smile = getattr(self, "image_Neutral")
                    hedef_yazi = "Normal"

                textsize = cv2.getTextSize(hedef_yazi, font, 1, 2)[0]
                textX = int((test_img.shape[1] - textsize[0]) / 2)
                textY = int((test_img.shape[0] + textsize[1]) / 2)
                yaziBaslangicKonumuX = int(x + (w) / 2 - (textsize[0] / 2))
                yaziBaslangicKonumuY = int(y - 10)

                emoji_x, emoji_y = yaziBaslangicKonumuX - 40, yaziBaslangicKonumuY - 30

                if hedef_smile is not None:
                    test_img = self.merge_image(test_img, hedef_smile, emoji_x, emoji_y)

                cv2.putText(test_img, hedef_yazi,
                            (yaziBaslangicKonumuX, yaziBaslangicKonumuY),#(textX, int(y)),
                            font, 1, (247, 247, 247), 2)


        except Exception as err:
            helper.hataKodGoster("VideoCamera get_frame hata: " + str(err))

        resized_img = cv2.resize(test_img, (1000, 600))
        _, jpg = cv2.imencode('.jpg', resized_img)
        return jpg.tobytes()