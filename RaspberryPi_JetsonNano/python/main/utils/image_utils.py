# import cv2
# import matplotlib.pyplot as plt
# import numpy as np
# import math
# import os
# import pandas as pd
# from tqdm import tqdm
#
# # image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/image')
# # print(image_dir)
# # image = cv2.imread(os.path.join(image_dir, "test_weather_ic.png"),0)
# # h = image.shape[0]
# # w = image.shape[1]
# #
# # ## 唯一确定阈值
# # a = 150
# # new_image = np.zeros((h,w),np.uint8)
# # for i in tqdm(range(h)):
# #     for j in range(w):
# #         if(image[i,j] > a ):
# #             new_image[i,j] = 255
# #         else:
# #             new_image[i,j] = 0
# #
# # print(new_image)
# # cv2.imwrite(os.path.join(image_dir, "test_weather_ic_new.png"), new_image)
#
#
# image_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/image')
# img  = cv2.imread(os.path.join(image_dir, "test_weather_ic.png"),0)
# cv2.imshow('src', img)
# print(img.shape)
#
# result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
#
# for i in range(0, img.shape[0]):  # 访问所有行
#     for j in range(0, img.shape[1]):  # 访问所有列
#         if img[i, j, 0] > 200 and img[i, j, 1] > 200 and img[i, j, 2] > 200:
#             result[i, j, 3] = 0
#
# cv2.imwrite(os.path.join(image_dir, "test_weather_ic_new.png"), result, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
# print(result.shape)
# cv2.imshow('result', result)
# B, G, R, A = cv2.split(result)
# cv2.imshow('B', B)
# cv2.imshow('G', G)
# cv2.imshow('R', R)
# cv2.imshow('A', A)
#
# cv2.waitKey()
# cv2.destroyAllWindows()