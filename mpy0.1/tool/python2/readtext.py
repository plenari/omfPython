# -*- coding: utf-8 -*-
#@author:shengjiex@qq.com

import sys  
if '..' not in sys.path:
    sys.path.append('..')

import numpy as np
import pandas as pd
import os
from analyze import ModelPara
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.pyplot as plt

class Read():
    '''
    初始化的数据必须和即将读取的数据具有相同的模型参数,
    有些命令将会改变数据集，返回自身
    其他命令返回计算结果（limit,slicing），不改变读取的数据集
    '''
    
    def __init__(self,fname):
        '''        
        读取一些模型参数,一次读取，接下来都要使用这个了，除非重启程序。       
        
        '''
        self.dict=ModelPara.analyze(fname)
     
    
    def loadData(self,fname) :
        '''        
        读取数据,如果数据列数，1、3、就分别加入xyz坐标， 如果有4、6列就返回
        
        fname: 文件名字
        
        把数据添加到self.data=[x,y,z,mx,my,mz]里。
        
        >>>r=Read(fname)
        
        >>>r.loadData(fname)
        
        ''' 
        assert os.path.isfile(fname)==True,'请正确输入文件名字'
        try:
            data=np.loadtxt(fname)            
        except:
            data=pd.read_table(fname,header=None,dtype=float,comment='#',delim_whitespace=True)#pandas read
            data=np.array(data)
        
        #判断是磁矩还是能量，以及是否包含坐标信息
        if self.dict['Title:']=='m':#磁矩
            if self.dict['columns']==3:#只包含磁矩数据 
                data=data/float(self.dict['ValueRangeMaxMag:'])
                data=np.hstack([self.createXYZ(),data])                    
            
            elif self.dict['columns']==6:#包含坐标数据
                data[:,3:]=data[:,3:]/float(self.dict['ValueRangeMaxMag:'])
        
        #能量
        elif self.dict['Title:']=='E':
            if self.dict['columns']==1:#只有能量数据，添加坐标
                data=np.hstack([self.createXYZ(),data])
            elif self.dict['columns']==4:#能量且包含坐标
                pass
            
        self.data=list(data.T)  
        #标记为类变量，用来保存数据
        self.fname=fname
        return self

    
    def createXYZ(self):
        '''
        对没有坐标数据的磁矩能量产生对应的坐标,如果已经有了，就不需要了。
        '''
        x_=np.arange(int(self.dict['xnodes:']))
        y_=np.arange(int(self.dict['ynodes:']))
        z_=np.arange(int(self.dict['znodes:']))        
        z,y,x=np.meshgrid(z_,y_,x_,indexing='ij')        
        x=x.flatten()*float(self.dict['xstepsize:'])+float(self.dict['xbase:'])
        y=y.flatten()*float(self.dict['ystepsize:'])+float(self.dict['ybase:'])
        z=z.flatten()*float(self.dict['zstepsize:'])+float(self.dict['zbase:'])
        
        return np.array([x,y,z]).T
    
    
    def flatten1D(self):
        '''
        把n维的数据展开成一维的
        
        >>>r=Read(fname)
        
        >>>r.loadData(fname).reshahpe3D().sumsample().flatten1D()
        
        >>>
        '''
        
        for i,values in enumerate(self.data):
            self.data[i]=values.flatten()
        return self
    
    
    def reshape3D(self,shape3D=None):
        '''
        把self.data 的每一个数据都转换3D
        shape3D=[z,y,x]
        
        >>>r=Read(fname)
        
        >>>r.loadData(fname).reshahpe3D()
        '''
        if shape3D==None:
            #计算形状
            shape3D=np.array([int(self.dict['znodes:']),int(self.dict['ynodes:']),int(self.dict['xnodes:'])])
            
        for i,values in enumerate(self.data):
            self.data[i]=values.reshape(shape3D)
        return self
    
    
    def subsample(self,rat=np.array([2,2,2])):
        '''
        重新采样的比例，就是减少样本, 在这个之前样本已经是3D的了.
        
        rat=np.array([2,2,2])  
        
        >>>r=Read(fname)
        
        >>>r.loadData(fname).reshahpe3D().subsample()
        
        >>>r.data[0].shape
        '''         
        assert len(rat)==3,'need 3 int'        
        for i,Values in enumerate(self.data):
            assert len(Values.shape)==3,'{}的维度不是三维的,需要先reshape3D'.format(i)
            
        for i,values in enumerate(self.data):
            self.data[i]=values[::int(rat[0]),::int(rat[1]),::int(rat[2])]   
            
        return self
    

    def limit(self,c=np.array([[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]])):
        '''
        在此之前数据还不是三维的。
        数据一共有六列，对每一列的限制都写好了。
        如果只有四列，那就是只要前四个。
        
        >>>r=Read(fname)
        
        >>>lim=r.loadData().limit()
        
        
        '''
        assert c.shape==(6,2),'c.shape should be 6,2'
        
        index=np.ones_like(self.data[0]).astype(bool)
        for i,values in enumerate(self.data):
            #对每一个筛选进行叠加
            index=index & (values>c[i][0]) & (values<c[i][1])
            
        if len(self.data)==6:
            #筛选磁矩非零数据            
            indexm=((np.fabs(self.data[3])+np.fabs(self.data[4])+np.fabs(self.data[5]))!=0.0)#非零筛选结果。
            index=index & indexm
        lim=[]
        for i,values in enumerate(self.data):
            lim.append(values[index])
        
        return lim
    
    
    def _slicing(self,data,loc,plane):
        '''
        切片,数据首先的3D
        '''
        if plane=='xy':
            slice_data=data[loc]
        elif plane=='yz':
            slice_data=data[:,:,loc].T
        elif plane=='zx':
            slice_data=data[:,loc,:]
        return slice_data
                   
    def slicing(self,loc,plane='xy',saveNpz=False):
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
               
        >>>r=Read(fname)
        
        >>> sl=r.loadData(fname).reshape3D().slicing(5,'xy')
        
        '''
        data_=[]
        for i,values in enumerate(self.data):
            data_.append(self._slicing(values,loc,plane))
        return data_
    
    
    def saveNpz(self,data,flag='-'):
        '''
        把数据保存到npz，不限制形状
        
        >>>r=Read(fname)
        
        >>>r.loadData()
        
        >>>r.saveNpz(r.data,flag='test')
        '''       
        fnpz=self.fname.replace(os.path.splitext(self.fname)[-1],flag+'.npz')
        np.savez(fnpz, data=data)
        return True
    
    def loadNpz(self,fname):
        '''
        从npz下载数据，保存到self.data里,最好知道
        
        >>>r=Read(fname)        
        >>>r.loadNpz(fname)
        
        '''
        self.data=np.load(fname)['data']
        self.fname=fname
        
        
    def saveExcel(self,data,flag='-'):
        '''
        把数据写入到Excel,每一个数据都必须是二维的 
        
        >>>r=Read(fname)
        
        >>>sl=r.loadData(fname).reshape3D().slicing(5)
        
        >>>r.saveExcel(sl,flag='test')
        
        '''
        assert isinstance(data,list),'保存的数据必须的列表形式'
        for i in data:
            assert len(i.shape)==2,'保存的数据必须是二维结构'
        
        fExcel=self.fname.replace(os.path.splitext(self.fname)[-1],flag+'.xlsx')
        writer=pd.ExcelWriter(fExcel)
        for i,Values in enumerate(data):
            pd.DataFrame(Values).to_excel(writer,sheet_name=str(i))
        writer.save()  
        
    def loadExcel(self,fname):
        '''
        把保存到excel里的数据在下载到self.data里面
        
        >>>r=Read(fname)
        >>>r.loadExcel(fname)
        '''
        dicts=pd.read_excel(fname,sheet_name=None)
        data=[]
        for i in range(len(dicts)):
            data.append(dicts[str(i)].values)
        self.data=data
        self.fname=fname
        
    def calQ(self,data):
        '''
        data=[x,y,mx,my,mz]， x是二维数据，可以通过slicing函数得到数据。
        
        计算二维数据的拓扑数，分别为对应的坐标和磁矩        
        Q=sum(m*(dm(x)Xdm(y))*dx*dy)/(4*pi)
        叉乘
        i,j,k
        x,y,z
        a,b,c
        叉乘结果=[yc-bz,az-xc,xb-ay]
        
        >>>r=Read(fname)
        
        >>>sl=r.loadData(fname).reshape3D().slicing(5)
        
        >>>xydensity,Q=r.calQ([sl[0],sl[1],sl[3],sl[4],sl[5]])
        
        '''    
        assert len(data)==5,'wrong'
        for i in data:
            assert len(i.shape)==2,'wrong'        
        
        x,y,mx,my,mz=data[0],data[1],data[2],data[3],data[4]
        
        def dt(m,axis=0):
            '''对x求导 axis=1,对y求导axis=0'''
            if axis==0:return np.diff(m,axis=axis)[:,:-1]
            elif axis==1:return np.diff(m,axis=axis)[:-1,:]
            
        def cross(v1,v2):
            '''叉乘，规律如上'''
            assert len(v1)==len(v2)==3,'wrong'
            return [v1[1]*v2[2]-v1[2]*v2[1],v1[2]*v2[0]-v1[0]*v2[2],v1[0]*v2[1]-v1[1]*v2[0]]
        dx=dt(x,1)
        dy=dt(y,0)
        #偏导数
        dmdx=[dt(mx,1)/dx,dt(my,1)/dx,dt(mz,1)/dx]
        dmdy=[dt(mx,0)/dy,dt(my,0)/dy,dt(mz,0)/dy]
        #叉乘
        dmdxdy=cross(dmdx,dmdy)
        #对应相乘
        dmdxdy_m=dmdxdy[0]*mx[:-1,:-1]+dmdxdy[1]*my[:-1,:-1]+dmdxdy[2]*mz[:-1,:-1]
        #相乘得到密度
        dmdxdy_m_dxdy=dmdxdy_m*dx*dy    
        result=[x,y,dmdxdy_m_dxdy]
        
        return result,dmdxdy_m_dxdy.sum(axis=None)/4/np.pi  

    
    def saveExcel2Image(self,data,flag='-xyzmxmymz',row=2,suffix='.png'):
        '''
        data:list数据,与保存到Excel里的一致
        row:设置多少行,列自动计算。
        也将保存到self.fname中去
        格式是：png
        >>>
        '''
        assert isinstance(data,list),'保存的数据必须的列表形式'
        for i in data:
            assert len(i.shape)==2,'保存的数据必须是二维结构'

        col=len(data)//row+len(data)%row
        fig, axs = plt.subplots(row,col,figsize=[25,5])
        axs=axs.flatten()
        for i,values in enumerate(data):
            im=axs[i].imshow(values)
            axs[i].set_xlabel('label'+str(i))  
            
            axins = inset_axes(axs[i],
                           width="4%", 
                           height="100%",
                           loc='lower right',
                           )
            
            plt.colorbar(im,cax=axins,)
        figname=self.fname.replace(os.path.splitext(self.fname)[-1],flag+suffix)
        plt.savefig(figname)
        plt.close()
