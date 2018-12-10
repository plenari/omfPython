# -*- coding: utf-8 -*-
#python3
"""
2017年9月6日
@author: 409200093@qq.com
模仿windows创建文件夹，若已经存在会自动在文件夹后面添加数字，直到成功。

2018年11月13日
添加注释
"""
import sys  
if '..' not in sys.path:
    sys.path.append('..')
import os
import shutil
from tool.selectSuffix import selectSuffix
namenum=0

def mdirs(name,num):
    '''
    递归创建文件夹，直到成功
    '''
    global namenum
    try:
        os.makedirs(name+str(namenum))
    except:
        namenum+=1
        mdirs(name,namenum)

def CreDir(namedirs,fdirs=os.getcwd()):
    '''
    namedirs:创建文件夹的名字
    fdirs:在那个文件夹创建
    
    >>>CreDir('xlsx',r'c:')
    
    '''
    file1=os.listdir(fdirs)
    os.chdir(fdirs)
    try:
        os.makedirs(namedirs)
    except:
        mdirs(namedirs,0)
    file2=os.listdir(fdirs)
    return os.path.join(fdirs,[i for i in file2 if i not in file1][0])#return new dirs


def smove(suffix,newdir,fdir=os.getcwd(),flag=''):#后缀，路径
    '''
    suffix:移动文件的后缀名称。
    fdir:移动文件的地址。
    newdir:新建一个文件夹，然后移动到这个里面。
    flag:只有文件名字里有这个字符才会移动。
    
    Example:将后缀为.xlsx 的移动到c: excel
    
    >>>
    
    '''
    cfdir=CreDir(newdir,fdir)#create new dir
    fnames=selectSuffix(fdir,suffix)[1]
    
    for f in fnames:        
        if flag in f:            
            shutil.move(os.path.join(fdir,f),os.path.join(cfdir,f))
            
if __name__=='__main__':
    print('will crate ok in current dirs')
    print(CreDir('ok'))
