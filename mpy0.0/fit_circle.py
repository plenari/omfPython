# -*- coding: utf-8 -*-
'''
计算excel文件里铁磁斯格明子的直径，只能含有一个斯格明子
>>>main(path,length=[0,1000],step=2e-9,name='M%d.xlsx',dname=3):
>>>length[start,stop],
>>>这个只能处理方格的情况，每隔格子的长度为step
>>>dname:希望用输入路径中倒数第几个来命名结果，比如:
>>>D:\\relax700\\relax250Hz700\\txt\\excel,倒数第三个，所以dname=3
>>>step，保存到excel的直径将乘以这个数字
>>>name，文件的格式，数字用%d代替。
'''
import pandas as pd
import numpy as np
import math
import os

def circle(x,y):#拟合圆形,最小二乘法
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

def main(pdir,pfiles,step=2e-9,dname=3,save=True,save_path=None):
    indexs,D,A,B=[],[],[],[]   
    for i in pfiles:
        x,y=getxy(os.path.join(pdir,i))
        d,a,b=circle(x,y)
        D.append(d*step)
        A.append(a*step)
        B.append(b*step)
        indexs.append(i)
        print(i,d)
    re=np.array([D,A,B])
    name=pdir.split(os.sep)[-dname]
    result1=pd.DataFrame(re.T,columns=['Dia','X','Y'],index=indexs)
    if save==True:
        result1.to_excel(os.path.join(save_path,'Position-%s.xlsx'%name))
    return result1

def getxy(path):
    '''
    输入数据的列是x轴,行是y轴.
    '''
    data=np.array(pd.read_excel(path))
    data_mul=data[:,:-1]*data[:,1:]
    loc=np.where(data_mul<0)
    locx,locy=loc[1],loc[0]#分别是第几列x,第几行y
    m0,m1=data[loc],data[locy,locx+1]#
    calx=(-m0)/(m1-m0)+locx
    return calx,locy

if __name__=='__main__':
    #如果需要更改数据，都在下边这行更改，在上边更改无效。
    step=2e-9       #cellsize
    dname=1           #用倒数第三个名字命名新的excel    
    pdir=input(r'请输入计算直径excel所在的文件夹:')
    pfiles=[i for i in os.listdir(pdir) if i.split('.')[-1]=='xlsx']
    pfiles=sorted(pfiles)
    ###########以下不需要更改
    name=pdir.split(os.sep)[-dname]#
    save_path=pdir.split(pdir.split(os.sep)[-dname])[0]    
    
    print('''当前使用的参数如下：\n1,计算文件夹：{}
\n2,cellsize:{}\n3,excel名字：{}\n4,保存路径：{}'''.format(pdir,step,name,save_path))
    main(pdir,pfiles,step=step,dname=dname,save_path=save_path)
    