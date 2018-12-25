# -*- coding: utf-8 -*-
#author:shengjiex@qq.com
'''
处理平面数据。
[1]
>>>读取数据
[2]
>>>切割一层
[3]
>>>计算当层的拓扑数，保存当层的excel，图片。
[4]
>>>计算当层斯格明子的大小，保存拟合数据，
[5]
>>>将以上数据移动到以flag命名的文件夹里。
'''

'''
绝对路径fname fdir
只是文件名字filenames 
'''
import sys  
if '..' not in sys.path:
    sys.path.append('..')

import numpy as np
import pandas as pd
import os
from analyze import readtext# 
from tool.selectSuffix import selectSuffix #筛选想要的文件名字
from tool.smove import smove  #移动生成的各类文件夹
from analyze.fit import Fit




if __name__=='__main__':
    fdir=input('输入需要处理文件的文件夹地址:')    
    #fdir=r'K:\模拟结果\曲率半径大于80的弯曲曲面\rectangle-Hz'
    filenames=selectSuffix(fdir,'.ovf')[1][124:]#前三百个以.ovf结尾的文件
    maxSkyr=4#处理过程中最多有多少个斯个明子
    
    #初始化两个类。
    r=readtext.Read(os.path.join(fdir,filenames[0]))
    f=Fit(fdir,maxSkyr=maxSkyr)
    QDF=pd.DataFrame(columns=['Q'])
    
    for filename in filenames:
        
        r.loadData(os.path.join(fdir,filename))
        #csl=r.reshape3D().circleSlicing(rclip=[49e-9,50e-9])
        #剪切一层,并保存到excel
        sl=r.reshape3D().slicing(loc=0,plane='xy')
        r.saveExcel(sl,flag='-xy-loc0-mxyz')
        #并将Excel的数据画图
        r.saveExcel2Image(sl,flag='-xy-loc0-mxyz')
        #计算拓扑数        
        xydensity,Q = r.calQ([sl[0],sl[1],sl[3],sl[4],sl[5]])
        QDF.loc[filename,'Q']=Q
        #保存拓扑密度,并画图
        r.saveExcel(xydensity,flag='-xy-loc0-density')
        r.saveExcel2Image(xydensity,flag='-xy-loc0-density')
        #计算位置,画出斯格明子边界和拟合值，保存计算出的边界
        f.fit([sl[0],sl[1],sl[5]],Q,index=filename,plots=True,sign=np.sign(Q),\
              plotsFlag='skyrmionEdge-fit',saveNewxy=True,saveNewxyFlag='newXY')
        
        print('filename:{} is done! '.format(filename))
    f.DF.to_excel(os.path.join(f.savedir,'circle-ellipse.xlsx'))
    QDF.to_excel(os.path.join(fdir,'Q.xlsx'))
    #移动指定文件到文件夹
    smove('.xlsx','xy-loc--mxyz-excel',fdir,flag='-xy-loc0-mxyz')
    smove('.png','xy-loc--mxyz-png',fdir,flag='-xy-loc0-mxyz')
    smove('.xlsx','xy-loc0-density-excel',fdir,flag='xy-loc0-density')
    #移动fdir里的文件名字里包含flag的png图片到xy-loc0-density-png里。
    smove('.png','xy-loc0-density-png',fdir,flag='xy-loc0-density')
    #移动拟合后的数据
    smove('.png','skyrmionEdge-fit',fdir,flag='skyrmionEdge-fit')
    smove('.xlsx','newXY',fdir,flag='newXY')
        

