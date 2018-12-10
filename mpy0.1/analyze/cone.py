# -*- coding: utf-8 -*-
#author:shengjiex@qq.com
'''
处理圆台数据

[1]
>>>读取数据
[2]
>>>沿着x方向切割，且每一个切割数据，
    计算圆心，限制距离，按角度排序
>>> 将上述数据铺平成平面
[3]
>>>计算y方向距离，计算当层的拓扑数，保存当层的excel，图片。
[4]
>>>计算数据中斯格明子的大小，保存拟合数据，
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
from analyze import curl# 
from tool.selectSuffix import selectSuffix #筛选想要的文件名字
from tool.smove import smove  #移动生成的各类文件夹
from analyze.fit import Fit


class Cone(curl.Curl):
    
    def __init__(self,fname):
        '''        
        读取一些模型参数,一次读取，接下来都要使用这个了，除非重启程序。       
        
        '''
        super(Cone,self).__init__(fname)
    def xyz2xy(self,data):
        '''
        data=[x,y,z]
        
        将y,z方向在y方向距离计算一下
        '''
        x,y,z=data
        tempy=np.zeros_like(x)
         
        tempy[1:]=np.sqrt(np.diff(y,axis=0)**2+np.diff(y,axis=0)**2)
        tempy[np.isnan(tempy)]=0.0
        tempy=tempy.cumsum(axis=0)
        tempy[np.isnan(x)]=np.nan
        return x,tempy
    
    def calQCone(self,data):
        '''
        data=[x,y,mx,my,mz]
        '''
        xydensity,Q = self.calQ(data)
        middle=xydensity[2].shape[0]//2
        up=xydensity[2][:middle]
        down=xydensity[2][-middle:]
        up=up[~np.isnan(up)].sum(axis=None)
        down=down[~np.isnan(down)].sum(axis=None)
        return xydensity,(up-down)/4/np.pi
         
def coneSlicing(data,rclip=[0,2e-9]):
    '''
    all in one
    对每一个x轴上的切片应用距离限制
    最后得到一个大列表   
    
    data: r.data
    '''
    
    assert len(data)==6,'xyz,mxmymz'
    assert len(data[0].shape)==3,'三维数据'
    clipData=[]
    
    #对x循环    
    for i in range(data[0].shape[2]):
        slic=[v[:,:,i] for v in data]
        
        M0=np.sqrt(slic[3]**2+slic[4]**2+slic[5]**2)>0
        #至少得有五个数据把
        if np.sum(M0,axis=None)>5:
            slici=selectRclip(slic,rclip)
            clipData.append(slici)
    return pave(clipData)        
    
def pave(data):
    '''
    铺平数据成二维的。
    以那条线为基准铺平数据将会导致很多不同的效果。
    data:[x,y,z,mx,my,mz] ,二维的，不规则的二维数据
    return :[x,y,z,mx,my,mz]，二维的
    '''
    assert len(data[0])==6,'每一个都是六个数据，且每个数据长度一样'
    #新数组的大小    
    len_index=np.max([len(i[0]) for i in data])
    len_col=len(data)
    
    plane=[]

    for xyz in range(6):
        '''
        对变量进行循环
        '''
        planei=np.zeros([len_index,len_col])
        planei[:,:]=np.nan
        for i,v in enumerate(data):
            '''
            对每一个x轴数据循环
            将数据的中心对准数组的中心
            '''
            youself=v[xyz].shape[0]#第几个切片的xyz变量，的长度
            start=getPaveIndex(youself,lens=170)
            planei[start:start+youself,i]=v[xyz]
        plane.append(planei)
    return plane

def getPaveIndex(youself,lens=170):
    '''
    你的长度比如是50，那么放入170个格的数据中，需要放置的起始点在哪里呢？
    '''
    assert lens>=youself,'数据必须足够大'
    return (lens-youself)//2

def selectRclip(data,rclip=[0,2e-9]):
    '''    
    对平面内的数据进行距离限制，且按照顺时针排序
    
    data：[x,y,z,mx,my,mz]，xyz为二维数据，data应为对X切片的值。
    rclip:[0,2e-9]    
    return :排序后的数据
    '''
    
    assert len(rclip)==2,'长度为2的列表'
    assert len(data[0].shape)==2,'维度为2的数据'
    assert len(set(data[0].flatten()))==1,'x方向应该是单一的'   
    
    datai=[]
    M0=np.sqrt(data[3]**2+data[4]**2+data[5]**2)>0
    for i,v in enumerate(data):
        datai.append(v[M0])
    data=datai
    # 圆环中心
    centery,centerz=data[1].mean(),data[2].mean()
    #距离圆心的距离
    ri=np.sqrt((data[1]-centery)**2+(data[2]-centerz)**2)
    rMax=ri.max()
    selectri=(ri>(rMax-np.max(rclip))) & (ri<(rMax-np.min(rclip)))
    
    for i,v in enumerate(data):
        data[i]=v[selectri]
    #排序
    index=sortByTheta(data[1:3],[centery,centerz])    
    for i,v in enumerate(data):
        data[i]=v[index]
    return data
    
def sortByTheta(data,center):
    '''
    
    排序，与Y轴正向夹角的顺时针
    data:y,z 返回值
    center:[centerx=y,centerz]  
    return [sorted(y),sorted(z)]
    '''
    
    #减去平均值可以方便的得到以圆柱为中心的
    cy=data[0]-center[0]
    cz=data[1]-center[1]
    #用arccos函数计算每一点与y轴正向的夹角
    thetaY=np.arccos(cy/np.sqrt(cy**2+cz**2))
    thetaY[cz<0]=2*np.pi-thetaY[cz<0]
    #从小到大的排列方式的位置索引。这个索引的作用对象是已经用距离筛选过的数据
    index_thetaY=np.argsort(thetaY)
    #return [data[0][index_thetaY],data[1][index_thetaY]]
    return index_thetaY




if __name__=='__main__':
    fdir=input('输入需要处理文件的文件夹地址:')    
    #fdir=r'C:\Users\omf\Desktop\mpy1.0\test'
    filenames=selectSuffix(fdir,'.ovf')[1][0:]#前三百个以.ovf结尾的文件
    maxSkyr=4#处理过程中最多有多少个斯个明子
    rclip=[0,2e-9]#每一个x处，从最外层往里距离限制。
    #初始化两个类。
    r=Cone(os.path.join(fdir,filenames[0]))
    f=Fit(fdir,maxSkyr=maxSkyr)
    QDF=pd.DataFrame(columns=['Q'])
    
    for filename in filenames:
        
        r.loadData(os.path.join(fdir,filename)).reshape3D()
        
        sl=coneSlicing(r.data,rclip)
        ##        
        
        r.saveExcel(sl,flag='-xy-r-mxyz')
        #并将Excel的数据画图
        r.saveExcel2Image(sl,flag='-xy-r-mxyz')
        #
        x,y=r.xyz2xy(sl[:3])
        #计算拓扑数        
        xydensity,Q = r.calQCone([x,y,sl[3],sl[4],sl[5]])
        Q=np.sum(xydensity[2][xydensity[2]>0])/4/np.pi
        QDF.loc[filename,'Q']=Q
        
        #保存拓扑密度,并画图        
        r.saveExcel(xydensity,flag='-xy-r-density')
        r.saveExcel2Image(xydensity,flag='-xy-r-density')
        #计算位置,画出斯格明子边界和拟合值，保存计算出的边界
        try:
            f.fit([x,y,sl[5]],Q,index=filename,plots=True,sign=np.sign(Q),\
                  plotsFlag='skyrmionEdge-fit',saveNewxy=True,saveNewxyFlag='newXY')
        except Exception as e:
            print(filename,':\t',e)
        print('filename:{} is done! '.format(filename))
    f.DF.to_excel(os.path.join(f.savedir,'circle-ellipse.xlsx'))
    QDF.to_excel(os.path.join(fdir,'Q.xlsx'))
    
    
    #移动指定文件到文件夹
    smove('.xlsx','xy-r-mxyz-excel',fdir,flag='-xy-r-mxyz')
    smove('.png','xy-r-mxyz-png',fdir,flag='-xy-r-mxyz')
    smove('.xlsx','xy-r-density-excel',fdir,flag='xy-r-density')
    #移动fdir里的文件名字里包含flag的png图片到xy-r-density-png里。
    smove('.png','xy-r-density-png',fdir,flag='xy-r-density')
    #移动拟合后的数据
    smove('.png','skyrmionEdge-fit',fdir,flag='skyrmionEdge-fit')
    smove('.xlsx','newXY',fdir,flag='newXY')
        

