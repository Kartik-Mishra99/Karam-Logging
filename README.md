# Karam-Logging



DATA DESCRIPTION -

Input - given a csv file containing logging information of the client on our dashboard. The input file consists of 7 columns - id, sys_info_desktop, sys_info_mobile, ip, login, created_at, email and tableData. But according to our work requirement we need 3 columns that are login, created_at (contains date and time) and email.

PROJECT OBJECTIVE - 
Objective of this projective is to automate the process of logging on a weekly basis i.e, to get a record of all the users (email) and the duration that they spent on our dashboard. We are considering only those users whose login is true in case of blank values in the login column it is considered that the user logged out.

PROJECT APPROACH - 
Approach was to create a python script for performing this task. All the code was written in python programming language using object oriented programming concepts majorly. Different functions are created for handling different operations. The user can choose if we want to get the log details based on previous week or based on past history as overall.
For automation purposes  DOUBT  is used. 

TECHNICAL FEASIBILITY -
The code can be run on windows/Linux/Unix operating systems given the fact you have the right version of python installed. The code is written using python 3 and can be run using a simple command line interface. For running the code you should have - 

*Python 3.7
*Pandas 
*Numpy

Rest it doesn’t have any other specific system requirement.

USAGE - 
Inputs - type of result you want (Users can choose either weekly or overall) and input csv file path.
You can run the code using the command - 
To get weekly logs (from recent monday to previous monday)  run :

`python finalscript.py weekly yourcsvfilename.csv`

To get overall logs grouped week-wise run :

`python finalscript.py overall logs.csv`

Result format - two excel files will be created as output one consisting of normal results and another file consisting of anomalies. A result folder will be created in which 2 subfolders will be present Success and Anomaly consisting of respective result files.

For Anamoly detection these email ids aren't considered - **dashboard@demo.com and sethi.sankalp@karam.in** 
