# coding: utf-8
# Plenari
'''
# * 平滑数据
# * 计算斯格明子所在的位置
# * 选择一个斯格明子，计算他的边界
# * 拟合该边界
'''
import pandas as pd
import numpy as np
import os
from sklearn.cluster import DBSCAN
#import matplotlib.pyplot as plt

def load_npz(ffile):
    '''
    只是简单的读取保存的npz数据
    
    '''
    f=np.load(ffile)
    x,y,z,mx,my,mz=f['x'],f['y'],f['z'],f['mx'],f['my'],f['mz']
    return x,y,z,mx,my,mz


def smooth(x,y,z):
    '''
    使三维数据铺平为二维数据
    x,y,z：使用的矩阵，且已经排过序。
    
    x不变，只要计算y-z的距离就可以。
    
    return :
    x不变，y变为y-z方向的距离,沿着0轴计算。
    '''
    new_y=np.zeros_like(y)
    new_y[1:]=np.sqrt((y[1:]-y[:-1])**2+(z[1:]-z[:-1])**2)
    new_y=new_y.cumsum(axis=0)
    return x,new_y

#x,y=smooth(x,y,z)

def SelectOneSkymion(m,sign=-1):  
    '''
    m为带有正负交界的磁矩信息，其中斯格明子位置的磁矩小于0，即sign为-1
    
    return :
     某一个斯格明子的位置限制
    '''
    #
    clf=DBSCAN(eps=15,min_samples=7)
    m_0=np.where((m*sign)>0)
    X=np.vstack([m_0[0],m_0[1]]).T
    clf.fit(X)
    if clf.labels_.max()==-1:
        return -1
    else:
        x=m_0[0][clf.labels_==0]
        y=m_0[1][clf.labels_==0]
        return x,y
#limitx,limity=SelectOneSkymion(m)    

def getxy(x,y,m):
    '''
    计算m在正负交界位置的坐标，坐标值从x,y矩阵获得
    
    x:x坐标，np.array,矩阵
    y:y坐标，np.array，矩阵
    m:需要处理的值，np.array ，矩阵
    
    return :两个一维列表x,y
    '''
    #数据左右相乘
    m_mul=m[:,:-1]*m[:,1:]
    #相乘结果小于零，左边的位置
    loc=np.where(m_mul<0)#
    #获取一个斯格明子索引
    limitx,limity=SelectOneSkymion(m)
    #得到一个斯格明子边界索引
    index=(loc[0]>limitx.min()-2)&(loc[0]<limitx.max()+2)&(loc[1]>limity.min()-2)&(loc[1]<limity.max()+2)
    locx,locy=loc[0][index],loc[1][index]#行列
    #斜率
    dm_dx=(m[(locx,locy+1)]-m[(locx,locy)])/(x[(locx,locy+1)]-x[(locx,locy)])
    #
    new_x=x[(locx,locy)]+(0-m[(locx,locy)])/dm_dx
    new_y=y[(locx,locy)]
    return new_x,new_y


def symbol_change_location(file):
    '''
    计算file符号改变位置的x,y
    
    file：npz数据
    '''
    x,y,z,mx,my,mz=load_npz(file)
    x,y=smooth(x,y,z)
    x,y=getxy(x,y,mz)
    return x,y

