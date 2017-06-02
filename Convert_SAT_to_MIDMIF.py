
# coding: utf-8

# In[752]:

import pandas as pd
import numpy as np


# ## Read Network data

# In[753]:

fp_data=r"Input_files/Flowdata.KP"
col_names=['A_node','B_node','data_1','data_2']
col_widths=[5,5,18,10]
data=pd.read_fwf(fp_data,widths=col_widths, names=col_names,delim_whitespace=True)
data[["A_node","B_node"]]=data[["A_node","B_node"]].astype(str)
data['key']=data["A_node"]+"_"+data["B_node"]


# In[754]:

data.info()


# In[755]:

data.head()


# ## Read Coordinate data

# In[756]:

fp_coo=r"Input_files/Coords.XY"
col_names=['node','X','Y']
coo=pd.read_csv(fp_coo,names=col_names,skiprows=1,skipfooter=1,engine='python',skipinitialspace=True,comment="*")
coo[["X","Y"]]=coo[["X","Y"]].astype(str)


# In[757]:

coo.info()


# In[758]:

coo.tail()


# ## Create first GIS data (straight links)

# In[759]:

straight0=data[["A_node","B_node"]]
A=straight0.merge(coo,how="left",left_on="A_node",right_on="node").drop(["node"],axis=1)
B=straight0.merge(coo,how="left",left_on="B_node",right_on="node").drop(["node"],axis=1)
A['key']=A["A_node"]+"_"+A["B_node"]
B['key']=B["A_node"]+"_"+B["B_node"]
A['index']=-1
B['index']=999999


# In[760]:

A.head()


# In[761]:

B.info()


# ## Read GIS data (curvy links)

# In[762]:

fp_gis="Input_files/Network_Shaping.gis"
#col_widths=[10,10,10,10,10,10,10,10]
colspecs=[(0,5),(0,10),(10,20),(20,30),(30,40),(40,50),(50,60),(60,70),(70,80)]
gis=pd.read_fwf(fp_gis,colspecs=colspecs,skiprows=14,skipfooter=2,header=None,comment="*",skipinitialspace=True,delim_whitespace=True,na_values="     ")


# In[763]:

gis.info()


# In[764]:

gis['key']=gis[0].isnull().cumsum()
gis=gis[[0,1,2,3,4,5,6,7,8,'key']]


# In[765]:

gis.head()


# In[766]:

gis_header= gis[gis[0].isnull()]
gis_header=gis_header.drop([0,3,4,5,6,7,8],axis=1)
gis_header.columns=["A_node","B_node","key"]
gis_header["A_node"]=gis_header["A_node"].str.strip()
gis_header["B_node"]=gis_header["B_node"].str.strip()


# In[767]:

gis_header.head()


# In[768]:

gis=gis[gis[0].notnull()]


# In[769]:

gis2=gis_header.merge(gis,how="inner",on="key").drop([0,"key"],axis=1)


# In[770]:

gis2.tail()


# In[771]:

gis_1=gis2[["A_node","B_node",1,2]].values.tolist()
gis_2=gis2[["A_node","B_node",3,4]].values.tolist()
gis_3=gis2[["A_node","B_node",5,6]].values.tolist()
gis_4=gis2[["A_node","B_node",7,8]].values.tolist()
gis_f=[None]*len(gis_1)*4
gis_f[::4]=gis_1
gis_f[1::4]=gis_2
gis_f[2::4]=gis_3
gis_f[3::4]=gis_4


# In[772]:

gis10=pd.DataFrame.from_records(gis_f).dropna(axis=0, how='any').rename_axis({0:"A_node",1:"B_node",2:"X",3:"Y"},axis=1)
gis11=gis10[["B_node","A_node","X","Y"]].rename_axis({"B_node":"A_node","A_node":"B_node"},axis=1)
gis11=gis11.iloc[::-1]
gis10.reset_index(inplace=True)
gis11.reset_index(inplace=True,drop=True)
gis11.reset_index(inplace=True)


# In[773]:

gis10.info()


# In[774]:

gis11.head()


# In[775]:

gis=pd.concat([gis10,gis11])
gis['key']=gis["A_node"]+"_"+gis["B_node"]


# In[776]:

gis[["X","Y"]]=gis[["X","Y"]].astype(float)
gis[["X","Y"]]=gis[["X","Y"]].astype(str)


# In[777]:

gis.info()


# In[778]:

gis[gis.loc[:,"key"]=="40526_49991"]#40526_49991


# ## Merge data

# In[779]:

tot=pd.concat([gis,A,B])
tot.head()


# ## Write MID/MIF files

# In[780]:

#mid:
data.iloc[:,:-1].to_csv("SATURN_network.MID",index=False,header=False)


# In[781]:

#dfdata=dfdata.set_index(["A_node","B_node"]).sort_index(level=["A_node","B_node"])


# In[782]:

#mif:
with open("SATURN_network.MIF","w") as mid:
    mid.write("Version  1200\nCharset \"WindowsLatin1\"\nDelimiter \",\"\nCoordSys Earth Projection 8, 79, \"m\", -2, 49, 0.9996012717, 400000, -100000 Bounds (-7845061.1011, -15524202.1641) (8645061.1011, 4470074.53373)\nColumns 4\n  A_Node Integer\n  B_Node Integer\n  data_1 Float\n  data_2 Float\nData\n\n")
    gps=tot.groupby('key')
    for k in data["key"]:
        mid.write("Pline "+str(len(gps.groups[k]))+"\n")
        gp=gps.get_group(k).sort_values(by="index", ascending=True)
        for i,r in gp.iterrows():
            mid.write(" "+(r['X']+" ")[:9]+"  "+r['Y']+"\n")
        mid.write("    Pen (1,2,0)\n")
    mid.close


# ## Verifications

# In[666]:

mid=pd.read_csv('SATURN_network.MID',header=None)
mid.info()


# In[667]:

mif=pd.read_fwf('SATURN_network.MIF',widths=[5],header=None)


# In[668]:

s=mif[0]=="Pline"
s.sum()


# In[ ]:



