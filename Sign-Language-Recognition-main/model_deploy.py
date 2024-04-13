import streamlit as st
from keras.models import load_model
import cv2
import numpy as np
import os
import mediapipe as mp
mphands = mp.solutions.hands
hand = mphands.Hands(max_num_hands=2, min_detection_confidence=0.75)
mpdraw = mp.solutions.drawing_utils
st.title("Sign Language Classification")
st.header("Gesture Model")
all_classes = os.listdir("D:/ASL")


@st.cache(hash_funcs={'tensorflow.python.keras.utils.object_identity.ObjectIdentityDictionary': id}, allow_output_mutation=True)
def model_upload():
    model = load_model("D:/gestures.h5")
    print("Loading")
    return model


def predict(model, image):
    img = np.array(image)
    img = cv2.resize(img, (100, 100))
    img = img / 255
    img = np.expand_dims(img, axis=0)
    prediction = model.predict(img)
    pred = np.argmax(prediction, axis=-1)
    return pred, prediction[0][pred[0]]


run = st.checkbox('Run')
FRAME_WINDOW = st.image([])
camera = cv2.VideoCapture(0)
if run is False:
    camera.release()

while run:
    x_points = []
    y_points = []
    _, frame = camera.read()
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hand.process(frame_rgb)
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            for id, ld in enumerate(landmarks.landmark):
                h, w, channels = frame.shape
                x_points.append(int(ld.x * w))
                y_points.append(int(ld.y * h))

            a1 = (int(max(y_points) + 30), int(min(y_points) - 30))
            a2 = (int(max(x_points) + 30), int(min(x_points) - 30))
        cv2.rectangle(frame, (a2[1], a1[1]), (a2[0], a1[0]), (0, 255, 0), 3)
        if len(x_points) == 21 or len(x_points) == 42:
            target = frame[a1[1]:a1[0], a2[1]:a2[0]]

            if len(target) > 0:
                m = model_upload()
                p, num = predict(m, frame)
                cv2.putText(frame, str(all_classes[p[0]]) + " " + str(100*num), (80, 80), cv2.FONT_ITALIC, 2, (255, 100, 100), 2)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(frame_rgb)


else:
    st.write('Stopped')
    camera.release()
