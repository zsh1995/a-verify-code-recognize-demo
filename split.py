# -*- coding: UTF-8 -*-
import sys, os, re
#set default decoding way,when encoding
reload(sys)
sys.setdefaultencoding('utf-8')
# os.chdir('C:\Python27\Lib\site-packages\pytesser')

import Image,ImageEnhance,ImageFilter,ImageDraw
from pytesseract import *

def cut_edge(image):
    '''
    切割验证码边缘无字符部分
    '''
    #从x轴开始遍历，切割左右边缘
    split_blank = ()
    im = Image.open(image)
    data = list(im.getdata())
    w,h = im.size
    for x in range(w):
        if len(split_blank) == 0:
            for y in range(h):
                if data[ y*w + x ] < 200:
                    split_blank = split_blank + (x,0)
                    break
                else:
                    continue
        else:
            break
    for x in range(w)[::-1]:
        if len(split_blank) < 4:
            for y in range(h):
                if data[ y*w + x ] < 200:
                    split_blank = split_blank + (x,h-1)
                    break
                else:
                    continue
        else:
            break
    box = split_blank
    region = im.crop(box)
    #从y轴开始遍历，切割上下边缘
    split_blank = ()
    data = list(region.getdata())
    w,h = region.size
    for y in range(h):
        if len(split_blank) == 0:
            for x in range(w):
                if data[ y*w + x ] < 200:
                    split_blank = split_blank + (0,y)
                    break
                else:
                    continue
        else:
            break
    for y in range(h)[::-1]:
        if len(split_blank) < 4:
            for x in range(w):
                if data[ y*w + x ] < 200:
                    split_blank = split_blank + (w-1,y)
                    break
                else:
                    continue
        else:
            break
    box = split_blank
    region = region.crop(box)
    return region

def check(num,w,record):
    '''
    确认该位置是否是分割点
    '''
    #遍历点数列表，寻找数量为0的点并记录，如果在边缘则忽略
    #数量小于5则继续
    #遍历点数列表，寻找数量为1的点，记录，如果存在相邻点数相同的，则取较远的。如果在边缘则忽略
    #循环遍历直到数量等于5则停止
    if len(record) != 0:
        for i in record:
            if abs(num - i) > 20 and num > 19 and num < w-19:
                continue
            else:
                return False
    else:
        if num > 19 and num < w-19:
            return True
        else:
            return False
    return True

def cut_char(region):
    '''
    分割单个字符
    '''
    #将图片像素点投影到x轴，根据像素点分布确定每一个字符的边缘
    point_count = []
    data = list(region.getdata())
    w,h = region.size
    for x in range(w):
        point_num = 0
        for y in range(h):
            if data[ y*w + x ] < 200:
                point_num += 1
            else:
                continue
        point_count.append(point_num)
    record = []
    for point in range(0,15):
        if len(record) < 5:
            for i in range(len(point_count)):
                if point_count[i] == point:
                    if check(i,w,record):
                        record.append(i)
        else:
            break
    record.sort()
    return record

def correct(string):
    '''
    '''
    # if string == '\\':
    #     string = 'B'
    return string
    #b p 
    #a h

def getWide(im):
    '''
    return the wide of char
    '''
    im = im.point(lambda i: i * 4)
    data = list(im.getdata())
    widelist = []
    w,h = im.size
    for x in range(w):
        if len(widelist) == 0:
            for y in range(h):
                if data[ y*w + x ] < 200:
                    widelist.append(x)
                    break
                else:
                    continue
        else:
            break   
    for x in range(w)[::-1]:
        if len(widelist) < 2:
            for y in range(h):
                if data[ y*w + x ] < 200:
                    widelist.append(x)
                    break
                else:
                    continue
        else:
            break
    wide = widelist[1] - widelist[0]
    print wide
    return wide

def rotate(im,angle = 5):
    '''
    rotate
    '''
    lis = []
    data = list(im.getdata())
    w,h = im.size
    for y in range(h):
        for x in range(w):
            if data[ y*w + x ] == 0:
                lis.append(1)
            else:
                lis.append(data[ y*w + x ])
    im.putdata(lis)     
    rotate = im.rotate(angle,expand = 1)
    #去除黑边
    w,h = rotate.size
    copy = Image.new('L',rotate.size)
    lis = []
    data = list(rotate.getdata())
    for y in range(h):
        use = 1
        for x in range(w):
            if use == 1:
                if data[ y*w + x ] == 0:
                    lis.append(255)
                else:
                    lis.append(data[ y*w + x ])
                    use = 0
            else:
                lis.append(data[ y*w + x ])

    copy.putdata(lis)
    data = list(copy.getdata())
    lis = []                
    for y in range(h):
        alis = []
        use = 1
        for x in range(w)[::-1]:
            if use == 1:
                if data[ y*w + x ] == 0:
                    alis.append(255)
                else:
                    alis.append(data[ y*w + x ])
                    use = 0
            else:
                alis.append(data[ y*w + x ])
        for it in alis[::-1]:
            lis.append(it)
    copy.putdata(lis)
    # copy.show()
    return copy

