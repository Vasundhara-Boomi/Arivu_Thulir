import cv2
import time
import mediapipe as mp
from statistics import mode
ptime = 0
mphands = mp.solutions.hands
hands = mphands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)
mpdraw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)


def dist(p1, p2):
    return int(((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5)


while True:
    ret, frame = cap.read()
    ctime = time.time()
    fps = 1/(ctime - ptime)
    ptime = ctime
    # set_sym = []
    ld_point = []
    dist_list = [0, 0, 0]  # distance between 1st and 2nd, 2nd and 3rd, 3rd and 4th fingers
    dist_from_thumb = [0, 0, 0, 0]
    symbol = 0
    a = 0
    a1 = 0
    bool_list = [0, 0, 0, 0, 0]
    cv2.putText(frame, "FPS: "+str(int(fps)),(80,80),cv2.FONT_HERSHEY_PLAIN,2, (0,0,0),2)
    frame_rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)
    if result.multi_hand_landmarks:
        for landmarks in result.multi_hand_landmarks:
            for id,lm in enumerate(landmarks.landmark):
                w, h, depth = frame.shape
                ld_point.append((lm.x, lm.y))
                ld_point[int(id)] = (int(lm.x*h), int(lm.y*w))
            unit = dist(ld_point[0], ld_point[13])
            for i in range(8, 21, 4):
                j=int(i/4) -2
                dist_from_thumb[j]=int(((ld_point[i][0] - ld_point[4][0])**2 + (ld_point[i][1] - ld_point[4][1])**2)**0.5)
                if ld_point[i][1] < ld_point[i-2][1]:
                    bool_list[j] = 1
                else:
                    bool_list[j] = 0
            if ld_point[4][0] > ld_point[3][0]:
                bool_list[4] = 1
            else:
                bool_list[4] = 0
            for i in range(8, 17, 4):
                j=int(i/4) -2
                dist_list[j] = int(((ld_point[i][0]-ld_point[i+4][0])**2 + (ld_point[i][1]-ld_point[i+4][1])**2)**0.5)
            if bool_list[0:4] == [0,0,0,0] and bool_list[4] == 1 and sum(dist_list) < 1.2*unit:
                symbol = 'A'
            elif bool_list[0:4] == [1,1,1,1] and bool_list[4] == 0 and sum(dist_list) < 180:
                symbol = 'B'
            for i in range(8, 21, 4):
                if ld_point[i][0] > ld_point[i-2][0] and bool_list[4] == 1 and dist_from_thumb[0]+10 > dist_from_thumb[1]:
                    symbol = 'C'
            if bool_list[1:5] == [0, 0, 0, 0] and min(dist_from_thumb) == dist_from_thumb[1] and max(dist_from_thumb) == dist_from_thumb[0]:
                symbol = 'D'
            elif bool_list[0:5] == [0, 0, 0, 0, 0] and ld_point[4][0] < ld_point[8][0] and ld_point[4][1]>ld_point[8][1]:
                symbol = 'E'
                a+=1
            if bool_list[1:4] == [1, 1, 1] and bool_list[0] == 0 and bool_list[4] == 0 and min(dist_from_thumb) == dist_from_thumb[0]:
                symbol = 'F'
            for i in range(4, 9, 4):
                if ld_point[i][0] > ld_point[i-2][0] and bool_list[0:4] == [0, 0, 0, 0] and dist_from_thumb[0] <unit:
                    for j in range(12, 21, 4):
                        if ld_point[i][0] > ld_point[i-3][0]:
                            symbol = 'G'
                            a1 += 1
            for i in range(8, 17, 4):
                if ld_point[i][0] < ld_point[i-2][0] and bool_list[4] == 0 and dist_list[0] < 100:
                    if ld_point[16][0]>ld_point[14][0] and ld_point[20][0]>ld_point[18][0] and bool_list[4] == 0:
                        for j in range(5,8):
                            if ld_point[j][1]-10 < ld_point[8][1] and dist_from_thumb[0]>100:
                                symbol = 'H'
            if bool_list[0:4] == [0, 0, 0, 1] and bool_list[4] == 0:
                symbol = 'I'
            for i in range(8, 17, 4):
                if ld_point[i][0] > ld_point[i-2][0] and ld_point[4][1] < ld_point[3][1] and bool_list[0:3] == [0, 0, 0]:
                    if ld_point[20][0] < ld_point[18][0]:
                        symbol = 'J'
            if bool_list[0:5] == [1, 1, 0, 0, 1] and 1.7*dist_list[0] > unit and ld_point[9][0]<ld_point[4][0]<ld_point[6][0] and ld_point[4][1]<ld_point[5][1]:
                symbol = 'K'
            if bool_list[1:4] == [0, 0, 0] and dist_from_thumb[0] > 2*unit:
                symbol = 'L'
            if bool_list[0:5] == [0,0,0,0,0] and ld_point[4][0]<ld_point[8][0]:
                symbol = 'M'
            if bool_list[0:5] == [0,0,0,0,0] and ld_point[4][0] < ld_point[8][0] and ld_point[4][1] < ld_point[14][1]:
                symbol = 'N'
            if bool_list[0:5] == [0, 0, 0, 0, 1] and min(dist_from_thumb) == dist_from_thumb[1] and dist_from_thumb[0:5]<[90, 90, 90, 90, 90]:
                symbol = 'O'
            for i in range(8,13,4):
                j = i+8
                if ld_point[i][0] > ld_point[i-2][0] and ld_point[j][0] < ld_point[j-2][0]:
                    if ld_point[6][1] < ld_point[4][1] < ld_point[10][1]:
                        symbol = 'P'
            for i in range(12,21,4):
                if ld_point[i][0]>ld_point[i-2][0]:
                    if ld_point[8][0]<ld_point[6][0] and ld_point[4][0]<ld_point[3][0] and ld_point[8][1]>ld_point[5][1]+120:
                        symbol = 'Q'
            if bool_list[2:5] == [0, 0, 0] and dist_list[0]<10 and bool_list[0:2] == [1, 1]:
                symbol = 'R'
            if bool_list[0:4] == [0, 0, 0, 0] and ld_point[3][0] > ld_point[4][0] > ld_point[6][0]:
                symbol = 'S'
            if bool_list[0:5] == [0,0,0,0,0] and ld_point[12][0] < ld_point[4][0] < ld_point[8][0] and ld_point[4][1] < ld_point[6][1]:
                symbol = 'T'
            if bool_list[0:5] == [1, 1, 0, 0, 0] and 10<dist_list[0]<60:
                symbol = 'U'
            if bool_list[0:5] == [1, 1, 0, 0, 0] and dist_list[0]>60 and ld_point[4][0]<ld_point[10][0]:
                symbol = 'V'
            if bool_list[0:5] == [1, 1, 1, 0, 0] and dist_list[0]<70 and dist_list[1]<70:
                symbol = 'W'
            # if bool_list[0:5] == [1, 0, 0, 0, 0] and ld_point[7][1]<ld_point[8][1]<ld_point[5][1]:
            #    symbol = 'X'
            if symbol == 'J':
                if a1>0:
                    symbol = 'G'
            if a>0:
                symbol = 'E'
            print(dist_list[0], unit)
            mpdraw.draw_landmarks(frame, landmarks, mphands.HAND_CONNECTIONS)
    cv2.putText(frame, str(symbol), (40, 50), cv2.FONT_HERSHEY_PLAIN, 3, (0,0,0),3)
    cv2.imshow('Window', frame)
    if cv2.waitKey(1) == ord('q'):
        # cv2.imwrite('hand_symbols_output2.jpg', frame)
        break
cv2.destroyAllWindows()
cap.release()