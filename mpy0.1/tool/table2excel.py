#!env/usr/bin/python3
#encoding=utf-8
'''
2018年1月4日
说明：
所有可以用txt打开的文档都可以处理。把他们按照要求保存到excel里。
可以处理一个文件夹下所有的文档。
使用方法，
给定usecols(使用那些列)，获取数据,重命名需要给定columns(列名)。
或者通过columns给定的列名称获取数据，有可能失败。
如果没有给出columns ,会使用文件中的名称命名所有列。
step 表示table里多少行数据保存一次。
如果都为 None 将保存所有的数据。


'''
print(__doc__)
import os
import numpy as np
import pandas as pd

def table2excel(pathfile,step=1,usecols=None,columns=None, sep='\t',): 
    '''
    step：保存间隔，
    usecols:使用那些列，
    columns:使用那些列，或者重命名数 
    delimiter ,分隔符
    
    '''
    data=pd.read_table(pathfile,usecols=usecols,sep=sep).iloc[::step].reset_index(drop=True)
    if columns!=None:
        try:
            data=data[columns]
        except:
            if data.shape[-1]==len(columns):
                data.columns=columns
    return data

def anapath(pdir,step=1,usecols=None,columns=None,sep='\t',rename_index=-1):
    '''
    结果保存的 参数
    '''
    rename_dir=pdir.split(pdir.split(os.sep)[rename_index])[0]
    
    for file in os.listdir(pdir):
        if os.path.isfile(os.path.join(pdir,file)):
            #想处理格式都可以加到下边的中括号内。
            if os.path.splitext(file)[-1] in ['.odt','.txt']:
                pathfile=os.path.join(pdir,file)
                data=table2excel(pathfile,step,usecols,columns,sep,)
                rename_file=pdir.split(os.sep)[rename_index]+'-'+file.replace(os.path.splitext(file)[-1],'.xlsx')
                print('{} is done!'.format(file))
                data.to_excel(os.path.join(rename_dir,rename_file))

if __name__=='__main__':
    #usecols=[0,5,9,10,11,12,13,15]#用哪些列
    #columns=['Total','Exc','DMI','Demag','Uzzem','B','Bx','Bz']#列的名字是什么？
    usecols=None
    columns=None#['mz ()','B_extz (T)']
    step=1#step,是想要保存的间隔
    rename_index=-1
    print('''当前使用的参数是：\n1，usecols:{}\n2,columns:{}\n3,step:{}'''.format(usecols,columns,step))
    path=input(r'请输入odt文件所在的文件夹地址:')
    anapath(path,step=step,usecols=usecols,columns=columns,sep='\t',rename_index=rename_index)
