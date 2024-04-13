import os
import mediapipe as mp
import cv2
import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D, Flatten, Dropout, Dense, MaxPooling2D
from sklearn import preprocessing
all_classes = os.listdir("D:/ASL")

label_encode = preprocessing.LabelEncoder()
# from keras.utils import to_categorical
Data_img = []
Labels = []
for path in os.listdir("D:/ASL"):
    full_path = "D:/ASL/" + path
    print(path)
    a=0
    for images in os.listdir(full_path):
        img = cv2.imread(full_path+'/'+str(images))
        img = cv2.resize(img, dsize=(100, 100))
        img = img/255
        Data_img.append(img)
        Labels.append(path)
print(len(Data_img), len(Labels))
Data_img = np.array(Data_img)
# Labels = np.array(Labels)

model = Sequential()

model.add(Conv2D(filters=128, kernel_size=(3, 3), activation="relu", input_shape=(100, 100, 3)))
model.add(Conv2D(filters=128, kernel_size=(2, 2), activation="relu", input_shape=(100, 100, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))


model.add(Flatten())
model.add(Dense(128, activation="relu"))
model.add(Dropout(0.4))
model.add(Dense(17, activation="sigmoid"))
Labels = label_encode.fit_transform(Labels)
# Labels = to_categorical(Labels)
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
print(model.summary())

model.fit(Data_img, Labels, batch_size=64, epochs=5, steps_per_epoch=150)

if os.path.isfile("D:/gestures.h5") is False:
    model.save("D:/gestures.h5")

from keras.models import load_model
model = load_model("D:/gestures.h5")
img = cv2.imread("D:/ASL/Pay/Pay_498.jpg")
img = cv2.resize(img, (100, 100))
img = img/255
test_img = np.expand_dims(img, axis=0)
prediction = model.predict(test_img)
# print(prediction)
# print(model.predict_classes(prediction))
pred = np.argmax(prediction, axis=-1)
print(pred)

# from keras.preprocessing import image
mphands = mp.solutions.hands
hand = mphands.Hands(max_num_hands=2, min_detection_confidence=0.75)
mpdraw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)
xsum = 0
ysum = 0
while True:
    x_points = []
    y_points = []
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hand.process(frame_rgb)
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            for id, ld in enumerate(landmarks.landmark):
                h, w, channels = frame.shape
                x_points.append(int(ld.x * w))
                y_points.append(int(ld.y * h))

            a1 = (int(max(y_points)+30), int(min(y_points)-30))
            a2 = (int(max(x_points)+30), int(min(x_points)-30))
        cv2.rectangle(frame, (a2[1], a1[1]), (a2[0], a1[0]), (0, 255, 0), 3)
        if len(x_points) == 21 or len(x_points) == 42:
            target = frame[a1[1]:a1[0], a2[1]:a2[0]]
            # print(len(target))
            if len(target) > 0:
                # cv2.imshow("HAND", target)
                target = cv2.resize(target, (100, 100))
                test_img = np.expand_dims(target, axis=0)
                test_img = test_img / 255
                prediction = model.predict(test_img)
                pred = np.argmax(prediction, axis=-1)
                cv2.putText(frame, str(all_classes[pred[0]]), (80, 80), cv2.FONT_ITALIC, 2, (255, 100, 100), 2)
                print(all_classes[pred[0]], np.max(prediction))
    cv2.imshow("WINDOW", frame)
    if cv2. waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()
cap.release()
