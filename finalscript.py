import pandas as pd
from datetime import timedelta
from dateutil.parser import parse
import sys
import numpy as np
import datetime
import argparse

class KaramLogger_overall:
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
        self.data = self.data.sort_values('Date',ascending=True)
        self.data['login'] = self.data['login'].replace(np.NaN,"Logout")
        self.data = self.data[self.data['login']==True]
        return self.data
    
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
        
class Runner:
    def __init__(self,Type,data):
        if Type == "overall":
            karam = KaramLogger_overall(data)
            grouped,Anamoly = karam.runner()
            grouped.to_excel("overall_result.xlsx",index=None)
            Anamoly.to_excel("overall_anamoly.xlsx",index=None)
        
        elif Type == "weekly":
            karam = KaramLogger_weekly(data)
            weekly,Anamoly = karam.runner()
            weekly.to_excel("weekly_result.xlsx",index=None)
            Anamoly.to_excel("weekly_anamoly.xlsx",index=None)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("Type",help="choose yearly/monthly/yearly",type=str)
    parser.add_argument("data",help="enter csv file name",type=str)
    args = parser.parse_args()
    Type = args.Type
    data = args.data

    runner = Runner(Type,data)

        

