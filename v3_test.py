import os

import cv2

for path in os.listdir(r'D:\repository\git\jiangyou_play_dnf'):
    if path.endswith('.jpg'):
        mat = cv2.imread(path)
        print(mat)
