#!/usr/bin/env python3
from datetime import datetime
from datetime import timedelta
import os
from os import path
import json

csv_path=os.path.dirname(os.path.realpath(__file__))+'/resources.csv'
cpu_count=int(os.popen('cat /proc/cpuinfo | grep -c "proc"').read())
interval=1
io_interval=10

# Replace rekursive all ocurences of original in string with replacement
def replace_all(string : str, original:str,replacement:str):
    while original in string:
        string=string.replace(original,replacement)
    return string

def get_cpu(head:bool=False):
    output=''
    replace_all()
    if head:
        for i in range(0,cpu_count):
            output+=",CPU"+str(i)+" Mhz"
            output+=",CPU"+str(i)+" %user"
            output+=",CPU"+str(i)+" %iowait"
            output+=",CPU"+str(i)+" %steal"
            output+=",CPU"+str(i)+" %idle"
    else:
        data=json.loads(os.popen("mpstat -P ALL -o JSON "+str(interval)+ " 1").read())['sysstat']['hosts'][0]['statistics'][0]['cpu-load']
        mhz=os.popen(' cat /proc/cpuinfo | grep "cpu MHz"').read().split('\n')
        for cpu in range(1,int(cpu_count+1)):
            cpu_data = data[cpu]
            output+=','+replace_all(mhz[cpu-1].split(':')[1],' ','')+',' +str(cpu_data['usr'])+','+str(cpu_data['iowait'])+','+str(cpu_data['steal'])+','+str   (cpu_data['idle'])
    return output

def get_temp(head:bool=False):
    data=os.popen('sensors | grep "Core"').read().split('\n')
    output=""
    for i in range(0,data.__len__()-1):
        if head:
            output+=',temp '+data[i].split(':')[0]
        else:
            output+=','+replace_all(replace_all(data[i].split(':')[1].split('(')[0],' ',''),'°C','')
    return output


def get_mem(head:bool=False):
    if head:
        return ",memory usage,swap usage"
    else:
        data= os.popen("free").read().split('\n')[1:]
        mem_used = replace_all(data[0],'  ',' ').split(" ")[2]
        swap_used= replace_all(data[1],'  ',' ').split(" ")[2]
        return ','+mem_used+','+swap_used

def get_data(head:bool=False):
    time = ""
    if head:
        time="time"
    else:
        time=datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    mem=get_mem(head)
    cpu=get_cpu(head)
    temp=get_temp(head)
    return time+mem+temp+cpu
    

if __name__ == "__main__":
    file = None
    if not path.isfile(csv_path):
        file = open(csv_path,'at')
        head_string=get_data(True)
        

        head_string+='\n'
        file.write(head_string)
    else:
        file = open(csv_path,'at')
    lastflush= datetime.now()
    while True:
        file.write(get_data()+'\n')
        delta=(datetime.now()-lastflush).total_seconds()
        if  delta >= io_interval:
            file.flush()
            lastflush=datetime.now()