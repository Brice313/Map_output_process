
# coding: utf-8

# In[63]:

from __future__ import print_function
import os


# ### Code for SATDB
# Link:  
# FF speed=5  
# V/C=12  
# Delay=14  
# Cruise Time=15  
# Tot Time=17  
# Actual Flow=24  
# Distance=6  
# 
# Node:  
# V/C=2  
# Delay Time=3  
# Arrive Flow=5  
# 

# In[1]:

def create_key_link(s_UC,l_data,s_fp):
    """Create a key file to be run with P1X to extract LINK data, specify a UC and a list of the data number 
        as well as the filepath of the output file"""
    with open("temp.key","w") as f:
        f.write("      1724       439   66    0  SATDB Opts     (Pixels/key/status/Line)     6001\n           4                                                                6800\n           1                                                                6820\n         201                                                                6801\n           "+(2*" "+s_UC)[-3:]+"                                                                6802\n")
        ##   
        for data in l_data:
            f.write("          "+(2*" "+data)[-3:]+"                                                                 6801\n")
        ##
        f.write("           0                                                                6801\n          13                                                                6800\n           1                                                                7530\n           0                                                                7530\n"+
s_fp+"\n\
Y\n\
           0                                                                6800\n\
      1538       752   81    0  Quit = Exit    (Pixels/key/status/Line)     6001\n\
Yes OK to exit the program?")
        f.close


# In[2]:

def create_key_node(l_data,s_fp):
    """Create a key file to be run with P1X to extract NODE data, specify a list of the data number 
        as well as the filepath of the output file"""
    with open("temp.key","w") as f:
        f.write("  1724       439   66    0  SATDB Opts     (Pixels/key/status/Line)     6001\n      18                                                                6800\n       4                                                                6800\n")
    ##
        for data in l_data:
            f.write("       1                                                                7300\n      "+(2*" "+data)[-3:]+"                                                                 6801\n")
    ##
        f.write("       0                                                                6801\n      13                                                                6800\n       0                                                                7530\n"+
s_fp+"\n\
Y\n\
       0                                                                6800\n\
  1538       752   81    0  Quit = Exit    (Pixels/key/status/Line)     6001\n\
Yes OK to exit the program?")
        f.close


# In[3]:

def create_bat(model,key,sat_path):
    """Creates a batch file which runs P1X from a given SATURN folder, using a key file and then do some housekeeping """
    with open("run.bat","w") as f:
        f.write("@ECHO OFF\nSET PATH="+sat_path+"\n\n$P1X "+model+" "+key+".key VDU VDU\n\nIF EXIST *.VDU DEL *.VDU\nIF EXIST *.LOG DEL *.LOG\nIF EXIST *.LPP DEL *.LPP\nIF EXIST *.CTL DEL *.CTL")
        f.close


# In[4]:

def Main():
    s_UC="0"
    s_fp=r"C:\Users\ChanNgYokB1\Documents\stuff.csv"
    l_data=["13","14"]
    create_key_link(s_UC,l_data,s_fp)
    
    model="2014_Base_AM"
    sat_path=r"P:\UKSTA1-TP-Planning\Projects\Transport Planning - LLITM\Applications\Melton Mowbray EDR\10 Technical\Stage 3 - Update OAR\Analysis\CordonOutputProcess\SATURN_11312U"

    create_bat(model,"temp",sat_path)
    
    #os.system("run.bat")
    #os.remove("temp.key")
    #os.remove("run.bat")


# In[5]:

if __name__ == "__main__":
    Main()


# In[ ]:



