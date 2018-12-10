# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from sympy.solvers import solve
import os
from sympy import Symbol

def solve_tuoyuan(x,y):
    '''
    x，y椭圆拟合的坐标
    return 下一个方程中的abcdef
    #a*x**2 + b*x*y + c*y**2 + d*x + e*y + f
    
    '''
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
    '''
    paras:    下一个方程中的abcdef
    #a*x**2 + b*x*y + c*y**2 + d*x + e*y + f
    return  :下一个方程中的abx0y0
    (x-x0)**2/a**2+(y-y0)**2/b**2=1
    '''
    
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
    return a,b,x0,y0,q

def tuoyuan(y,x,p):
    '''
    解方程使用
    '''    
    return p[0]*x**2+p[1]*x*y+p[2]*y**2+p[3]*x + p[4]*y + p[5]

def cal_fit_data(p,normal,x):
    '''
    p:solve_tuoyuan返回的值
    normal：normal_style返回的值
    x:自变量
    '''
    #print('计算拟合后的数据.....')    
    rx,ry=[],[]
    y=Symbol('y')
    for i in x:
        yi=solve(tuoyuan(y,i,p),y)
        for ind,v in enumerate(yi):
            if 'I' not in str(v):
                rx.append(i)
                ry.append(v)
    return rx,ry

def plots(x,y,fits,fname):
    '''
    ??
    '''
    fig=plt.figure()
    ax=fig.add_subplot(111)
    ax.plot(x,y,'b*',label='origin')    
    ax.plot(fits[0],fits[1],'r.',label='fits')
    plt.show()
    fig.savefig(fname.replace('.txt','.png'))
    
    
    
def fit_ellipse(x,y):
    '''
    ???
    '''    
    paras=solve_tuoyuan(x,y)
    normal=normal_style(paras)
    fits=cal_fit_data(paras,normal)
  
