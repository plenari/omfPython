#coding=utf-8
#Plenari
import os
import re

def selectSuffix(pdir,suffix='.xlsx'):
    '''
    选择pdir文件下，以suffix结尾的文件。
    排序返回,文件夹地址和选择后的文件。
    Example:
        
    >>>pdir=r'K:\模拟结果\曲率半径大于80的弯曲曲面\arc-Hz-R80'
    >>>print(selectSuffix(pdir,'.ovf'))
    
    '''
    pnames=[i for i in os.listdir(pdir) if os.path.splitext(i)[-1]==suffix]
    try:
        pnames=sorted(pnames,key=lambda x:int(re.search('[\d]+',x).group(0)))
    except:
        pnames=sorted(pnames)
    return pdir,pnames

if __name__=='__main__':
    pdir=r'K:\模拟结果\曲率半径大于80的弯曲曲面\rectangle-Hz'
    print(selectSuffix(pdir,'.xlsx'))