#coding=utf-8
#!env/usr/bin/python
#2017年11月7日
'''
单个文件夹，转格式，移动和重命名
使用条件：
1.文件夹下包含mif文件，mif文件里有，'file ******.omf'行，
有‘Schedule Oxs_TimeDriver::Magnetization archive stage **'行，
这两行代表了omf文件的初始态文件和保存的间隔。一般情况都有这两行。
2.没有mif文件需要手动输入，初始态文件名字(可为空)和保存间隔(不可为空)
3.可能需要根据计算机更改tclsh86和oommf的文件地址。
4.转格式的类型一般为.omf,.oef,.ovf，可以在文件里更改。
流程：
1.输入文件夹，自动或手动得到文件夹下mif文件里的file ,step然后会忽略file文件
2.文件后缀为.txt的都会移动到当前文件夹txt下
3.重命名，会得到文件名字里的数字，如果有多个符合取第一串数字，除step得到新的名字
TCL_OOMMF=r'C:\ProgramFiles\tcl\bin\tclsh C:\ProgramFiles\oommf\oommf.tcl'
4.如果设置了name_format=[start,end],则用着个规则命名。
'''
#这是使用tcl和oommf的地址，不同机器地址不同。
TCL_OOMMF=r'C:\ActiveTcl\bin\tclsh F:\omf\oommf12b\oommf.tcl'

import os
import shutil
import re

def get_data(p):
    '''
    获得omf 源文件的名字和保存间隔
    '''
    schedule=r'Schedule Oxs_TimeDriver::Magnetization archive stage'
    omf,step=None,None
    for i in os.listdir(p):
        if os.path.splitext(i)[-1]=='.mif':
            with open(os.path.join(p,i)) as f:
                file=f.readlines()
            for ii in file:
                if '.omf' in ii and 'file' in ii :
                    omf=(ii.strip()[4:]).strip()
                if schedule in ii:
                    step=(re.search('[\d]{1,3}',ii).group())            
            
    if omf==None or step==None:
        return False,False
    else:
        return omf,step
def get_dir():
    #判断地址是是否符合要求
    pathdir=input('\n请输入需要转格式的文件夹地址: ')
    if os.path.isdir(pathdir):
        return pathdir
    else:
        print('输入的地址不是文件夹: ')
        get_dir()

def get_file_step():
    path_dir=get_dir()
    file,step=get_data(path_dir)
    if file==False and step==False:
        file=input('初始文件\n')#代表初始文件的名字
        step=input('保存间隔\n')#代表文件的保存间隔
    return path_dir,file,step

def zgs(addres,file):
    """
    :param address:single director
    :return:1
    """
    os.chdir(addres)
    for i in os.listdir(addres):
        if os.path.splitext(i)[-1] in ['.omf','.oef','.ovf'] and i!=file:#可以把'.omf'改成其他后缀来更改需要转格式的内容
            #这个地址可能会需要改一下，只修改引号内部的，表示两个程序的地址：d:\tcl\bin\tclsh86t d:\oommf12a5\oommf.tcl 
            os.system(r'%s avf2ovf -format text -grid irreg %s %s.txt'%(TCL_OOMMF,i,i))
    print('%s格式转换完毕'%addres)
    return True

def move(addres):
    #把addres文件夹下的txt文件移动到txt文件夹下去
    os.makedirs(os.path.os.path.join(addres,'txt'))
    for txt in os.listdir(addres):
        if os.path.splitext(txt)[1]=='.txt':
            shutil.move(os.path.join(addres,txt),os.path.join(addres,'txt',txt))
    print('%s移动完毕'%addres)
    return os.path.join(addres,'txt')

def renam(pathi,step,name_formart=None):
    '''
    :param path:
    :param step:
    name_formart=[0,5]
    :return:
    '''
    for txt in os.listdir(pathi):
        #需要数字串的长度要在这两个数之间，可以更改：[\d]{3,12}
        if name_formart==None:
            name=int(int(re.search('-([\d]{3,12})-',txt).group(1))/int(step))
        else:
            name=txt[name_formart[0]:name_formart[1]]
        os.rename(os.path.join(pathi,txt),os.path.join(pathi,'M%d.txt'%name))
    print('%s重命名完毕'%pathi)
    return True

def Zyc(path_dir): 
    file,step=get_data(path_dir)
    _z=zgs(path_dir,file)
    path_move=move(path_dir)
    renam(path_move,step)
    return path_move

if __name__=='__main__':
    print('\n当前使用的TCL_OOMMF地址是：\n{}'.format(TCL_OOMMF))
    name_formart=None
    #name_formart=[15,20]
    path_dir,file,step=get_file_step()
    zgs=zgs(path_dir,file)
    path_move=move(path_dir)
    renam(path_move,step,name_formart)