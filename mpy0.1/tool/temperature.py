#coding=utf-8
#Plenari
'''
2018年11月13日
远程获得cpu温度，检测温度和网络的畅通
服务器x3850满载时CPU的温度减去27就是空调当前显示的温度。
把CPU温度设置成57报警，当时空调显示的应该是30.
如果有情况可能会有刺耳的警报声。
针对centos系统，不知其他系统有没有变化
'''
import time
from multiprocessing import Process
import paramiko
import matplotlib.pyplot as plt

hostname=''#远程服务器地址。
username=''#用哪个用户名登陆服务器
password=''#服务器的密码,
ssh = paramiko.SSHClient()#创建SSH对象
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())#把要连接的机器添加到known_hosts文件中

def plot_wrong():
    plt.text(0,0.5,'something wrong',fontsize=100)#有错误会画图
    plt.show()
    
def get_ssh():
    try:#get  data
        ssh.connect(hostname=hostname, port=22, username=username, password=password)
        cmd = 'cat /sys/class/hwmon/hwmon0/device/temp1_input'#CPU温度所在的文件位置
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = int(stdout.read().decode('utf-8'))/1000  
        ssh.close()
        return 1,result#net is ok,temperature of cpu
    except:#失败返回0,0
        p1=Process(target=plot_wrong)
        p1.start()
        return 0,0
        
def beep(mess='high temp'): #waring 
    print(time.strftime('%m-%d %H:%M'),mess,) 
    for i in range(20):
        print('\a')
        time.sleep(1)
        
def analys():#analys
    global net,temp
    _net,_cpu=get_ssh()
    net.pop(0);net.append(_net);temp.append(_cpu)
    print(time.strftime('%m-%d %H:%M'),'net:',_net,'temp:',int(_cpu-27),'cpu:',int(_cpu))
    return net,_cpu

if __name__=='__main__':
    net,temp=[1,1],[]#连续两次网络不通会报警。
    cpu=57#报警温度。#
    while True:       
        net,_cpu=analys()#
        if sum(net)==0:#[0,0]
            p1=Process(target=beep,args=('network is disable',))
            p1.run()
        if _cpu>cpu:
            p2=Process(target=beep,args=('high temperature',))
            p2.run()
        time.sleep(15*60)
    
    