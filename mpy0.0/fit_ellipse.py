# -*- coding: utf-8 -*-
'''
从txt中读取数据，并截取其中一层。并根据正负相交的位置
计算坐标。用这些坐标拟合成椭圆。
保存拟合后的图片。
保存椭圆的中心，长短轴，以及倾角。
需要注意的是：计算出来的位置可能会有比例尺或者其他问题，
找好与自己坐标系的对应关系。
'''
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from sympy.solvers import solve
from sympy import Symbol
from readtxt_omf_slice import readtxt
import os

def getxy(data):
    '''
    输入数据的列是x轴,行是y轴.
    '''    
    data_mul=data[:,:-1]*data[:,1:]
    loc=np.where(data_mul<0)
    locx,locy=loc[1],loc[0]#分别是第几列x,第几行y
    m0,m1=data[loc],data[locy,locx+1]#
    calx=(-m0)/(m1-m0)+locx
    return calx,locy

def solve_tuoyuan(x,y):
    #a*x**2 + b*x*y + c*y**2 + d*x + e*y + f
    print('拟合......')
    x0,y0 = x.mean(),y.mean()      
    D1=np.array([(x-x0)**2,(x-x0)*(y-y0),(y-y0)**2]).T
    D2=np.array([x-x0,y-y0,np.ones(y.shape)]).T
    S1=np.dot(D1.T,D1)
    S2=np.dot(D1.T,D2)
    S3=np.dot(D2.T,D2)    
    T=-1*np.dot(np.linalg.inv(S3),S2.T)
    M=S1+np.dot(S2,T)
    M=np.array([M[2]/2,-M[1],M[0]/2])
    lam,eigen=np.linalg.eig(M)
    cond=4*eigen[0]*eigen[2]-eigen[1]**2
    A1=eigen[:,cond>0] 
    A=np.vstack([A1,np.dot(T,A1)]).flatten()
    A3=A[3]-2*A[0]*x0-A[1]*y0
    A4=A[4]-2*A[2]*y0-A[1]*x0
    A5=A[5]+A[0]*x0**2+A[2]*y0**2+A[1]*x0*y0-A[3]*x0-A[4]*y0
    A[3]=A3;A[4]=A4;A[5]=A5
    return A

def normal_style(paras):
    print('计算标准椭圆位置.....')
    #solve_tuoyuan.return A
    paras=paras/paras[5]
    A,B,C,D,E=paras[:5]
    #椭圆中心    
    x0=(B*E-2*C*D)/(4*A*C-B**2)
    y0=(B*D-2*A*E)/(4*A*C-B**2)
    #长短轴
    a= 2*np.sqrt((2*A*(x0**2)+2*C*(y0**2)+2*B*x0*y0-2)/(A+C+np.sqrt(((A-C)**2+B**2))))
    b= 2*np.sqrt((2*A*(x0**2)+2*C*(y0**2)+2*B*x0*y0-2)/(A+C-np.sqrt(((A-C)**2+B**2))))
    #长轴倾角
    q=0.5 * np.arctan(B/(A-C))
    #normal_style
    return x0,y0,a,b,q

def tuoyuan(y,x,p):
    #用来计算
    return p[0]*x**2+p[1]*x*y+p[2]*y**2+p[3]*x + p[4]*y + p[5]

def cal_fit_data(p,normal):
    print('计算拟合后的数据.....')
    ##,solve_tuoyuan,P
    ##normal_style,
    x=np.linspace(normal[0]-normal[2]/2,normal[0]+normal[2]/2,100)
    rx,ry=[],[]
    y=Symbol('y')
    for i in x:
        yi=solve(tuoyuan(y,i,p),y)
        if  'I' not in str(yi[0]):
            rx.append(i)
            ry.append(yi[0])
        if 'I' not in str(yi[1]):
            rx.append(i)
            ry.append(yi[1])
    return rx,ry
    

def plots(x,y,fits,pfile):
    fig=plt.figure()
    ax=fig.add_subplot(111)
    ax.plot(x,y,'b*',label='origin')    
    ax.plot(fits[0],fits[1],'r.',label='fits')
    plt.show()
    fig.savefig(pfile.replace('.txt','.png'))

if __name__=='__main__':
    pdir=input(r'输入需要拟合椭圆的文件夹：')
    result=pd.DataFrame(columns=['x0','y0','a','b','q'])
    pfiles=os.listdir(pdir)
    for i,name in enumerate(pfiles):
        
        print('开始处理{}'.format(i))
        if os.path.isfile(os.path.join(pdir,'M{}.txt'.format(i))):
            pfile=os.path.join(pdir,'M{}.txt'.format(i))
            datas=readtxt(pfile,mag='mz',save=False)
        else:
            pfile=os.path.join(pdir,pfiles[i])
            datas=readtxt(pfile,mag='mz',save=False)
          
        loc=np.where(datas<0)
        locx,locy=loc[1],loc[0]#分别是第几列x,第几行y
        if len(locx)<3:
            print('there no ',i)
            continue  
        a,b=getxy(datas)  
        paras=solve_tuoyuan(a,b)
        normal=normal_style(paras)
        fits=cal_fit_data(paras,normal)
        plots(a,b,fits,pfile)
        result.loc[name]=np.array(normal)
    result.to_excel(os.path.join(pdir,'ellipse.xlsx'))
    
    