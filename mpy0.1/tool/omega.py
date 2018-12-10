#encoding=utf-8
'''
1. 有一个 excel，有两列，X,Y分别代表位置
2. main(path,dtime=1e-10,para=-1)
	path : 文件夹地址，
	para: if clockwise para=-1,if anticlockwise para=1 
	dtime:两个数据点之间的时间间隔。
3. 计算角速度，文件夹下可以包含多个excel，不过每个excel都要有Rx,Ry
通过这两列给出位置，还需要各处旋转方向。
如果顺时针就每次减pi，逆时针就加pi，每次x换号的时候加减。
'''
print(__doc__)
import pandas as pd
import math
import os
import numpy as np

def change(path):    
    '''
    '''
    xx=[[],[]]#store x,y
    if os.path.isfile(path):
        xy=pd.read_excel(path)
        x1=xy['Rx']
        y1=xy['Ry']
    elif isinstance(path,pd.DataFrame):        
        x1=xy['Rx']
        y1=xy['Ry']
    for i_0 in range(len(x1)):
        if x1[i_0]==0:
            if x1[i_0-1]>0:
                xx[0].append(0.001)#x
                xx[1].append(y1[i_0])
            else:
                xx[0].append(-0.001)#x
                xx[1].append(y1[i_0])
        else :
            xx[0].append(x1[i_0])#x
            xx[1].append(y1[i_0])#y
    return xx

def list2omega(xy,para):
    '''
    1,如果顺时针就每次减pi，逆时针就加pi，每次x换号的时候加减。
    2,把需要处理的数据放在同一个文件夹里会得到，mega.xlsx文件夹就是结果
	'''
    omega=[]
    n_1=0
    for i_1 in range(len(xy[0])-1):
        if xy[0][i_1]*xy[0][i_1+1]>0:
            theat=math.atan(xy[1][i_1]/xy[0][i_1])+math.pi*n_1*para
            omega.append(theat)
        else:
            theat=math.atan(xy[1][i_1]/xy[0][i_1])+math.pi*n_1*para
            omega.append(theat)
            n_1+=1
    return omega#每个地址的数据

def main(path,dtime=1e-10,para=-1):
    result=[]
    name=[]
    for addres in os.listdir(path):     
        namei=os.path.splitext(addres)[0]
        data=change(os.path.join(path,addres))#x,y
        omega=list2omega(data,para)#正负很重要
        omega2=(np.array(omega[1:])-np.array(omega[:-1]))/dtime
        result.append(omega2)
        name.append(namei)
    pf=pd.DataFrame(np.array(result).T,columns=name)
    os.chdir(path)
    pf.to_excel(r'omega.xlsx')    
   
if __name__=='__main__':
	#需要更改在这里更改
    path=input(r'please input the name of the dir:')
    main(path,dtime=20e-11,para=1)
    print('done!!')




