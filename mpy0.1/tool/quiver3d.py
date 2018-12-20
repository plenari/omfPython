# -*- coding: utf-8 -*-
#python3
"""
2018年12月20日
@author: 409200093@qq.com
画x-y-z-dx-dy-dz图片
"""

import sys  
if '..' not in sys.path:
    sys.path.append('..')
import numpy as np
import os
from mayavi import mlab
import pandas as pd
import re
from analyze import readtext 
from tool.selectSuffix import selectSuffix #筛选想要的文件名字
from tool.smove import smove  #移动生成的各类文件夹
import warnings
warnings.filterwarnings("ignore")# message="RuntimeWarning")

class quiver3D():
    '''
    三维quiver图，需要确定画图的文件夹
    '''
    def __init__(self,bgcolor=None,size=(1080,720),scale_mode='vector',
                 colormap='bwr',mode='arrow',scale_factor=1.0e-9,
                 show_outline=False,show_axes=False,show_colorbar=True,
                 show_fig=True,view=np.array([[90,180]]),gpu=False,
                 fig_format='.png',save_path=os.getcwd()):
        '''
        bgcolor:tuple,背景颜色：(1,1,1)
        size:tuple,图片大小 (1080,720)
        scale_mode:str,颜色模式：scalar/vector    
        colormap:str,'bwr','coolwarm'
        mode:str,arrow,cone,cube....
        scale_factor：float,缩放
        show_outline:bool,显示外框
        show_axes:bool,显示坐标轴
        view:array,视图
        gpu:bool
        fig_format:str,图片格式
        '''
        
        self.bgcolor=bgcolor #图片背景颜色
        self.size=size #图片大小
        self.scale_mode=scale_mode
        self.colormap=colormap
        self.mode=mode
        self.scale_factor=scale_factor
        self.show_axes=show_axes
        self.show_outline=show_outline
        self.show_colorbar=show_colorbar
        self.show_fig=show_fig
        self.view=view
        self.gpu=gpu
        self.fig_format=fig_format
        self.save_path=save_path
        
    def plot(self,x,y,z,mx,my,mz,scalars,fname,savefig=True):
        '''
        x,y,z,mx,my,mz为xyzdxdydz方式的数据
        scalars:标量数据，可能用于标记颜色
        fname:str,文件的名字
        '''
        
        figure=mlab.figure(bgcolor=self.bgcolor,size=self.size)#图片的
        
        mlab.quiver3d(x,y,z,mx,my,mz,
                      scalars=scalars,
                      colormap=self.colormap,
                      scale_mode=self.scale_mode,
                      scale_factor=self.scale_factor)
        
        if self.show_colorbar:
            mlab.colorbar(title='Mz',#color 的名字
                          orientation='vertical', #垂直方向
                          nb_labels=5, #显示五个标签
                          label_fmt='%.1f') #保留一位小数
        #坐标轴：
        if self.show_axes:
            #线宽，显示五个标签
            mlab.axes(xlabel='x',ylabel='y',zlabel='z',line_width=3.0,nb_labels=5)
            
        if self.show_outline:
            #线宽2.0 ，有一点透明
            mlab.outline(line_width=2.0,opacity=0.5)
        
        for view in self.view:
            mlab.view(view[0],view[1])#观察角度    
            if isinstance(fname,str) and isinstance(self.save_path,str) and savefig:
                print('savefig in ',self.save_path)
                if self.gpu:
                    mlab.savefig(os.path.join(self.save_path,'%s-z%d-x%d.%s'%(fname,view[0],view[1],self.fig_format)),magnification=3)
                else:
                    mlab.savefig(os.path.join(self.save_path,'%s-z%d-x%d.%s'%(fname,view[0],view[1],self.fig_format)))
    
        if self.show_fig:            
            print("Need to manually turn off the picture, will continue drawing!")
            mlab.show()#显示图片
            
        if not self.show_fig:
            mlab.close(all=True)#关闭画布    

def dealdir(fdir,name_index=-3):
    '''
    计算用文件夹分割倒数第name——index分割，
    前部分用作保存地址，后半部分用作名字前缀
    return savepath ,name_prefix
    '''
    fdir_list=fdir.split(os.sep)    
    if np.abs(name_index)>=len(fdir_list):
        '''
        如果数据不够长了，就直接返回最上一级
        '''
        name_index=1-len(fdir_list)    
    return os.sep.join(fdir_list[:len(fdir_list)+name_index]),'-'.join(fdir_list[name_index:])
    
    
def ana(fdir,name_index=-2):#总的分析
    '''
    fdir:处理一个文件，该文件下内容设置相同
    name_index:-3之后的名字都讲作为新的文件的名字
    '''
    #一些参数
    clip=np.array([[0,1],[0,1],[0,1],[-1,1],[-1,1],[-1,1]])   #array,x,y,z,mxmymz坐标范围的选择，
    
    save_path,name_prefix=dealdir(fdir,name_index)#
    
    filenames=selectSuffix(fdir,'.ovf')[1][20:22]#以.ovf结尾的文件    
    
    #初始化两个类。
    rdata=readtext.Read(os.path.join(fdir,filenames[0]))
    plt=quiver3D(save_path=save_path)
    
    for filename in filenames:
        try:
            rdata.loadData(os.path.join(fdir,filename))
            x,y,z,mx,my,mz=rdata.limit(clip)
            
        
            if len(x)>5:
                fname=name_prefix+'-'+os.path.splitext(filename)[0]
                plt.plot(x,y,z,mx,my,mz,my/2+0.5,fname)
                
        except Exception as e:
            print('{}: {}'.format(filename,e))
            
            
		 
def getdir(fdir,suffix='.dat'):
    '''
    得到所有.dat所在的文件夹地址    
    '''
    a=[]
    for roots,dirs,file in os.walk(fdir):
        for i in file:
            a.append(os.path.join(roots,i))
    a=set([os.path.split(i)[0] for i in a if os.path.splitext(i)[1]==suffix])    
    return list(a)        


if __name__=='__main__':   
    
    fdirs=input(r'输入需要处理文件的文件夹地址:')    
    dirs=getdir(fdirs,'.ovf') 
    
    for i in dirs:
        print('ana dir',i)
        ana(i)
        
   
