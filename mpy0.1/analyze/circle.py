# -*- coding: utf-8 -*-

import numpy as np
import os
import math
def circle(x,y):
    '''
    #最小二乘法,拟合圆形
    返回的是直径，x,y的圆心。
    
    Example:
        
    >>>y=[0,-1,0,1]
    >>>x=[0,1,2,1]
    >>>circle(x,y)
    (2.0, 1.0, 0.0)
    '''
    if len(x)==0:
        return 0,0,0
    x1,x2,x3,y1,y2,y3=0.,0.,0.,0.,0.,0.
    x1y1,x1y2,x2y1=0.,0.,0.
    N=len(x)
    for i in range(N):
        x1=x1+x[i]
        x2=x2+x[i]**2
        x3=x3+x[i]**3
        y1=y1+y[i]
        y2=y2+y[i]**2
        y3=y3+y[i]**3
        x1y1=x1y1+x[i]*y[i]
        x1y2=x1y2+x[i]*y[i]*y[i]
        x2y1=x2y1+x[i]*x[i]*y[i]
    C=N*x2-x1**2
    D=N*x1y1-x1*y1
    E=N*x3+N*x1y2-(x2+y2)*x1
    G=N*y2-y1**2
    H=N*x2y1+N*y3-(x2+y2)*y1
    a=(H*D-E*G)/(C*G-D*D)
    b=(H*C-E*D)/(D*D-G*C)
    c=-(a*x1+b*y1+x2+y2)/N
    A=-a/2
    B=-b/2
    D=math.sqrt(a**2+b**2-4*c)
    return D,A,B