import cv2
import numpy as np

# opencv2中坐标原点：左上角
dic = {"1": "红（报警）", "2": "绿（运行）", "3": "空闲", "4": "蓝（关机）", "5": "黄（调试）"}
location_data = [(660 - 53, 665 - 57), (865 - 53, 550 - 57), (1185 - 53, 362 - 57), (1428 - 53, 505 - 57),
                 (1791 - 53, 713 - 57), (1995 - 53, 830 -
                                         57), (2198 - 53, 947 - 57), (2400 - 53, 1065 - 57),
                 (2603 - 53, 1180 - 57), (2801 - 53, 1297 - 53),
                 (2893 - 53, 1724 - 57), (2696 - 53,
                                          1842 - 57), (613 - 53, 1047 - 57),
                 (1809 - 54, 1035 - 66), (2003 - 54, 1147 -
                                          66), (2197 - 54, 1259 - 66), (2391 - 54, 1371 - 66),
                 (2585 - 54, 1483 - 66), (2371 - 54,
                                          1607 - 66), (2177 - 54, 1495 - 66),
                 (1983 - 54, 1383 - 66), (1789 - 54, 1271 -
                                          66), (1595 - 54, 1159 - 66), (1401 - 54, 1047 - 66),
                 (1208 - 54, 935 - 66), (1013 - 54, 823 - 66), ]


def add_alpha_channel(img):
    """为jpg图像添加alpha通道

    Args:
        img (_type_): _description_

    Returns:
        _type_: _description_
    """
    b_channel, g_channel, r_channel = cv2.split(img)
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
    new_img = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
    return new_img


def merge_png_with_jpg(jpg_img, png_img, x1, y1, x2, y2):
    """_summary_

    Args:
        jpg_img (_type_): 大图
        png_img (_type_): 小图
        x1 (_type_): 截图位置：左上角
        y1 (_type_): 
        x2 (_type_): 截图位置：右下角
        y2 (_type_): 

    Returns:
        _type_: _description_
    """
    if jpg_img.shape[2] == 3:
        jpg_img = add_alpha_channel(jpg_img)

    alpha_png = png_img[0:png_img.shape[0], 0:png_img.shape[1], 3] / 255.0
    alpha_jpg = 1 - alpha_png

    # 这里参考：https://blog.csdn.net/u013066730/article/details/125453249
    for i in range(0, 3):
        jpg_img[y1:y2, x1:x2, i] = ((alpha_jpg * jpg_img[y1:y2, x1:x2, i]) + (
            alpha_png * png_img[0:png_img.shape[0], 0:png_img.shape[1], i]))

    return jpg_img


def main():
    # 读取信号
    while True:
        f = open('dataset.txt', 'r')
        txt = f.readline()
        lst = list(txt)
        f.close()
        # 读取大图 尺寸 3840x2160
        jpg_img = cv2.imread('B车间效果图底图.JPG', cv2.IMREAD_UNCHANGED)
        for i in range(len(lst)):
            if int(lst[i]) == 3:
                continue
            if i <= 12:
                png_img_name = "竖直" + str(dic[lst[i]]) + ".png"
            else:
                png_img_name = "水平" + str(dic[lst[i]]) + ".png"

            # 读取贴片图 尺寸 226x127
            png_img = cv2.imread(png_img_name, cv2.IMREAD_UNCHANGED)  # 读取四通道图片

            # (x1, y1) (x2, y2) 叠加位置
            x1 = location_data[i][0]
            y1 = location_data[i][1]
            x2 = x1 + 226
            y2 = y1 + 127

            jpg_img = merge_png_with_jpg(jpg_img, png_img, x1, y1, x2, y2)

        cv2.imshow('jpg_img', jpg_img)

        key = cv2.waitKey(0)
        if key == 27 or key == 113:  # 27 是 ESC 键的键值，113 是 q 键的键值
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    print("done!")
