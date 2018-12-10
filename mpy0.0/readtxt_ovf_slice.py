# -*- coding: utf-8 -*-
'''
一，如果想要选取从下到上第6层的数据，分为三种情况：
1，xy平面，既Z=5,(m[5])
2，yz平面，既X=5,(m[:,:,5].T)
3，zx平面，既Y=5,(m[:,5,:])
指定平面plane ['xy','yz','zx']之一。
指定loc=5(int)即可。

二，保存到excel里的视图是:
    #    #   #   #
#  0,0  1,0 2,0 3,0
#  1,0  1,1 2,1 3,1
其中的数字是坐标，
xy平面：第一个x，第二个y
zx平面：第一个x，第二个z
yz平面：第一个z，第二个y
三，保存的数据，一共有四类
mag is one of [mx,my,mz,E]
'''         
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

def readtxt(fpath,loc=0,mag='mx',plane='xy',ratio=1,print_dict=False,header=True,index=True,save=True):
    '''
    loc：保存平面距离底面的层数
    plane：保存的平面
    mag:保存的数据类型
    ratio:缩放比例，正整数
    '''
    #分析text头部数据
    dic=analyze(fpath)
    if print_dict:
        print('\nthe dictionary of the data is')
        for i in dic:
            print(i,dic[i])            
    rat=int(ratio)    
    #read data    
    try:
        d=np.loadtxt(fpath)#文件里有中文，会读取失败。
    except:
        d=pd.read_table(fpath,header=None,dtype=float,comment='#',delim_whitespace=True)#pandas read
        d=np.array(d)#有中文也没有问题。
    #模型形状  
    model_shape=np.array([int(dic['znodes:']),int(dic['ynodes:']),int(dic['xnodes:'])])#计算形状
        
    #读取text数据
    if mag=='E':#读取的text能量
        data=d[:,0]#read
        if dic['columns']!=1:
            print('注意保存的变量可能不是能量！！')
        del d#delete d 
        
    if mag in ['mx','my','mz']:#读取的是ovf的磁矩
        m_index={'mx':0,'my':1,'mz':2}[mag]
        Ms=float(dic['ValueRangeMaxMag:'])
        if Ms!=1.0:
            data=d[:,m_index]/Ms
        else:
            data=d[:,m_index]       
        del d#delete d 

    #改变数据的形状        
    data=data.reshape(model_shape)[::rat,::rat,::rat]
    if plane=='xy':
        slice_data=data[loc]
    if plane=='yz':
        slice_data=data[:,:,loc].T
    if plane=='zx':
        slice_data=data[:,loc,:]
    save_path=fpath.replace('.ovf','-'+plane+str(loc)+'-'+mag+'.xlsx')
    if save:
        pd.DataFrame(slice_data).to_excel(save_path,header=header,index=index)        
    return slice_data

if __name__=='__main__':
    #########################读取格式的设置。
    ratio=1                                          #int,整数且大于1，模型的缩放比例。
    print_dict=False
    loc=5
    plane='yz'#['xy','yz','zx']
    mag='mz'
    #####保存到excel的设置################################
    save=True#保存到excel
    header=True#Write row names (columns)|||true or  False
    index=True#Write row names (index)||||true or False
    ########################################################
    print('''当前使用的参数是：\n1,plane:{}\n2,loc:{}\n3,mag:{}\n4,save:{}'''.\
          format(plane,loc,mag,save))
    fpath=input(r"Please enter the txt file folder address:")

    #######x################################################以下不用修改
    ffile=[i for i in os.listdir(fpath) if i.split('.')[-1]=='ovf']#筛选后缀是txt的文件
    try:
        ffile=sorted(ffile,key=lambda x:int(re.search('[\d]+',x).group(0)))
    except:
        pass
    for i in ffile:
        readtxt(os.path.join(fpath,i),loc=loc,mag=mag,plane=plane,ratio=ratio,\
                print_dict=print_dict,header=header,index=index)
        print('{} is done'.format(i))
    ########################################################
    