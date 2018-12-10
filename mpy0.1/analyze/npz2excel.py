#coding=utf-8
import pandas as pd
import numpy as np
import os
import shutil
'''
把npz文件内的数据保存成Excel用于画图
'''         
def read_npz(ffile):
    f=np.load(ffile)['data']
    x,y,z,mx,my,mz=f[0],f[1],f[2],f[3],f[4],f[5]
    return x,y,z,mx,my,mz

if __name__=='__main__':
    #计算多个文件夹,包含文件夹的文件夹地址。
    fdir=input(r'input dir  ：')
    save_quant='mz'
    dicts={'x':0,'y':1,'z':2,'mx':3,'my':4,'mz':5}[save_quant]
    path=[os.path.join(fdir,i) if i[-4:]=='.npz' else None for i in os.listdir(fdir) ]
    for i in path:
        cc=read_npz(os.path.join(fdir,i))
        pd.DataFrame(cc[dicts]).to_excel(os.path.join(fdir,i).replace('.npz','.xlsx'))
        print('%s has done!'%i)
        
