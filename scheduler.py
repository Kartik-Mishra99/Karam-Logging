import os
import pandas as pd
from datetime import timedelta
from dateutil.parser import parse
import sys
import numpy as np
import datetime
import argparse
import schedule
from finalscript import Runner
from time import gmtime, strftime


def schedulerfunc(Type="weekly",data="./data/logs.csv"):
    runner = Runner(Type,data)

if __name__=="__main__":   

    parser = argparse.ArgumentParser()
    parser.add_argument("--Type",help="choose weekly or overall",type=str,default='weekly')
    parser.add_argument("--data",help="enter csv file name",type=str,default='./data/logs.csv')
    args = parser.parse_args()
    Type = args.Type
    data = args.data

    schedule.every(15).seconds.do(schedulerfunc,Type=Type,data=data)
    while 1:
        schedule.run_pending()

