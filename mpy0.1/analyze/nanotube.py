# -*- coding: utf-8 -*-
#@author:shengjiex@qq.com
'''
处理纳米管数据
[1]
>>>读取数据
[2]
>>>切割圆弧一层
[3]
>>>计算当层的拓扑数，保存当层的excel，图片。
[4]
>>>计算当层斯格明子的大小，保存拟合数据，
[5]
>>>将以上数据移动到以flag命名的文件夹里。

绝对路径fname fdir
只是文件名字filenames 

现在拓扑数的正负号很奇怪。
'''
import sys  
if '..' not in sys.path:
    sys.path.append('..')
    
from analyze import readtext
import numpy as np
import pandas as pd
import os
from tool.selectSuffix import selectSuffix #筛选想要的文件名字
from tool.smove import smove  #移动生成的各类文件夹
from analyze import fit


class Nanotube(readtext.Read):
    '''
    初始化的数据必须和即将读取的数据具有相同的模型参数,
    有些命令将会改变数据集，返回自身
    其他命令返回计算结果（limit,slicing），不改变读取的数据集
    '''
    
    def __init__(self,fname):
        '''        
        读取一些模型参数,一次读取，接下来都要使用这个了，除非重启程序。       
        
        '''
        super(Nanotube,self).__init__(fname)
        
    def circleSlicing(self,rclip=[0,1],center=None):
        '''
        针对纳米管实兴新的切片方式，圆形切片。就是只保留距离纳米管圆心一定距离内的磁矩和坐标
        然后按照某种方式排列。
        
        纳米管的中心沿着x轴方向，并且不同x对应的数据结构完全相同，所以我只需要计算第一个位置就可以了。
        
        Example:
            
        >>>self.loadData(fname)        
        
        >>>self.circleSlicing()
        '''
        x,y,z=self.data[0],self.data[1],self.data[2]
        mx,my,mz=self.data[3],self.data[4],self.data[5]
        #只计算x=0位置  
        y0=y[:,:,0]
        z0=z[:,:,0]
        
        #计算圆心位置
        if center==None:
            center=[y0.mean(),z0.mean()]
            
        r=np.sqrt((y0-center[0])**2+(z0-center[1])**2)#计算距离
        
        index_r=(r>min(rclip))*(r<max(rclip))  
        #减去平均值可以方便的得到以圆柱为中心的
        cy=y0[index_r]-center[0]
        cz=z0[index_r]-center[1]
        #用arccos函数计算每一点与y轴正向的夹角
        thetaY=np.arccos(cy/np.sqrt(cy**2+cz**2))
        thetaY[cz<0]=2*np.pi-thetaY[cz<0]
        #从小到大的排列方式的位置索引。这个索引的作用对象是已经用距离筛选过的数据
        index_thetaY=np.argsort(thetaY)
        
        x=x[index_r][index_thetaY]
        y=y[index_r][index_thetaY]
        z=z[index_r][index_thetaY]
        mx=mx[index_r][index_thetaY]
        my=my[index_r][index_thetaY]
        mz=mz[index_r][index_thetaY]
        
        return [x,y,z,mx,my,mz]
    
    def xyz2xy(self,xyz):
        '''
        xyz=
        把坐标系xyz变成坐标系xy
        其中新的y为yz方向的距离之和,  x不变    
        return :
            x不变，y变为y-z方向的距离,沿着0轴计算。
            
        >>>n=Nanotube(fname)
        >>>n.loadData(fname)
        >>>csl=n.reshape3D().circleSlicing(rclip=[49e-9,50e-9])
        >>>n.xyz2xy(cls[:3])
        '''
        assert len(xyz)==3,'三个元素'        
        assert xyz[0].shape==xyz[1].shape==xyz[2].shape,'维度需要相同'
        x,y,z = xyz[0],xyz[1],xyz[2]
        
        new_y=np.zeros_like(y)
        new_y[1:]=np.sqrt((y[1:]-y[:-1])**2+(z[1:]-z[:-1])**2)
        new_y=new_y.cumsum(axis=0)
        return x,new_y
    
    
    def calQN(self,data):
        '''
        data=[x,y,mx,my,mz]， x是二维数据，可以通过slicing函数得到数据。
        由于cirlceSlicing 改变了相对位置，所以需要下半部分去相反数。
        
        '''
        x,y,mx,my,mz=data[0],data[1],data[2],data[3],data[4]
        xydensity,Q=self.calQ([x,y,mx,my,mz])
        den=xydensity[2]
        cut=den.shape[0]//2
        Q=(den[:cut].sum(axis=None)-den[-cut:].sum(axis=None))/4/np.pi
        return xydensity,Q
        
