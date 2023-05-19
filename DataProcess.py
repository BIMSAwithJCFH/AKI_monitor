#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 14 21:28:09 2023

@author: yangwuyue
"""

import pandas as pd
import numpy as np
import datetime

# 明确每个患者住院的天数和首次住院时期, 确定起始日期和结束日期
class AKI_simplify():

    def __init__(self, file_dir):
        
        self.olddata = pd.read_csv(file_dir,encoding = 'GBK')  
        self.data = self.olddata[['subjid','test_date','test_result','sex','age']]


    def data_process(self):
        
        if self.data['sex'][0] == 1:
            self.scr = (75/(186*(self.data['age']**-0.203)))**-0.867*88.4
        elif self.data['sex'][0] == 2:
            self.scr = (75/(186*(self.data['age']**-0.203)*0.742))**-0.867*88.4

        #self.scr = (75 / (186 * (self.data['age'] ** (-0.203)))) ** (-0.867) * 88.4
        self.data.insert(self.data.shape[1], 'scr', self.scr)
        #print(self.data['test_date'])
        self.data['id_minday'] = self.data.groupby('subjid')['test_date'].transform('min')
        def interval(series):
            id_minday = series["id_minday"]
            startTime = datetime.datetime.strptime(id_minday, "%Y/%m/%d")
            days_from_admission = series["test_date"]
            endTime = datetime.datetime.strptime(days_from_admission, "%Y/%m/%d")
            day = (endTime - startTime).days
            interval = day 
            return interval
        self.data["day_interval"] = self.data.apply(interval,axis=1)
        #self.id_minday = self.data.groupby('subjid').agg({'days_from_admission':'min'})
        self.data.to_csv('AKI_simplify.csv')

if __name__ == '__main__':
    
    '''
    读取表格
    '''
    file_dir1 = 'AKI_0513.csv'
    aki = AKI_simplify(file_dir = file_dir1)
    aki.data_process()