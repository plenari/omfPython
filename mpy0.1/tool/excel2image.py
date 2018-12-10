# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 09:03:55 2018
1. 用来把excel的数据用图片保存到excel所在的文件夹内
@author: omf
"""
import os 
import pandas as pd
import matplotlib.pyplot as plt

def savef(file,para):
    '''
    file:保存路径
    para:二维数据结构。
    return:None
    '''
    fig=plt.figure()
    plt.imshow(para)
    fig.savefig(file)
    plt.close()

def ana():
    dpath=input(r"Please enter the excel file folder address\n:")
    ffile=[i for i in os.listdir(dpath) if i.split('.')[-1]=='xlsx']#筛选后缀是txt的文件
    for i in ffile:
        filei=os.path.join(dpath,i)
        f=pd.read_excel(filei)
        savef(filei.replace('.xlsx','.png'),f)    
    
        
if __name__=='__main__':
    ana()