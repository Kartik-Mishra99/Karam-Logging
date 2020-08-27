import pandas as pd
from datetime import timedelta
from dateutil.parser import parse
import sys

class KaramLogger:
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
    
    def runner(self):
        preprocesseddata = self.preprocess()
        for (a,b) in zip(preprocesseddata['Year'],preprocesseddata['Week']):
            self.get_start_end_dates(a,b)
        preprocesseddata['StartDate'] = self.startdates
        preprocesseddata['EndDate'] = self.enddates
        preprocesseddata['login'] = preprocessed['login'].replace(np.NaN,"Logout")
#         preprocesseddata = preprocesseddata[preprocesseddata['login']==True]
        grouped = preprocesseddata.groupby(['StartDate','EndDate','email'])['Hour','Minutes','Seconds'].sum().reset_index()
        grouped['Hour'] = grouped['Hour'].apply(lambda x:x*3600)
        grouped['Minutes'] = grouped['Minutes'].apply(lambda x: x*60)
        grouped['TotalSeconds'] = [a+b+c for a,b,c in zip(grouped['Hour'],grouped['Minutes'],grouped['Seconds'])]
        grouped.drop(columns=['Hour','Minutes','Seconds'],axis=1,inplace=True)
        grouped['TimeSpent'] = self.gettotaltime(grouped)
        grouped.drop(columns=['TotalSeconds'],axis=1,inplace=True)
        return grouped
        

if __name__=="__main__":
    karam = KaramLogger("logs.csv")
    result = karam.runner()
    result.to_excel("result.xlsx",index=None)
