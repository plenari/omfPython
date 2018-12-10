# -*- coding: utf-8 -*-
#@author:shengjiex@qq.com

import sys  
if '..' not in sys.path:
    sys.path.append('..')
from analyze import nanotube,circle

import numpy as np
import pandas as pd
import os
from tool.selectSuffix import selectSuffix #筛选想要的文件名字
from tool.smove import smove  #移动生成的各类文件夹
from analyze.fit import Fit

class Curl(nanotube.Nanotube):
    '''
    初始化的数据必须和即将读取的数据具有相同的模型参数,
    有些命令将会改变数据集，返回自身
    其他命令返回计算结果（limit,slicing），不改变读取的数据集
    '''
    
    def __init__(self,fname):
        '''        
        读取一些模型参数,一次读取，接下来都要使用这个了，除非重启程序。       
        
        '''
        super(Curl,self).__init__(fname)
        

    def curlSlicing(self,rclip=[0,1]):
        '''
        reshape3D
        '''
        x,y,z=self.data[0],self.data[1],self.data[2]
        mx,my,mz=self.data[3],self.data[4],self.data[5]      
        
        self.center=self.getCenter(y[:,:,0],z[:,:,0],mx[:,:,0],my[:,:,0],mz[:,:,0])
        return self.circleSlicing(rclip=rclip,center=self.center)
        
    def getEdge(self,mx,my,mz,direction='down'):
        '''
        #请注意，与实际使用的坐标是反着的
        
        mx,my,mz:二维数组，在X方向的一个切片。
        比如X=1e-9nm时按照位置排列的
        loc=up,left,right,down
        up_left=True,就是选择上边或者左边的数据，
        其中一个可能是这样的，
        0 0 0 1 2 3 0 0 0 
        0 0 1 2 3 4 5 6 0
        0 0 0 4 5 6 0 0 0
        上边就是第一行112356; 下边就是145656  ; 
        左边就是114 ;         右边就是366;    
        return ,返回坐标 
        
        >>> m=np.array([[ 0, 0, 0, 1, 2, 3, 0, 0, 0], 
        [0, 0, 1, 2, 3, 4, 5, 6, 0],
        [0, 0, 0, 4, 5, 6, 0, 0, 0]])
        
        >>> getEdge(m,m,m,'up')
        >>> (array([1, 0, 0, 0, 1, 1], dtype=int64),
     array([2, 3, 4, 5, 6, 7], dtype=int64))
        '''    
        
        m=(mx**2+my**2+mz**2)
        x,y=np.where(m>0.0)
        assert len(mx.shape)==len(my.shape)==len(mz.shape)==2,'三个磁矩维度需要相同,且为2'
        
        loc=[]
        if direction=='right':
            '''
            模型右侧
            '''
            for xi in np.unique(x):

                yi=np.max(y[x==xi])
                loc.append([xi,yi])
                
        if direction=='left':
            '''
            模型左侧
            '''
            for xi in np.unique(x):
                yi=np.min(y[x==xi])
                loc.append([xi,yi])
               
        if direction=='up':
            '''
            与模型的仰视图一样
            '''
            for yi in np.unique(y):
                xi=np.min(x[y==yi])
                loc.append([xi,yi]) 
        if direction=='down':
            '''
            与模型的俯视图一样，
            '''
            for yi in np.unique(y):
                xi=np.max(x[y==yi])
                loc.append([xi,yi])  
        loc=np.array(loc) 
        return loc[:,0],loc[:,1] 
    
    def getCenter(self,y,z,mx,my,mz,direction='down'):
        '''
        计算圆弧的圆心
        
        '''
        location=self.getEdge(mx,my,mz,direction=direction)
        circley,circlez=y[location],z[location]
        dia,centery,centerz=circle.circle(circley,circlez)
        return [centery,centerz]
                      
    def calQC(self,data):
        '''
        data=[x,y,z,mx,my,mz]， x是二维数据，可以通过slicing函数得到数据。
        x,y是距离，z是原来的z
        '''
        
        x,y,mx,my,mz,z=data[0],data[1],data[3],data[4],data[5],data[2]
        sha=x.shape[1]
        index = z>self.center[1]
        x,y,mx,my,mz,z=x[index],y[index],mx[index],my[index],mz[index],z[index]
        xydensity,Q=self.calQ([x.reshape(-1,sha),y.reshape(-1,sha),mx.reshape(-1,sha),\
                               my.reshape(-1,sha),mz.reshape(-1,sha)])
        return xydensity,Q
    
    
        
def test():
    fname=r'K:\模拟结果\曲率半径大于80的弯曲曲面\arc-Hz-R100\m000490.ovf'
    r=Curl(fname)
    r.loadData(fname)
    csl=r.reshape3D().curlSlicing(rclip=[92e-9,94e-9])    
    x,y=r.xyz2xy(csl[:3])      
    xydensity,Q=r.calQC([x,y,csl[2],csl[3],csl[4],csl[5]])    
    
if __name__=='__main__':    
    
    #fdir=input('输入需要处理文件的文件夹地址:')    
    fdir=r'K:\模拟结果\曲率半径大于80的弯曲曲面\arc-Hz-R100'
    filenames=selectSuffix(fdir,'.ovf')[1][:]#前三百个以.ovf结尾的文件
    maxSkyr=5#处理过程中最多有多少个斯个明子
    
    #初始化两个类。
    r=Curl(os.path.join(fdir,filenames[0]))
    f=Fit(fdir,maxSkyr=maxSkyr)
    QDF=pd.DataFrame(columns=['Q'])
    
    for filename in filenames:
        
        r.loadData(os.path.join(fdir,filename))
        #剪切一层,并保存到excel
        sl=r.reshape3D().curlSlicing(rclip=[98e-9,100e-9])        

        r.saveExcel(sl,flag='-xy-r98-mxyz')
        #并将Excel的数据画图
        r.saveExcel2Image(sl,flag='-xy-r98-mxyz')
        #计算拓扑数
        x,y=r.xyz2xy(sl[:3])#纳米管使用
        xydensity,Q = r.calQC([x,y,sl[2],sl[3],sl[4],sl[5]])
        QDF.loc[filename,'Q']=Q
        #保存拓扑密度,并画图
        r.saveExcel(xydensity,flag='-xy-r98-density')
        r.saveExcel2Image(xydensity,flag='-xy-r98-density')
        #计算位置,画出斯格明子边界和拟合值，保存计算出的边界
        f.fit([x,y,sl[5]],Q,index=filename,plots=True,sign=-np.sign(Q),\
              plotsFlag='skyrmionEdge-fit',saveNewxy=True,saveNewxyFlag='newXY')
        
        print('filename:{} is done! '.format(filename))
    f.DF.to_excel(os.path.join(f.savedir,'circle-ellipse.xlsx'))
    QDF.to_excel(os.path.join(fdir,'Q.xlsx'))
    #移动指定文件到文件夹
    smove('.xlsx','xy-r98--mxyz-excel',fdir,flag='-xy-r98-mxyz')
    smove('.png','xy-r98--mxyz-png',fdir,flag='-xy-r98-mxyz')
    smove('.xlsx','xy-r98-density-excel',fdir,flag='xy-r98-density')
    #移动fdir里的文件名字里包含flag的png图片到xy-r98-density-png里。
    smove('.png','xy-r98-density-png',fdir,flag='xy-r98-density')
    #移动拟合后的数据
    smove('.png','skyrmionEdge-fit',fdir,flag='skyrmionEdge-fit')
    smove('.xlsx','newXY',fdir,flag='newXY')