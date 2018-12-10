# -*- coding: utf-8 -*-
"""
2018年2月1日
功能：
 读取由omf转成的txt或者保存成text格式的ovf文件(默认)。
方法：
1: 读取并返回需要的数据包括坐标以及坐标对应的能量或者磁矩(mx,my,mz,E)。
2，用muamx保存的text文件有三列磁矩，需要计算出对应的坐标(也可以通过omf2txt转格式为txt)。
3,通过txt头部注释内的参数计算坐标。
"""
import numpy as np
import os
import pandas as pd
import re

# keyword list from ovf-file:
keywords = ["Title:","meshtype:", "meshunit:", 'columns',
            "xbase:", "ybase:", "zbase:",
            "xstepsize:", "ystepsize:", "zstepsize:",  
            "xnodes:", "ynodes:","znodes:",'ValueRangeMaxMag:',
            "xmin:", "ymin:", "zmin:", "xmax:", "ymax:", "zmax:"]
dic={}

def parse_for_keywords(keywords, line):
    """determines if a keyword is in a line and if so, manipulates it to
    ensure correct format"""
    for x in keywords:
        if line[0:len(x)+2] == "# "+x:
            # removes any end of line character and any leading white space
            dic[x] = line[len(x)+2:].strip()

def analyze(filename):
    """Takes a file and returns a dictionary of keyword-value pairs"""
    f = open(filename, "r")
    while 1:
        line = f.readline()
        
        # until eof
        if line[0] != "#":
            dic['columns']=len(line.strip().split())
            break
        if line[0] == "#":
            parse_for_keywords(keywords, line)
    f.close()
    return dic

def createxyz(dic):
    x_=np.arange(int(dic['xnodes:']))
    y_=np.arange(int(dic['ynodes:']))
    z_=np.arange(int(dic['znodes:']))
    #print('\nx-dircetion:{0}\ny-dircetion:{1}\nz-dircetion:{2}\n'.format(int(dic['xnodes:']),int(dic['ynodes:']),int(dic['znodes:'])))
    z,y,x=np.meshgrid(z_,y_,x_,indexing='ij')
    x=x.flatten()*float(dic['xstepsize:'])+float(dic['xbase:'])
    y=y.flatten()*float(dic['ystepsize:'])+float(dic['ybase:'])
    z=z.flatten()*float(dic['zstepsize:'])+float(dic['zbase:'])
    return x,y,z

def readtxt(fpath,ratio=1,cl=np.array([[0,1],[0,1],[0,1]]),\
          cm=np.array([[-1,1],[-1,1],[-1,1]]),D3=0,print_dict=False):
    '''main
    ratio #int,整数且大于1，模型的缩放比例。
    D3  #是否返回3D数据结构,3d结构不能去掉全为0的磁矩
    cl  #array,x,y,z坐标范围的选择，
    cm  #array,磁矩除以Ms后mx,my,mz磁矩范围的选择
    Ms  #饱和磁矩
    输入内容是文件的地址，并进行按照某种步进刷选，不包括磁矩全为0的部分。
    如果读取的是能量的话所有的参数都不会起作用。
    '''
    #分析text头部数据
    dic=analyze(fpath)
    if print_dict:
        print('\nthe dictionary of the data is')
        for i in dic:
            print(i,dic[i])
    x,y,z=createxyz(dic)

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
    #模型形状  
    model_shape=np.array([int(dic['znodes:']),int(dic['ynodes:']),int(dic['xnodes:'])])#计算形状
    #set Ms
    Ms=float(dic['ValueRangeMaxMag:'])
    if Ms!=1.0:
        mx,my,mz=mx/Ms,my/Ms,mz/Ms#normal Ms;
        
    #读取text数据
    if dic['columns']==1:#读取的text能量
        En=d[:,0]#read
        del d#delete d 
        return x,y,z,En
    if dic['columns']==3:#读取的是ovf的磁矩
        mx,my,mz=d[:,0],d[:,1],d[:,2]
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
        index=indexl*indexm*inde0#所有筛选结果求并集
        z,x,y=z[index],x[index],y[index]#筛选索引里的坐标数据
        mz,my,mx=mz[index],my[index],mx[index]#筛选索引里的磁矩数据
        return x,y,z,mx,my,mz

def read_ovf(fpath):
    '''    测试用    '''
    #########################读取格式的设置。
    clip_xyz=np.array([[0,1],[0,1],[0,1]])            #array,x,y,z坐标范围的选择，
    clip_ms=np.array([[-1,1],[-1,1],[-1,1]])         #array,磁矩除以Ms后mx,my,mz磁矩范围的选择
    ratio=1                                          #int,整数且大于1，画图时模型的缩放比例。
    print_dict=False
    #fpath=input(r"Please enter the txt file folder address\n:")
    #######################################################以下不用修改
    #ffile=[i for i in os.listdir(fpath) if i.split('.')[-1]==file_suffix]#筛选后缀是txt的文件
    #ffile=sorted(ffile,key=lambda x:int(re.search('[\d]+',x).group(0)))

    return readtxt(fpath,ratio=1,cl=clip_xyz,cm=clip_ms,D3=0,print_dict=print_dict)
    ########################################################