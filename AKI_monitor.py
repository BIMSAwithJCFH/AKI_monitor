# -*- coding: utf-8 -*-
"""
@author: DELL
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import csv

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
        self.idx = idx

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
    '''
    def __baselineMax__(self):
        
        self.test_result_baselineMax = max(self.data[self.id]['test_result'])
        return self.test_result_baselineMax
        
        #self.baseline = min(self.test_result)
    '''

    
    def period_monitor_2(self):
    
        self.data_determine = (self.data[self.id]).iloc[:,[3,5]]
        
        '''
        test_result  day_interval
        0         80.2             0
        1        109.2             4
        2         69.0             6
        3         76.1            90
        4         78.1            97
        5         67.9           505
        6         80.2             0
        '''
        self.flag = (self.data_determine.iloc[:,[1]]).max(axis = 0)
        date_df = self.data_determine.iloc[:,[1]]
        self.result = (self.data[self.id]['test_result'])
        date = []
        id_result = []
        for i in range(len(date_df)):
            date.append(date_df.iloc[i].item())
            id_result.append(self.result.iloc[i].item())
        ilos = (self.data_determine.iloc[:,[1]]).max(axis = 0)
        i_los = ilos.item()
        # 2 days as a period
        if i_los < 2:
            i_los = 2
        for i in range(0, i_los-2+1, 1):
            # i->[0,1,2,...,503]
            # 定义以1天为基本步数的2天时间框;
            date_start = date[0] + i
            date_end = date[0] + i + 2 
            window = []
            for m in enumerate(date):
                if m[1]>=date_start and m[1]<=date_end:
                    window.append(id_result[m[0]])
                    bl = self.__baseline__()
                    #result_min = min(np.min(window), bl)
                    result_min = np.min(window)
                    result_max = np.max(window)
                    #print("i:",i,",m:", m,',result',id_result[m[0]])
                    #print("i:",i,",m:", m,',window',window,'min',result_min)
                    if (result_max - result_min) >=26.5:
                        self.AKI_stage = 1
                        print("id",self.idx,"day_inteval:",i, "m:", m[1],'window',window,"AKI_stage:",self.AKI_stage)
                    else:
                        self.AKI_stage = 0
                        #print("id:",self.idx,"day_inteval:",i, "m:", m[1],'window',window,"AKI_stage:",self.AKI_stage)
                      
                    
            '''
            for j in range(0, len(date_df)):
            #由于开始日期是以1为步数累加，故存在实际起始日期大于等于开始时间，则跳出循环，重新进入该循环，记录起始mark值。设定大于是因为有的人日期有跳跃性，可能导致不等于;
                if date[j] == date_start:
                    date_start_mark = j
                    break       
            for j in range(0, len(date_df)):
                # 由于日期不确定性，一旦有日期大于时间框，则结束循环，记录mark值
                if date[j] > date_end:
                    j = j - 1
                    date_end_mark = j
                    break
                elif date[j] == date_end:
                    date_end_mark = j
                    break
            #print(date_start)
            #print("i: ", i, "date_end: ", date_end)
            #print("i: ", i,"date_end_mark: ", date_end_mark)
            '''
            '''
            判断这段时间的最小值和最大值------------------------------------------------------------------------------------------;
			有的两头只有1条或2条记录，会导致result[date_end_mark]实际为空，也就是没有endmark。此时，result[date_start_mark]会大于等于result[date_end_mark]
			 此时，数据库中肯定有result[date_start_mark]，test_result[&i_Nobs.]则有可能就是result[date_start_mark];
            '''
            #if date_start_mark >= date_end_mark:
                #有2条记录的，需要判断下最大最小值，最小值与期望值比较，择其小者；有3条以上记录的，会默认以最小值&base_CR.作为其基线;
                #self.result_min =  self.__baseline__()
                #self.result_max =  self.__baseline__()
            #elif date_start_mark < date_end_mark:
                #pass
            
            
            
        return self.AKI_stage
    
    def period_monitor_7(self):
        self.data_determine = (self.data[self.id]).iloc[:,[1,-2,-1]]
        self.flag = (self.data_determine.iloc[:,[2]]).max(axis = 0)
        date_df = self.data_determine.iloc[:,[2]]
        self.result = (self.data[self.id]['test_result'])
        self.scr = (self.data[self.id]['scr'])
        
        date = []
        id_result = []
        id_scr = self.scr.iloc[0].item()
        for i in range(len(date_df)):
            date.append(date_df.iloc[i].item())
            id_result.append(self.result.iloc[i].item())
            
        
        
        ilos = (self.data_determine.iloc[:,[2]]).max(axis = 0)
        i_los = ilos.item()
        '''
        疑似AKI判断和转正
        '''
        doubt = 0.5
        self.id_result_max = max(id_result)
        if id_result[0] >= id_scr*1.5:
            self.AKI_doubt = 1
            doubt = self.AKI_doubt
            print(self.idx,"为疑似AKI")
            #self.id_result_max = max(id_result)
            id_result_min = min(id_result)
            if self.id_result_max/id_result_min>=1.5:
                self.AKI_stage = 1
                print("疑似AKI转正:", self.AKI_stage)
        else:
            self.AKI_doubt = 0
            doubt = self.AKI_doubt
        
        
        #period = math.ceil((i_los+1)/30)
        period = 1
        for k in range(0, period, 1):
            # 2 days as a period
            if i_los < 7:
                i_los = 7
            inteval_list = []
            stage_list = []
            for i in range(0 + k * 30 , i_los + k * 30 - 2 , 1):
                #print("k:",k,"i:",i)
                # i->[0,1,2,...,503]
                # 定义以1天为基本步数的7天时间框;
                # date[0] = 0
                date_start = date[0] + i
                date_end = date[0] + i + 7 
                window = []
                for m in enumerate(date):
                    #print("k:",k,"i:",i,"m",m[1])
                    if m[1]>=date_start and m[1]<=date_end:
                        #print("k:",k,"i:",i,"m:",m[1],'date_start:',date_start,'date_end:',date_end)
                        window.append(id_result[m[0]])
                        # bl = self.__baseline__()
                        #result_min = min(np.min(window), bl)
                        result_min = np.min(window)
                        result_max = np.max(window)
                        maxloc = window.index(max(window))
                        #print("result_max",maxloc)
                        
                        ratio = result_max / result_min
                        FD = result_max - result_min
                        #print("i:",i,",m:", m,',result',id_result[m[0]])
                        #print("i:",i,",m:", m,',window',window,'min',result_min)
                        recover = None
                        if ((FD >=44) and (result_max>=354)) or ratio >= 3:
                            self.AKI_stage = 3
                            if (id_result[m[0]] == result_min) and (self.id_result_max/id_result[m[0]]>=1.5) and (m[1]!=date_end) and (m[1]!=date_start) and (m[1]!=0):
                                print("inteval:",m[1],"为恢复日期")
                                recover = m[1]
                                inteval_list.append(maxloc+i)
                            else: 
                                inteval_list.append(m[1])
                            stage_list.append(self.AKI_stage)
                            #print("id:",self.idx, "day_flag:",i, "m:", m[1],'window',window,"AKI_stage:",self.AKI_stage)
                            break
                        elif (ratio >= 2) and (ratio < 3):
                            self.AKI_stage = 2
                            if (id_result[m[0]] == result_min) and self.id_result_max/id_result[m[0]]>=1.5 and (m[1]!=date_end) and (m[1]!=date_start) and (m[1]!=0):
                                print("inteval:",m[1],"为恢复日期")
                                recover = m[1]
                                inteval_list.append(maxloc+i)
                            else: 
                                inteval_list.append(m[1])
                            stage_list.append(self.AKI_stage)
                            #print("id:",self.idx, "day_flag:",i, "m:", m[1],'window',window,"AKI_stage:",self.AKI_stage)
                            break
                        elif (ratio >= 1.5) and (ratio < 2):
                            self.AKI_stage = 1
                            if (id_result[m[0]] == result_min) and self.id_result_max/id_result[m[0]]>=1.5 and (m[1]!=date_end) and (m[1]!=date_start) and (m[1]!=0):
                                print("inteval:",m[1],"为恢复日期")
                                recover = m[1]
                                inteval_list.append(maxloc+i)
                            else: 
                                inteval_list.append(m[1])
                            stage_list.append(self.AKI_stage)
                            #print("id:",self.idx, "day_flag:",i, "m:", m[1],'window',window,"AKI_stage:",self.AKI_stage)
                            break
                        else:
                            self.AKI_stage = 0
                            #inteval_list.append(m[1])
                            stage_list.append(self.AKI_stage)
                            #print("id:",self.idx, "day_flag:",i, "m:", m[1],'window',window,"AKI_stage:",self.AKI_stage)
                    
                
                #if self.AKI_stage !=0:
                    #print("id:",self.idx, "疑似转为确诊，确诊日期为:", m[1],"AKI_stage:",self.AKI_stage)
                    #continue
                if self.AKI_stage !=0:
                    print("id:",self.idx, "day_flag:",i, "inteval:", m[1],"AKI_stage:",self.AKI_stage,"AKI_stage:",recover)
                    xieru = []   
                    xieru.append({'id': self.idx, 'doubt': doubt, 'inteval': m[1], 'AKI_stage': self.AKI_stage, 'recover': recover})
                    # Write the data to CSV file
                    with open('AKI所有结果.csv', 'a', newline='') as csvfile:
                        fieldnames = ['id', 'doubt', 'inteval', 'AKI_stage', 'recover']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        #writer.writeheader()
                        for row in xieru:
                            writer.writerow(row)
                    break
                else:
                    print("id:",self.idx, "day_flag:",i, "inteval:", m[1],"AKI_stage:",self.AKI_stage)
                    xieru = []   
                    xieru.append({'id': self.idx, 'doubt': doubt, 'inteval': m[1], 'AKI_stage': self.AKI_stage})
                    # Write the data to CSV file
                    with open('AKI所有结果.csv', 'a', newline='') as csvfile:
                        fieldnames = ['id', 'doubt', 'inteval', 'AKI_stage']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        #writer.writeheader()
                        for row in xieru:
                            writer.writerow(row)
                    break

                    
           
            if inteval_list == []:
                stage = max(stage_list)
                print("id:", self.idx, "inteval_list: ", None, "AKI stage: ", stage)
            else:
                inteval_min = min(inteval_list)
                inteval_max = max(inteval_list)
                stage = max(stage_list)
                print("id:", self.idx,"inteval_list: ", [inteval_min, inteval_max], "确诊日期为:", inteval_min)
           
      


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
    file_dir2 = 'AKI_simplify2.csv'
    data = pd.read_csv(file_dir2,encoding = 'GB2312')
    id_all = data['subjid'].unique() 
    # 手动输入id
    monitor = AKI_monitor(file_dir = file_dir2, idx = "2100-0298") # 2100-0298
    #monitor.period_monitor_2()
    #monitor.period_monitor_7()
    #input(">>>")
    # 遍历所有id
    for idx in enumerate(id_all):
        #print("############48 hours#####################")
        monitor = AKI_monitor(file_dir = file_dir2, idx = idx[1])
        #monitor.period_monitor_2()
        print("-------------------------------------------------")
        monitor.period_monitor_7()
    '''
    预警功能
    '''

    
    

    