def test():
    fname=r'C:\Users\omf\Desktop\mpy_new\test\m000477.ovf'
    n=Nanotube(fname)
    n.loadData(fname)
    csl=n.reshape3D().circleSlicing(rclip=[49e-9,50e-9])
    #n.saveExcel(csl,flag='circle')
    x,y=n.xyz2xy(csl[:3])
    xydensity,Q=n.calQN([x,y,csl[3],csl[4],csl[5]])
    
    

if __name__=='__main__':
    fdir=input('输入需要处理文件的文件夹地址:')    
    #fdir=r'K:\模拟结果\nanotube的模拟结果\nanotube-Hz-R40-r10.out'
    filenames=selectSuffix(fdir,'.ovf')[1][0:]#前三百个以.ovf结尾的文件
    maxSkyr=10#处理过程中最多有多少个斯个明子
    
    #初始化两个类。
    r=Nanotube(os.path.join(fdir,filenames[0]))
    f=fit.Fit(fdir,maxSkyr=maxSkyr)
    QDF=pd.DataFrame(columns=['Q'])
    
    for filename in filenames:
        
        r.loadData(os.path.join(fdir,filename))
        #剪切一层,并保存到excel
        sl=r.reshape3D().circleSlicing(rclip=[38e-9,40e-9])        
        #sl=r.reshape3D().slicing(r49=0,plane='xy')
        r.saveExcel(sl,flag='-xy-r49-mxyz')
        #并将Excel的数据画图
        r.saveExcel2Image(sl,flag='-xy-r49-mxyz')
        #计算拓扑数
        x,y=r.xyz2xy(sl[:3])#纳米管使用
        xydensity,Q = r.calQN([x,y,sl[3],sl[4],sl[5]])
        QDF.loc[filename,'Q']=Q
        #保存拓扑密度,并画图
        r.saveExcel(xydensity,flag='-xy-r49-density')
        r.saveExcel2Image(xydensity,flag='-xy-r49-density')
        #计算位置,画出斯格明子边界和拟合值，保存计算出的边界
        #f.fit([x,y,sl[5]],Q,index=filename,plots=True,sign=-np.sign(Q),\
        #     plotsFlag='skyrmionEdge-fit',saveNewxy=True,saveNewxyFlag='newXY')
        
        print('filename:{} is done! '.format(filename))
    f.DF.to_excel(os.path.join(f.savedir,'circle-ellipse.xlsx'))
    QDF.to_excel(os.path.join(fdir,'Q.xlsx'))
    #移动指定文件到文件夹
    smove('.xlsx','xy-r49--mxyz-excel',fdir,flag='-xy-r49-mxyz')
    smove('.png','xy-r49--mxyz-png',fdir,flag='-xy-r49-mxyz')
    smove('.xlsx','xy-r49-density-excel',fdir,flag='xy-r49-density')
    #移动fdir里的文件名字里包含flag的png图片到xy-r49-density-png里。
    smove('.png','xy-r49-density-png',fdir,flag='xy-r49-density')
    #移动拟合后的数据
    smove('.png','skyrmionEdge-fit',fdir,flag='skyrmionEdge-fit')
    smove('.xlsx','newXY',fdir,flag='newXY')
        

