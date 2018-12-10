# -*- coding: utf-8 -*-
#python3.x
#@author :shengjiex@qq.com
'''
2018年4月3日
如果有M000032.txt，或者M32.txt这样连续的文件，需要把数字加减乘除n,可以用这个办法。
保存的时候有两种保存方法，
第一个就是保存成数字，就是从1到100，
第二个就是把数字保存成固定长度的。比如000001，000002....00100...
方法：
加:+2   减：-2   乘：*2   除：/2


'''
print(__doc__)

import re
import os


if __name__=='__main__':
    fdir=input(r'需要操作的文件夹地址：')
    fnum=input(r'被+-*/的数：')
    print('如果想要名字中数字的长度为固定值，为0表示数字长度不固定名字的长度。')
    the_length_of_num=int(input('输入:'))
    os.chdir(fdir)
    qb='abzqbwq'

    #用qb替换了数字,
    for i in os.listdir(os.getcwd()):
        try:
            num_origin=re.search('[\d]+',i).group(0)#文件名里的数字
            if num_origin==None:
                continue
            num_new=str(int(eval('{}{}'.format(\
                         str(int(num_origin)),fnum))))#新的数字
            new_name=i.replace(num_origin,qb+num_new)
            if the_length_of_num:
                new_name=i.replace(str(num_origin),'0'*(the_length_of_num-len(str(num_new)))+qb+num_new)
            assert num_origin!=None,'%s里没有数字'%i
            os.rename(i,new_name) 
        except:
            pass
    #去掉qb
    for i in os.listdir(os.getcwd()):
        if qb in i:
            os.rename(i,i.replace(qb,''))
    print('Rename has done!')
