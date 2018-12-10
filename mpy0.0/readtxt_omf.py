# -*- coding: utf-8 -*-
"""
2018年2月1日
功能：
 读取由omf转成的txt
方法：
1: 读取并返回需要的数据包括坐标以及坐标对应的能量或者磁矩。
"""
import numpy as np
import os
import pandas as pd
import re
def readtxt(fpath,ratio=1,cl=np.array([[0,1],[0,1],[0,1]]),\
          cm=np.array([[-1,1],[-1,1],[-1,1]]),D3=0,):
    '''
    ratio #int,整数且大于1，模型的缩放比例。
    D3  #是否返回3D数据结构,3d结构不能去掉全为0的磁矩
    cl  #array,x,y,z坐标范围的选择，
    cm  #array,磁矩除以Ms后mx,my,mz磁矩范围的选择
    输入内容是文件的地址，并进行按照某种步进刷选，不包括磁矩全为0的部分。
    '''
    assert isinstance(ratio,int),'img_ratio is int'
    assert cl.shape==(3,2),'clip_xyz is (3,2) array '
    assert cm.shape==(3,2),'clip_ms is (3,2) array'
    rat=ratio
    cx,cy,cz=cl[0],cl[1],cl[2]#坐标范围选择
    cmx,cmy,cmz=cm[0],cm[1],cm[2]#磁矩范围的选择。
    #read data    
    try:
        d=np.loadtxt(fpath)#文件里有中文，会读取失败。
    except:
        d=pd.read_table(fpath,header=None,dtype=float,comment='#',delim_whitespace=True)#pandas read
        d=np.array(d)#有中文也没有问题。

    x,y,z,mx,my,mz=d[:,0],d[:,1],d[:,2],d[:,3],d[:,4],d[:,5]#read data
    #set model_shape
    model_shape=np.array([len(set(z)),len(set(y)),len(set(x))])#计算形状
    assert model_shape.prod()==len(x),'Please enter the correct model parameters'

    #set Ms
    Ms=np.sqrt(mx**2+my**2+mz**2).mean()
    mx,my,mz=mx/Ms,my/Ms,mz/Ms#normal Ms;
    del d#delete d 

    #改变数据的形状        
    x=x.reshape(model_shape)[::rat,::rat,::rat]
    y=y.reshape(model_shape)[::rat,::rat,::rat]
    z=z.reshape(model_shape)[::rat,::rat,::rat]
    mx=mx.reshape(model_shape)[::rat,::rat,::rat]
    my=my.reshape(model_shape)[::rat,::rat,::rat]
    mz=mz.reshape(model_shape)[::rat,::rat,::rat]
    if D3:#如果需要3d的形状
        return x,y,z,mx,my,mz

    '''
    #删除全是0的位置。并且用其他方法筛选数据。
    #这里得到需要的数据。两个条件相加是'或'的关系，想乘是'并'的关系。
    #distance=np.sqrt((yi-40e-9)**2+(zi-40e-9)**2)
    #example:
    >>>index=((mz!=0.0)*(x<100e-9)*(x>50e-9)*(z>40e-9)*(distance<40e-9)*(distance>28e-9))
    '''
    indexl=((x>cx[0])*(x<cx[1])*(y>cy[0])*(y<cy[1])*(z>cz[0])*(z<cz[1]))#位置筛选结果
    indexm=((mx>cmx[0])*(mx<cmx[1])*(my>cmy[0])*(my<cmy[1])*(mz>cmz[0])*(mz<cmz[1]))#磁矩筛选结果
    inde0=((np.fabs(mz)+np.fabs(mx)+np.fabs(my))!=0.0)#非零筛选结果。
    index=indexl*inde0*indexm#所有筛选结果求并集
    z,x,y=z[index],x[index],y[index]#筛选索引里的坐标数据
    mz,my,mx=mz[index],my[index],mx[index]#筛选索引里的磁矩数据
    return x,y,z,mx,my,mz

def test(fpath):
    #########################读取格式的设置。
    clip_xyz=np.array([[0,1],[0,1],[0,1]])            #array,x,y,z坐标范围的选择，
    clip_ms=np.array([[-1,1],[-1,1],[-1,1]])         #array,磁矩除以Ms后mx,my,mz磁矩范围的选择
    ratio=2                                           #int,整数且大于1，画图时模型的缩放比例。
    return readtxt(fpath,ratio=2)

