# -*- coding: utf-8 -*-
import sys
if '..' not in sys.path:
    sys.path.append('..')
import pandas as pd
import numpy as np
import os
from sklearn.cluster import DBSCAN
from analyze import nanotube,ellipse,circle
from tool.selectSuffix import selectSuffix
import matplotlib.pylab as plt

class Fit():
    '''
    主要针对用来计算斯格明子位置,大小等。 输入数据为计算拓扑数使用的数据格式，[x,y,m]   
    
    >>>输入xym和拓扑数
    >>>密度聚类和拓扑数一致，就进行下一步
    >>>选择一个斯格明子的xym
    >>>计算该斯格明子的大小和位置
    >>>选择另外一个
    >>>计算出来的数据保存:将得到的新的位置距离之前哪个更近就放到那个斯格明子的位置上。
    
    >>>计算出来的边界位置，是否需要保存
    >>>是否需要画出边界和拟合边界的效果图
    
    '''
    def __init__(self,savedir='',maxSkyr=10):
        '''
        maxSkyr:最多有几个斯格明子,默认为10     
        savedir:将文件保存到那个文件夹。
        '''
        self.maxSkyr=maxSkyr#
        #计算两个斯格明子位置时，索引在column位置。
        self.calDisComTwoSkyr = [1,2]
        self.columns,self.circlexy=self.createColumns()        
        self.DF=pd.DataFrame(columns=self.columns)#    
        self.savedir=savedir

        
    def createColumns(self):
        '''
        产生保存结果DF的列名称，与最大斯格明子数有关，
        
        self.calDisComTwoSkyr:
            并且返回一些固定位置的索引，比如圆心坐标x,y,这个位置主要是为了保证与新的斯格明子圆心位置对比。
        '''
        column=['circleD','circleX','circleY','ellipseA','ellipseB','ellipseX','ellipseY','ellipseQ']
        self.columnLen=len(column)
        columns=[]
        circlexy=[]
        for i in range(self.maxSkyr):
            for j in column:
                columns.append(j+str(i))
            circlexy.append([self.calDisComTwoSkyr[0]+len(column)*i,self.calDisComTwoSkyr[1]+len(column)*i])            
        return columns,circlexy
    

    def updataDF(self,data,index,fillna=0.0):
        '''
        data:为按照column排列的一组数据
     
        每计算一次，更新一次计算结果
        把计算出来的斯格明子位置与之前的数据比较，然后保存。
        '''
        if len(self.DF)==0:
            #第一次，把这个填满
            new_data=np.array(data).flatten()
            zeros=np.zeros(self.DF.shape[1])
            zeros[:len(new_data)]=new_data
            self.DF.loc[index]=zeros
            self.DF.fillna(0.0,inplace=True)
        
        else:#需要排序，然后插入指定位置。
            lens=len(self.DF)#更新前DF的长度
            for indexDF,tempDF in enumerate(data):
                '''
                计算tempDF圆心位置距离上一次所有位置的距离，
                找到最近的那个，然后保存下来
                :对每一组数进行循环。只计算距离圆心的距离吧。
                
                '''
                whereMin={}
                for i,circlexy in enumerate(self.circlexy):
                    '''
                    i:第i个斯格明子
                    circlexy:这个斯格明子计算距离使用的数据在DF中的位置
                    '''
                    prexy=self.DF.iloc[lens-1,circlexy]
                    curxy=np.array(tempDF[self.calDisComTwoSkyr[0]:np.sum(self.calDisComTwoSkyr)])
                    
                    distance=np.sqrt(np.sum((prexy-curxy)**2))
                    #字典的key为一个斯格明子数据的位置。
                    whereMin[circlexy[0]-1]=distance
                    #print(index,indexDF,i,circlexy,prexy,curxy,distance,'\n')
                whereMinIndex,mindis=sorted(whereMin.items(),key=lambda item:item[1])[0]
                
                self.DF.loc[index,self.columns[whereMinIndex:whereMinIndex+self.columnLen]]=tempDF
                
            self.DF.fillna(0.0,inplace=True)#把tempDF都加入DF里后，把没有数据的位置，填充为0                       
    
        
    def dbscan(self,x,y):
        '''
        分析x,y中可能存在的斯格明子，  结果存在clf.labels_里
        其中xy为m与limit对比结果的索引值。
        '''
        #距离两个网格之内至少有六个点认为是斯格明子
        clf=DBSCAN(eps=3,min_samples=6)
        X=np.vstack([x,y]).T
        clf.fit(X)
        return clf
    
    
    def getChange(self,xlim,ylim,mlim):
        '''        
        找到mlim变号对应的位置。 xlim,ylim,mlim都是二维的矩阵形状。
        
        由于可能有多个斯格明子，所以这个可以直说原始矩阵的一部分,都是经过限制的矩阵。
        
        >>>
        '''
        assert len(xlim.shape)==2,'必须是二维的矩阵'
        #数据左右相乘
        m_mul=mlim[:,:-1]*mlim[:,1:]
        #相乘结果小于零，左边的位置
        loc=np.where(m_mul<0)#
        locx,locy=loc[0],loc[1]#行列
        #斜率
        dm_dx=(mlim[(locx,locy+1)]-mlim[(locx,locy)])/(xlim[(locx,locy+1)]-xlim[(locx,locy)])
        #
        new_x=xlim[(locx,locy)]+(0-mlim[(locx,locy)])/dm_dx
        new_y=ylim[(locx,locy)]
        return new_x,new_y

    
    
    def fit(self,data,Q,index='filesName',plots=True,plotsFlag='',saveNewxy=True,saveNewxyFlag='',sign=-1,limit=0,extend=5):
        '''
        data:[x,y,m]  主要是通过m小于0 的部分确定斯格明子的位置。  
        Q:计算处出拓扑数
        sign:-1,代表斯格明子在m小于limit的位置，sign：1,代表斯格明子在m大于limit的位置
        limit：为阈值,只能为0
        index:如果保存这个数据的话，用什么作标记呢？一般用文件的名字
        extend：
        '''
        assert isinstance(data,list),'保存的数据必须的列表形式'
        for i in data:
            assert len(i.shape)==2,'数据必须是二维结构'
        self.index=index#可以用来保存数据
        x,y,m=data[0],data[1],data[2]        
        
        m0=np.where((m*sign)>limit)
        #密度聚类斯格明子。        
        clf=self.dbscan(m0[0],m0[1])
        skyrNum=clf.labels_.max()+1#斯格明子的个数
        print('fit: \t index:{}, \tQ:{},\t skyrNum:{}'.format(index,Q,skyrNum))
        
        #只有拓扑数计算和密度聚区分的一致才进行下一步计算。        
        if skyrNum==np.ceil(np.abs(Q)) and skyrNum>0 and skyrNum<=self.maxSkyr:
            temp_newXY=[]
            newXY_columns=[]
            tempDF=[]
            for i in range(skyrNum):
                #当前斯格明子
                loc0=m0[0][clf.labels_==i]
                loc1=m0[1][clf.labels_==i]
                #得到限制后的x,y,m
                
                extendx=(loc0.max()-loc0.min())//2+2
                extendy=(loc1.max()-loc1.min())//2+2
                xlim=x[loc0.min()-extendx:loc0.max()+extendx, loc1.min()-extendy:loc1.max()+extendy]
                ylim=y[loc0.min()-extendx:loc0.max()+extendx, loc1.min()-extendy:loc1.max()+extendy]
                mlim=m[loc0.min()-extendx:loc0.max()+extendx, loc1.min()-extendy:loc1.max()+extendy]
                #得到改变符号后的
                new_x,new_y=self.getChange(xlim,ylim,mlim) 
                self.new_x,self.new_y=new_x,new_y               
                
                
                #圆和椭圆拟合
                circleDXY=self.circle(new_x,new_y)
                normal,paras=self.ellipse(new_x,new_y)                
                self.normal,self.paras=normal,paras
                #baocun
                temp_newXY.append(new_x);temp_newXY.append(new_y)
                newXY_columns.append(circleDXY[1]);newXY_columns.append(circleDXY[2])
                
                #画图
                if plots and len(new_x)>3:
                    fits=ellipse.cal_fit_data(paras,normal,new_x)                    
                    self.plots(new_x,new_y,fits[0],fits[1],self.index,flag=plotsFlag+str(i))  
                tempDF.append([*circleDXY,*normal])

            self.updataDF(tempDF,index)
            if saveNewxy and len(temp_newXY)>2:
                self.saveNewxy(temp_newXY,newXY_columns,filename=index,flag=saveNewxyFlag)
        else:
            pass
            

        

    def plots(self,x0,y0,fitx,fity,filename='m000.xlsx',flag='ellipse'):
        '''
        画出拟合数据和原始数据，并保存。
        filename的后缀是什么无所谓，可以自己替换。
        '''   
        fig=plt.figure()
        ax=fig.add_subplot(111)
        ax.plot(x0,y0,'b*',label='origin')    
        ax.plot(fitx,fity,'r.',label='fits')
        ax.set_title(filename+'-'+flag)
        plt.legend(loc='best')
        #plt.show()
        figname=filename.replace(os.path.splitext(filename)[-1],flag+'.png')        
        fig.savefig(os.path.join(self.savedir,figname))
        plt.close()
        
    def saveNewxy(self,tempNewXY,newXYColumns,filename,flag='newxy'):
        '''
        X,y保存new_x，new_y,
        每一个文件保存一次。
        temp_newXY:为按照相同顺序保存的计算的每一个斯格明子的边界位置[[x0,y0],[x1,y1],....]
        file: name
        '''
        
        columns=[]
        for i,value in enumerate(newXYColumns):
            if i%2==0:
                columns.append('x'+str(i//2)+str(value))
            elif i%2==1:
                columns.append('y'+str(i//2)+str(value))
        xy=pd.DataFrame(tempNewXY).T    
        xy.columns=columns
        xyname=filename.replace(os.path.splitext(filename)[-1],flag+'.xlsx')        
        xy.to_excel(os.path.join(self.savedir,xyname))         

                
    def circle(self,x,y):
        '''
        #最小二乘法,拟合圆形
        返回的是直径，x,y的圆心。
        
        Example:
            
        >>>y=[0,-1,0,1]
        >>>x=[0,1,2,1]
        >>>circle(x,y)
        (2.0, 1.0, 0.0)
        '''
        if len(x)>3:
            try:
                return circle.circle(x,y)
            except:
                return 0,0,0
        else:
            return 0,0,0
    
    def ellipse(self,x,y):
        '''
        椭圆拟合
        a,b,x,y,theta
        '''
        if len(x)>3:
            try:    
                paras=ellipse.solve_tuoyuan(x,y)
                normal=ellipse.normal_style(paras)      
                return normal,paras
            except:
                return (0,0,0,0,0),[0]*6
        else:
            return (0,0,0,0,0),[0]*6
        
if __name__=='__main__':  
    
    fdir=r'K:\模拟结果\nanotube的模拟结果\nanotube-Hz-R50-r40.out'
    fnames=selectSuffix(fdir,'.ovf')[1][480:485]
    
    n=nanotube.Nanotube(os.path.join(fdir,fnames[0]))
    
    f=Fit(fdir,maxSkyr=10)
    for i in fnames:
        n.loadData(os.path.join(fdir,i))
        csl=n.reshape3D().circleSlicing(rclip=[49e-9,50e-9])
        x,y=n.xyz2xy(csl[:3])
        xydensity,Q = n.calQN([x,y,csl[3],csl[4],csl[5]])
        m=csl[5]   

        f.fit([x,y,m],Q,index=i,sign=np.sign(Q))
        
    f.DF.to_excel(os.path.join(f.savedir,'circle-ellipse.xlsx'))

