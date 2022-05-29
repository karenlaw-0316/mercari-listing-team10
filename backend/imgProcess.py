import os
import cv2
import base64
import numpy as np
from pathlib import Path
from typing import Union, List

def img_base64(img):
    base64_str = cv2.imencode('.jpg', img)[1].tostring()
    base64_str = base64.b64encode(base64_str)
    return base64_str

def removeBackground(img_path, img_filename, x, y, w, l):

    rect = (x, y, w, l)
    rect_or_mask = 0      # flag of selecting rect or mask mode

    img = cv2.imread(img_path)
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

    cv2.imwrite(f'db/mask/mask_{img_filename}',result_mask)
    print(f"Write db/mask/mask_{img_filename}")


def addBackground(img_path, img_filename, color, background_path):
    print(f"Add background to {img_filename}")

    try:
        img = cv2.imread(img_path)
        if img is None:
            print(f"Can not read {img_path}")
            return

        img_m = cv2.imread(f'db/mask/mask_{img_filename}') # mask image
        if img_m is None:
            print(f"Can not read db/mask/mask_{img_filename}")
            img_m = cv2.imread('db/mask/mask_default.jpg')

        # resize image and img_m
        height, width = img.shape[:2] # get height and width of img
        height = 200
        width = 200
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

        if background_path is None or not os.path.exists(background_path):
            print("Background does not exist")
            for r in range(height):
                for c in range(width):
                    if bg_mask[r, c] == 255: # if the pixel is white
                        result[r, c] = (color[2], color[1], color[0]) # (B,G,R)
        else:
            # read background
            img_bg = cv2.imread(background_path)

            img_bg = cv2.resize(img_bg, (width, height))

            # merge img and background
            img_bg = cv2.bitwise_and(img_bg, img_bg, mask = bg_mask)
            img = cv2.bitwise_and(img, img, mask = img_mask)
            result = cv2.add(img_bg, img)

        # for debug
        #cv2.imshow('res', result)
        #cv2.waitKey(0)

        print(img_base64(result))
        return img_base64(result)
    except NameError:
        print("NameError")
    except Exception:
        print("Exception")
