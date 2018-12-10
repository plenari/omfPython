# -*- coding: utf-8 -*-
#python3
"""
2017年9月6日
@author: 409200093@qq.com
close the compute

2018年11月13日
未测试
"""
import time
import os

def cmp():#定义关机的方法，但是并没有运行
    print('The Compute will close in 200 seconds!\n ctrl+c to stop!')
    time.sleep(200)
    import platform
    if 'Windows' in platform.platform():
        os.system('shutdown -a')#windows
    elif 'Linux' in platform.platform(): 
        os.system('poweroff')#linux 
    else:
        assert 1==0,'unknow system platform'
