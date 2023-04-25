# -*- coding: utf-8 -*-
"""
@author: DELL
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 明确每个患者住院的天数和首次住院时期, 确定起始日期和结束日期
class AKI_simplify():

    def __init__(self, file_dir):
        
        self.olddata = pd.read_csv(file_dir,encoding = 'GB2312')  
        self.data = self.olddata[['subjid','GenderNo','age','test_result','days_from_admission']]
    
    def basic_statistics(self):
        
        self.count = self.data['subjid'].value_counts()
        self.male = (self.data['GenderNo'] == 1).sum()
        self.female = (self.data['GenderNo'] == 2).sum()
        self.age18 = (self.data['age'] <= 18).sum()
        self.age90 = (self.data['age'] >= 90).sum()
        #print('一共有', self.male,'个男性患者和', self.female,'个女性患者')
        #print('一共有', self.age18,'个未成年患者')
        #print('一共有', self.age90,'个年龄大于90患者')
    
    def data_process(self):

        self.scr = (75 / (186 * (self.data['age'] ** (-0.203)))) ** (-0.867) * 88.4
        self.data.insert(self.data.shape[1], 'scr', self.scr)
        #self.id_minday = self.data.groupby('subjid').agg({'days_from_admission':'min'})
        
        self.data['id_minday'] = self.data.groupby('subjid')['days_from_admission'].transform('min')
        def interval(series):
            id_minday = series["id_minday"]
            days_from_admission = series["days_from_admission"]
            interval = days_from_admission - id_minday 
            return interval
        
        self.data["day_interval"] = self.data.apply(interval,axis=1)
        #print(self.data)
        #self.data.to_csv('AKI_simplify.csv')


# 明确每个患者住院的天数和首次住院时期, 确定起始日期和结束日期
class AKI_monitor():
    def __init__(self, file_dir, idx):
        
        self.data = pd.read_csv(file_dir,encoding = 'GB2312')
        self.id = (self.data['subjid'] == idx) # '2100-0124'
    def __baseline__(self):
        '''
        有3条以上肌酐值的，用所有测量结果的最小值作为该患者基线;
        否则取scr平均值
        '''
        if len(self.data[self.id]) >= 3:
            self.test_result_baseline = min(self.data[self.id]['test_result'])

        else:
            
            self.test_result_baseline = (self.data[self.id]['scr']).mean()
            
        return self.test_result_baseline

        
        #self.baseline = min(self.test_result)

    
    def period_monitor(self):
        
        '''
        定义时间框的循环，截止到最后一条观测的化验日期前2天，借此框定2天的时间框，因此第0,1,2天3次的化验结果中间认为间隔48h;
        '''
        '''
        *最小和最大比较------------------------------------------------------------------------------------------------------------
        *48h肌酐的判断，对于每一个患者，有2次或以上，均以该患者所有现有肌酐结果的最低CR作为基线
        分析思路为：1，选择每名患者最低肌酐，若含2次以上，则以区间内最低值为基线，记录该基线和时间；否则以估测期望值为基线；
		   2，差值判断：区间内每次的肌酐与区间内最低值进行对比，判断是否与区间内最低值相比，升高≥26.5 且天数相减≤2，如此则满足条件1。选择的最低点为多次检测之最低点，故不会出现下降超过26.5的情况；
           I期;
        f result_max - result_min >=26.5 then do;
        AKI = 1;
        AKI_stage = 1;
        '''
        '''
        提取每一个id的test_result和day_interval出来为self.data_determine
        '''
        self.data_determine = (self.data[self.id]).iloc[:,[3,5]]
        self.flag = self.data_determine.iloc[0,[1]]
        for i in range(1,len(self.data_determine)):
            print(len(self.data_determine))
            self.temp = self.data_determine.iloc[i,:]            
            self.diff = self.temp['day_interval'] - self.flag
            AKI_stage = 0
            ratio = self.temp['test_result'] / self.test_result_baseline
            FD = self.temp['test_result'] - self.test_result_baseline
            # 2 days as a period
            if self.diff.values <=2:
                if  FD >= 26.5:
                    AKI_stage = 1
                    break
                print("时间:", i, ", AKI_stage:", AKI_stage)
            # 7 days as a period
            elif self.diff.values >2 and self.diff.values <=7:
            
                if (ratio >= 1.5) and (ratio < 2):
                    AKI_stage = 1
                elif (ratio >= 2) and (ratio < 3):
                    AKI_stage = 2
                elif (ratio >= 3):
                    AKI_stage = 3
                elif FD>=44 and self.temp['test_result']>=354:
                    AKI_stage = 3
                print("时间:", i, ", AKI_stage:", AKI_stage)
            else:
                break
            return i, AKI_stage




if __name__ == '__main__':
    
    '''
    读取表格
    '''
    file_dir1 = 'AKI.csv'
    # aki = AKI_simplify(file_dir = file_dir1)
    # aki.data_process()
    # aki.hour48_monitor()
    '''
    读取简化版表格
    '''
    file_dir2 = 'AKI_simplify.csv'
    monitor = AKI_monitor(file_dir = file_dir2, idx = '2100-0124')
    monitor.__baseline__()
    monitor.period_monitor()
    #print('AKI_stage is:', monitor.day2_monitor())

    