def rotateToMin(im):
    '''
    使用旋转卡壳进行判别，找出最小宽度
    '''
    # print 'rotateToMin'
    rotateIm = rotate(im)
    oriWide = getWide(im)
    rotateWide = getWide(rotateIm)
    if rotateWide >= oriWide:
        rotateIm = rotate(im, angle = -5)
        rotateWide = getWide(rotateIm)
        if rotateWide >= oriWide:
            minIm = im
            return minIm.point(lambda i: i * 4)
        else:
            minIm = rotateIm
            oriWide = rotateWide
            for i in range(2,100):
                rotateIm = rotate(im, angle = -5*i)
                rotateWide = getWide(rotateIm)
                if rotateWide >= oriWide:
                    return minIm.point(lambda i: i * 4)
                else:
                    minIm = rotateIm
                    oriWide = rotateWide
    else:
        minIm = rotateIm
        oriWide = rotateWide
        for i in range(2,100):
            rotateIm = rotate(im, angle = 5*i)
            rotateWide = getWide(rotateIm)
            if rotateWide >= oriWide:
                return minIm.point(lambda i: i * 4)
            else:
                minIm = rotateIm
                oriWide = rotateWide
    # return im

def char_to_string(record,region):
    '''
    cut it,and return a string-l fontyp 
    '''
    # print 'char_to_string'
    w,h = region.size
    try:
        box = (0,0,record[0],h)
        char1 = rotateToMin(region.crop(box))
        # char1.show()
    except:
        return 'error'
        # char1 =  None
    try:   
        box = (record[0],0,record[1],h)
        char2 = rotateToMin(region.crop(box))
        # char2.show()
    except:
        return 'error'
        # char2 =  None
    try:        
        box = (record[1],0,record[2],h)
        char3 = rotateToMin(region.crop(box))
        # char3.show()
    except:
        return 'error'
        # char3 =  None
    try:
        box = (record[2],0,record[3],h)
        char4 = rotateToMin(region.crop(box))
        # char4.show()
    except:
        return 'error'
        # char4 =  None
    try:
        box = (record[3],0,record[4],h)
        char5 = rotateToMin(region.crop(box))
        # char5.show()
    except:
        return 'error'
        # char5 =  None
    try:    
        box = (record[4],0,w,h)
        char6 = rotateToMin(region.crop(box))
        # char6.show()
    except:
        return 'error'
        # char6 =  None
    # return char1,char2,char3,char4,char5,char6  
    str1 = correct(image_to_string(char1,config='-psm 10'))
    str2 = correct(image_to_string(char2,config='-psm 10'))
    str3 = correct(image_to_string(char3,config='-psm 10'))
    str4 = correct(image_to_string(char4,config='-psm 10'))
    str5 = correct(image_to_string(char5,config='-psm 10'))
    str6 = correct(image_to_string(char6,config='-psm 10'))
    string = str1+str2+str3+str4+str5+str6
    return string

def main(image):
    '''
    main func
    '''
    # print 'main'
    region = cut_edge(image)
    # region.show()
    record = cut_char(region)
    # print record
    string = char_to_string(record,region)
    print string
    # char1,char2,char3,char4,char5,char6 = char_to_string(record,region)
    # return char1,char2,char3,char4,char5,char6

if __name__ == '__main__':
    # for i in range(1,80):
    #     image = 'E:\pil\spin\image'+'\image' + str(i) + '.jpg'
    #     char1,char2,char3,char4,char5,char6 = main(image)
    #     if char1 is not None:
    #         char1.save('E:\pil\spin\char1\\' + str(i) + 'char1.tif')
    #     if char2 is not None:
    #         char2.save('E:\pil\spin\char1\\' + str(i) + 'char2.tif')
    #     if char3 is not None:
    #         char3.save('E:\pil\spin\char1\\' + str(i) + 'char3.tif')
    #     if char4 is not None:
    #         char4.save('E:\pil\spin\char1\\' + str(i) + 'char4.tif')
    #     if char5 is not None:
    #         char5.save('E:\pil\spin\char1\\' + str(i) + 'char5.tif')
    #     if char6 is not None:
    #         char6.save('E:\pil\spin\char1\\' + str(i) + 'char6.tif')
    image = 'E:\pil\spin\image\image20.jpg'
    main(image)
    # image = '25char5.tif'
    # im = Image.open(image)
    # rotateToMin(im).show()
        