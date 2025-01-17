import pandas as pd
from datetime import timedelta
from dateutil.parser import parse
import sys
import numpy as np
import datetime
import argparse
from time import gmtime, strftime

'''
This class is used to get the overall result values from the log file
'''

class KaramLogger_overall:
    def __init__(self,data):
        self.dataframe = data
        self.data = pd.read_csv(self.dataframe) # reading the csv log file 
        self.data = self.data[["email","created_at",'login']]
        self.startdates = []
        self.enddates = []

    '''this function is used for preprocessing purposes. It first reads the date column and converts it into
    required datetime followed by extraction of hour,minutes and seconds from the date column,
    also it filters only those rows where login is true and replace blank login entries with logout'''  
    def preprocess(self):
        dates = []
        time = []
        for i in list(self.data['created_at']):
            dates.append(i.split("T")[0])
        
        for i in list(self.data['created_at']):
            t = i.split("T")[1].split(".")[0]
            time.append(t)
        self.data['Time'] = time
        self.data['Date'] = dates
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.data[['Hour','Minutes','Seconds']] = self.data['Time'].astype(str).str.split(':', expand=True).astype(int)
        self.data.drop(columns=['created_at'],inplace=True)
        self.data["Week"] = pd.DatetimeIndex(self.data['Date']).week
        self.data['Year'] = pd.DatetimeIndex(self.data['Date']).year
        self.data = self.data.sort_values('Date',ascending=True)
        self.data['login'] = self.data['login'].replace(np.NaN,"Logout")
        self.data = self.data[self.data['login']==True]
        return self.data
    '''This function is used to get the start and end date for each date value of date column'''
    def get_start_end_dates(self,year,week):
        first_day_year = str(year) + '-' +  '01' + '-' + '01'
        d = parse(first_day_year)
        if(d.weekday()<= 3):
            d = d - timedelta(d.weekday())             
        else:
            d = d + timedelta(7-d.weekday())
        dlt = timedelta(days = (int(week)-1)*7)
        self.startdates.append((d + dlt).strftime('%Y-%m-%d'))
        self.enddates.append((d + dlt + timedelta(days=6)).strftime('%Y-%m-%d'))

    '''This function is used to get the total time a person spend on dashboard''' 
    def gettotaltime(self,data):
        time = []
        for i in data['TotalSeconds']:     
            mini, sec = divmod(i, 60)
            hour, mini = divmod(mini, 60)
            t = "%d:%02d:%02d" % (hour, mini, sec)
            time.append(t)
        return time 

    '''This function is used for filtering our anomaly values i.e., those rows whose total time in seconds
    is more than duration of week (604800 seconds) also it is filtering out some email ids that shouldn't
    be considered in final results'''
    def findAnomaly(self,grouped):
        grouped['Anomaly'] = grouped['TotalSeconds'].map(lambda x: "Anomaly" if x>604800 else "Non-Anomaly")
        Anomaly = grouped[grouped['Anomaly']=='Anomaly']
        ignoremails = ['dashboard@demo.com','sethi.sankalp@karam.in'] # ignore these mails
        Anomaly = Anomaly.loc[~Anomaly.email.isin(ignoremails)]
        return Anomaly

    '''
    this runner function is using all the other defined functions for finally performing the actual task 
    of getting the result in desired format we are using group by method of pandas to get the result
    we are first grouping on startdate and enddate column followed by email to get the desired entries also 
    we are taking care of anamolies.    
    '''

    def runner(self):
        preprocesseddata = self.preprocess()
        for (a,b) in zip(preprocesseddata['Year'],preprocesseddata['Week']):
            self.get_start_end_dates(a,b)
        preprocesseddata['StartDate'] = self.startdates
        preprocesseddata['EndDate'] = self.enddates
        grouped = preprocesseddata.groupby(['StartDate','EndDate','email'])['Hour','Minutes','Seconds'].sum().reset_index()
        grouped['Hour'] = grouped['Hour'].apply(lambda x:x*3600)
        grouped['Minutes'] = grouped['Minutes'].apply(lambda x: x*60)
        grouped['TotalSeconds'] = [a+b+c for a,b,c in zip(grouped['Hour'],grouped['Minutes'],grouped['Seconds'])]
        grouped.drop(columns=['Hour','Minutes','Seconds'],axis=1,inplace=True)
        grouped['TimeSpent'] = self.gettotaltime(grouped)
        Anamoly = self.findAnomaly(grouped)
        grouped.drop(columns=['TotalSeconds'],axis=1,inplace=True)
        grouped = grouped[::-1]
        grouped = grouped[['StartDate','EndDate','email','TimeSpent']]
        return grouped,Anamoly

'''This class is used to get result values of only last week almost all the steps are same
as performed above ! we are just using a new function by name of "getrecentweekdetails" for retrieving
the details of logins from last week's monday '''

