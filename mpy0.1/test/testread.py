# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 11:22:59 2018

@author: Plenari
"""
import sys
if '..' not in sys.path:
    sys.path.append('..')

import os
import numpy as np
import pandas as pd    
from read import readtext


file=r'C:\Users\omf\Desktop\mpy_new\test\m000001.ovf'
txt=r'C:\Users\omf\Desktop\mpy_new\test\m000001.ovf.txt'
test=r'C:\Users\omf\Desktop\mpy_new\test\m000477.ovf'


#读取

print('\ntxt\n')
r=readtext.Read(txt)
r.loadData(txt) 
print(r.data[0].shape)
print(r.dict)

print('\ntest\n')
r=readtext.Read(test)
r.loadData(test)
print(r.data[0].shape)
print(r.dict)

print('\n\nfile\n')
r=readtext.Read(file)
r.loadData(file)
print(r.data[0].shape)
print(r.dict)




#ModelPara 程序有点问题。

# reshape
r.reshape3D()
print(r.data[0].shape)

#flatten
r.flatten1D()
print(r.data[0].shape)


# slicing
slicing=r.reshape3D().slicing(4)
print(slicing[0].shape)


#subsample

r.reshape3D().subsample([2,4,5])
print(r.data[0].shape)


#r.limit，坐标系有点问题。
lim=r.flatten1D().limit()
print([[i.min(),i.max()]for i in lim])


#切片 
r=readtext.Read(test)
r.loadData(test)
print(r.data[0].shape)
print(r.dict)
sl=r.reshape3D().slicing(4)

#计算拓扑数
xydensity,Q=r.calQ([sl[0],sl[1],sl[3],sl[4],sl[5]])
print(Q)
print(xydensity[0].shape)


#save 
#只能保存二维数据
r.saveExcel(sl,flag='slcing')

#保存
r.saveNpz(r.data,flag='data')




















