# -*- coding: utf-8 -*-
"""
2018年11月9日
解析产生文件的字典
把与模型相关的参数添加到字典里。
@author:shengjiex@qq.com
"""
import re
def comment(fname):
    '''
    读取文件fname的注释信息，以#为准
    return 带有#的段落，不带#号的第一行有多少列
    
    '''
    s=''
    with open(fname, "r") as f:
        while True:
            line=f.readline()
            if line[0] == "#":
                s=s+line
            elif line[0] != "#":
                columns=len(line.strip().split())
                break
    return s,columns


def analyze(fname):
    dic={}
    # keyword list from ovf-file:
    keywords = ["Title:","meshtype:", "meshunit:", 'columns',
            "xbase:", "ybase:", "zbase:",
            "xstepsize:", "ystepsize:", "zstepsize:",  
            "xnodes:", "ynodes:","znodes:",'ValueRangeMaxMag:',
            "xmin:", "ymin:", "zmin:", "xmax:", "ymax:", "zmax:"]
    s,columns=comment(fname)
    dic['columns']=columns
    
    #
    for key in keywords:        
        z=re.findall('{}\s(.*)'.format(key),s)
        if len(z)>0:
            dic[key]=z[0].strip()
    
    #读取ovf之类的
    if 'znodes:' in dic.keys()  :
        return dic
    
    # 如果读取的是txt导致信息不全。
    else:
        key1=['xbase:', 'ybase:', 'zbase:']
        key2=[ 'xnodes:', 'ynodes:', 'znodes:']
        #计算base，
        for i in key1:
            dic[i]=(float(dic[i[0]+'min:'])+float(dic[i[0]+'stepsize:']))/2
        #计算节点数
        for i in key2:
            dic[i]=int(float(dic[i[0]+'max:'])/float(dic[i[0]+'stepsize:']))
            
        return dic
        