class KaramLogger_weekly:
    def __init__(self,data):
        self.dataframe = data
        self.data = pd.read_csv(self.dataframe)
        self.data = self.data[["email","created_at",'login']]
        self.startdates = []
        self.enddates = []
        
    def preprocess(self):
        dates = []
        time = []
        for i in list(self.data['created_at']):
            dates.append(i.split("T")[0])
        
        for i in list(self.data['created_at']):
            t = i.split("T")[1].split(".")[0]
            time.append(t)
        self.data['Time'] = time
        self.data['Date'] = dates
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.data[['Hour','Minutes','Seconds']] = self.data['Time'].astype(str).str.split(':', expand=True).astype(int)
        self.data.drop(columns=['created_at'],inplace=True)
        self.data["Week"] = pd.DatetimeIndex(self.data['Date']).week
        self.data['Year'] = pd.DatetimeIndex(self.data['Date']).year
        self.data['Day'] = pd.DatetimeIndex(self.data['Date']).dayofweek
        self.data = self.data.sort_values('Date',ascending=True)
        self.data['login'] = self.data['login'].replace(np.NaN,"Logout")
        self.data = self.data[self.data['login']==True]
        return self.data
    
    def gettotaltime(self,data):
        time = []
        for i in data['TotalSeconds']:     
            mini, sec = divmod(i, 60)
            hour, mini = divmod(mini, 60)
            t = "%d:%02d:%02d" % (hour, mini, sec)
            time.append(t)
        return time    
    
    def findAnomaly(self,grouped):
        grouped['Anomaly'] = grouped['TotalSeconds'].map(lambda x: "Anomaly" if x>604800 else "Non-Anomaly")
        Anomaly = grouped[grouped['Anomaly']=='Anomaly']
        ignoremails = ['dashboard@demo.com','sethi.sankalp@karam.in'] # ignore these mails
        Anomaly = Anomaly.loc[~Anomaly.email.isin(ignoremails)]
        return Anomaly
        
    '''
    This function is used to get the result values from only last week based on current date it aims to
    get the result values based on last monday
    '''
    def getrecentweekdetails(self,grouped):
        grouped['Day'] = grouped['Date'].dt.dayofweek
        grouped['DayName'] = grouped['Day'].map({0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"})
        filter = grouped["Day"]==0
        onlymonday = grouped.head().where(filter)
        onlymonday.dropna(inplace=True)
        recentmonday = onlymonday['Date']
        lastmonday = pd.to_datetime(recentmonday)-datetime.timedelta(days=7)
        recentmonday = str(recentmonday).split()[1]
        lastmonday = str(lastmonday).split()[1]
        mask = (grouped['Date'] > lastmonday) & (grouped['Date'] <= recentmonday)
        grouped = grouped[mask]
        grouped = grouped.drop(columns=['Day','DayName'],axis=1)
        return grouped
    
    def runner(self):
        preprocesseddata = self.preprocess()
        grouped = preprocesseddata.groupby(['Date','email'])['Hour','Minutes','Seconds'].sum().reset_index()
        grouped['Hour'] = grouped['Hour'].apply(lambda x:x*3600)
        grouped['Minutes'] = grouped['Minutes'].apply(lambda x: x*60)
        grouped['TotalSeconds'] = [a+b+c for a,b,c in zip(grouped['Hour'],grouped['Minutes'],grouped['Seconds'])]
        grouped.drop(columns=['Hour','Minutes','Seconds'],axis=1,inplace=True)
        grouped['TimeSpent'] = self.gettotaltime(grouped)
        Anamoly = self.findAnomaly(grouped)
        Anamoly = Anamoly[['Date','email','TimeSpent','Anomaly']] # we don;t want total seconds column here 
        grouped.drop(columns=['TotalSeconds'],axis=1,inplace=True)
        grouped = grouped[::-1]
        pastweekdata = self.getrecentweekdetails(grouped)   
        pastweekdata = pastweekdata[['Date','email','TimeSpent']]
        pastweekdata = pastweekdata[::-1]
        return pastweekdata,Anamoly
        
'''
This Runner class is built to bring the code into action based on the user input (weekly or overall)
it runs the above classes and generates the result into excel file format
'''
class Runner:
    def __init__(self,Type,data):
        
        self.now = str(strftime("%Y-%m-%d_%H:%M:%S", gmtime()))
        # self.now = str(datetime.date.today().strftime('%Y-%m-%d %H:%M:%S'))
        if Type == "overall":
            karam = KaramLogger_overall(data)
            grouped,Anamoly = karam.runner()
            grouped.to_excel("./Result/Success/overall_result_{}.xlsx".format(self.now).replace(':', '.'),index=None)
            Anamoly.to_excel("./Result/Anamoly/overall_anamoly_{}.xlsx".format(self.now).replace(':', '.'),index=None)
        
        elif Type == "weekly":
            karam = KaramLogger_weekly(data)
            weekly,Anamoly = karam.runner()
            weekly.to_excel("./Result/Success/weekly_result_{}.xlsx".format(self.now).replace(':', '.'),index=None)
            Anamoly.to_excel("./Result/Anamoly/weekly_anamoly_{}.xlsx".format(self.now).replace(':', '.'),index=None)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--Type",help="choose weekly or overall",type=str,default='weekly')
    parser.add_argument("--data",help="enter csv file name",type=str,default='./data/logs.csv')
    args = parser.parse_args()
    Type = args.Type
    data = args.data

    runner = Runner(Type,data)

        

