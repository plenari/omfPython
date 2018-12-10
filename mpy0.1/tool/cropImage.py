# -*-coding:utf-8-*-
'''
用来剪切图片，
为了保证图片剪切的一致，可以使用这个程序
'''
from PIL import Image
import os

def crop_image(file,ul,ur,dl,dr):
    '''
    file :图片地址
    ul,upper left
    ur ,upper right
    dl, down left
    dr,down right
    '''
    try:
        im = Image.open(file)
        suffix=os.path.splitext(file)[1]    
        region = im.crop((ul,ur,dl,dr))
        region.save(file.replace(suffix,'-crop{}'.format(suffix)))

    except Exception as e:
        print(e)
        
if __name__=='__main__':
    fdirs=input(r'输入需要裁剪图片的文件夹')
    #ul,ur,dl,dr=110,210,810,750
    ul,ur,dl,dr=348,160,1047,665
    for i in os.listdir(fdirs):
        
        crop_image(os.path.join(fdirs,i),ul,ur,dl,dr)