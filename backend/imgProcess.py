import os
import cv2
import base64
import numpy as np
from pathlib import Path
from typing import Union, List


MASKPATH = "./db/mask"
BGPATH = "./db/backgrounds"

def img_base64(img):
    base64_str = cv2.imencode('.jpg', img)[1].tostring()
    base64_str = base64.b64encode(base64_str)
    return base64_str

def base64_img(imgbase64):
    imgstr = base64.b64decode(imgbase64)
    nparr = np.fromstring(imgstr, np.uint8)
    img = cv2.imdecode(nparr, cv2.COLOR_BGR2RGB)
    return img

def removeBackground(imgbase64, img_filename, x, y, w, l):

    rect = (x, y, w, l)
    rect_or_mask = 0      # flag of selecting rect or mask mode
    
    img = base64_img(imgbase64)
    mask = np.zeros(img.shape[:2], dtype = np.uint8) # mask initialization
    result = img.copy()         # result image
    result_mask = mask.copy()   # result mask

    try:
        for i in range(5):
            bgdmodel = np.zeros((1, 65), np.float64)
            fgdmodel = np.zeros((1, 65), np.float64)
            if (rect_or_mask == 0):         # grabcut with rect
                cv2.grabCut(img, mask, rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_RECT)
                rect_or_mask = 1
            elif (rect_or_mask == 1):       # grabcut with mask
                cv2.grabCut(img, mask, rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_MASK)

        result_mask = np.where((mask==1) + (mask==3), 255, 0).astype('uint8')
        output = cv2.bitwise_and(img, img, mask=result_mask)
    except:
        import traceback
        traceback.print_exc()

    cv2.imwrite(f'{MASKPATH}/mask_{img_filename}',result_mask)
    print(f"Write {MASKPATH}/mask_{img_filename}")


def addBackground(imgbase64, img_filename, color, background_id):
    print(f"Add background to {img_filename}")

    try:
        img = base64_img(imgbase64)

        img_m = cv2.imread(f'{MASKPATH}/mask_{img_filename}') # mask image
        if img_m is None:
            print(f"Can not read {MASKPATH}/mask_{img_filename}")
            img_m = cv2.imread('{MASKPATH}/mask_default.jpg')

        # resize image and img_m
        height, width = img.shape[:2] # get height and width of img
        img = cv2.resize(img, (width, height))
        img_m = cv2.resize(img_m, (width, height))
        result = img.copy()

        # generate mask
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([70, 70, 70])
        bg_mask = cv2.inRange(img_m, lower_black, upper_black)
        kernel = np.ones((2,2), np.uint8)
        bg_mask = cv2.dilate(bg_mask, kernel, iterations = 1)
        img_mask = ~bg_mask

        if background_id is 0 or not os.path.exists(f'{BGPATH}/bg{background_id}.jpg'):
            print("Background does not exist")
            for r in range(height):
                for c in range(width):
                    if bg_mask[r,c] == 255: # if the pixel is white
                        result[r,c] = (color[2], color[1], color[0]) # (B,G,R)
        else:
            # read background
            img_bg = cv2.imread(f'{BGPATH}/bg{background_id}.jpg')

            img_bg = cv2.resize(img_bg, (width, height))

            # merge img and background
            img_bg = cv2.bitwise_and(img_bg, img_bg, mask = bg_mask)
            img = cv2.bitwise_and(img, img, mask = img_mask)
            result = cv2.add(img_bg, img)

        # for debug
        #cv2.imshow('res', result)
        #cv2.waitKey(0)
        #print(img_base64(result))

        return img_base64(result)
    except NameError:
        print("NameError")
    except Exception:
        print("Exception")
