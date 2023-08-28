import cv2
import numpy as np
import math

if __name__ == '__main__':
    ############################################
    file_name = '1.jpg'  # 修改成你的图片路径
    ############################################

    # 表盘45度的读数  一般是0
    vol45 = 0
    # 表盘315度的读数
    vol315 = 1

    img = cv2.imread(file_name)  # 读入图片
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度化
    debug = False  # 须手动调整
    if debug:
        cv2.imshow('gray', gray)
        cv2.waitKey(0)
    # 返回所有圆的中心坐标和半径信息向量circles(x,y,r)  这里只取第一个
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, minDist=10, param1=100, param2=100, minRadius=30,
                               maxRadius=120)
    if debug:
        print(len(circles[0]))  # 总共识别到多少个圆
    lst = []
    for i in range(len(circles[0])):
        lst.append(circles[0][i][2])
    k = lst.index(max(lst))  # 最大圆的序号
    x = int(circles[0][k][0])  # 圆心 (x, y) 半径 r
    y = int(circles[0][k][1])  # 此处x指图片宽度 y指图片高度
    r = int(circles[0][k][2])
    if debug:
        print(r)
    mask = np.zeros(gray.shape[:2], dtype=np.uint8)  # 圆形掩膜
    cv2.circle(mask, (x, y), int(r * 0.55),
               (255, 255, 255), -1)  # 画圆 画小一点 -1表示画实心圆
    cv2.circle(img, (x, y), 5, (0, 0, 255), -1)  # 画圆心
    gray_circle = cv2.add(gray, np.zeros(
        np.shape(gray), dtype=np.uint8), mask=mask)
    if debug:
        cv2.imshow("gray_circle", gray_circle)
        cv2.waitKey(0)
    equ = cv2.equalizeHist(gray_circle)  # 直方图均衡化
    if debug:
        cv2.imshow("equ", equ)
        cv2.waitKey(0)
    gray_circle_not = cv2.bitwise_not(gray_circle)  # 像素取反
    if debug:
        cv2.imshow("gray_circle_not", gray_circle_not)
        cv2.waitKey(0)
    gray_circle_and = cv2.bitwise_and(gray_circle_not, mask)  # 并操作
    if debug:
        cv2.imshow("gray_circle_and", gray_circle_and)
        cv2.waitKey(0)

    med = cv2.medianBlur(gray_circle_and, 5)  # 中值滤波 5 x 5
    if debug:
        cv2.imshow("med", med)
        cv2.waitKey(0)

    kernel = np.ones((3, 3), np.uint8)
    open = cv2.morphologyEx(med, cv2.MORPH_OPEN, kernel)  # 开运算 先腐蚀后膨胀
    if debug:
        cv2.imshow("open", open)
        cv2.waitKey(0)

    ero = cv2.erode(open, kernel, iterations=1)  # 腐蚀 作用：去除白色点
    if debug:
        cv2.imshow("ero", ero)
        cv2.waitKey(0)
    # 若某像素点的q值大于第二个参数，则将其值改成第三个参数 255白 0黑
    ret, thre = cv2.threshold(ero, 100, 255, cv2.THRESH_BINARY)  # 二值化
    if debug:
        cv2.imshow("thre", thre)
        cv2.waitKey(0)

    lines = cv2.HoughLinesP(thre, 1.0, np.pi / 180, 40,
                            lines=500, minLineLength=5, maxLineGap=0)
    if lines is not None:
        # print(lines)
        lst1 = []
        for i in range(len(lines)):
            x1, y1, x2, y2 = lines[i][0]
            a = lines[i][0][2]-lines[i][0][0]
            b = lines[i][0][3]-lines[i][0][1]
            c = int(math.sqrt(a*a+b*b))
            if c > 40:
                lst1.append(c)
                if debug:
                    print(x1, y1, x2, y2)
                    print(a)
                    print(b)
                    print(c)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 1)
            else:
                lst1.append(0)
        k = lst1.index(max(lst1))
        x1, y1, x2, y2 = lines[k][0]  # 此处x指图片宽度 y指图片高度
        if debug:
            print('data:', x1, y1, x2, y2)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        if (x1 - x) ** 2 + (y1 - y) ** 2 > (x2 - x) ** 2 + (y2 - y) ** 2:
            # X1,Y1为指针头  X2,Y2为指针尾巴
            k = abs(y - y1) / abs(x - x1)  # 直线斜率
            angle = math.degrees(math.atan(k))  # 与水平线的角度
            if y1 > y:
                angle = 90 - angle
            else:
                angle = 90 + angle
        else:
            # cv2.line(img, (x, y), (x2, y2), (0, 255, 0), 2)
            k = abs(y - y2) / abs(x - x2)  # 直线斜率
            angle = math.degrees(math.atan(k))  # 与水平线的角度
            if y2 > y:
                angle = 270 + angle
            else:
                angle = 270 - angle
        if debug:
            print("角度：", int(angle), "度")
            cv2.imshow("title", img)
            cv2.waitKey(0)
        # 45度对应0mpa  315度对应1mpa，因此下面公式 可由度数转mpa
        vol = round((int(angle)-45)*(vol315-vol45)/270, 2)
        if vol < 0.05:
            vol = 0
        print(vol, "MPa")
    else:
        print("未找到直线")
