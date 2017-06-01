
# coding: utf-8

# In[136]:

import pandas as pd


# ## Read Network data

# In[137]:

fp_data=r"Input_files/Flowdata.KP"
col_names=['A_node','B_node','data_1','data_2']
col_widths=[5,5,18,10]
data=pd.read_fwf(fp_data,widths=col_widths, names=col_names,delim_whitespace=True)
data[["A_node","B_node"]]=data[["A_node","B_node"]].astype(str)


# In[138]:

data.info()


# In[139]:

data.head()


# ## Read Coordinate data

# In[140]:

fp_coo=r"Input_files/Coords.XY"
col_names=['node','X','Y']
coo=pd.read_csv(fp_coo,names=col_names,skiprows=1,skipfooter=1,engine='python',skipinitialspace=True)
coo[["X","Y"]]=coo[["X","Y"]].astype(str)


# In[141]:

coo.info()


# In[142]:

coo.tail()


# ## Create first GIS data (straight links)

# In[143]:

straight0=data[["A_node","B_node"]]
A=straight0.merge(coo,how="left",left_on="A_node",right_on="node").drop(["node"],axis=1)
B=straight0.merge(coo,how="left",left_on="B_node",right_on="node").drop(["node"],axis=1)
A['key']=A["A_node"]+"_"+A["B_node"]
B['key']=B["A_node"]+"_"+B["B_node"]


# In[162]:

A.head(60)


# In[145]:

B.info()


# ## Read GIS data (curvy links)

# In[146]:

fp_gis="Input_files/Network_Shaping.gis"
col_widths=[5,5,10,10,10,10,10,10,10]
gis=pd.read_fwf(fp_gis,widths=col_widths,skiprows=14,skipfooter=2,header=None)


# In[147]:

gis[11]=gis[0]+gis[1]
gis['key']=gis[0].isnull().cumsum()
gis=gis[[0,1,11,2,3,4,5,6,7,8,'key']]


# In[148]:

gis.head()


# In[149]:

gis_header= gis[gis[0].isnull()]
gis_header=gis_header.drop([0,11,3,4,5,6,7,8],axis=1)
gis_header.columns=["A_node","B_node","key"]
gis=gis.drop([0,1],axis=1).rename_axis({11:1},axis=1)


# In[150]:

gis_header.head()


# In[163]:

gis.head()


# In[152]:

gis2 = gis_header.merge(gis[gis[1].notnull()], on='key')
gis2=gis2.drop(['key'],axis=1)#.dropna(axis=0, how='any')


# In[153]:

gis3=gis2[["B_node","A_node",1,2,3,4,5,6,7,8]].rename_axis({"B_node":"A_node","A_node":"B_node"},axis=1)
gis4=pd.concat([gis2,gis3])


# In[154]:

gis4.columns


# In[155]:

#gis4["1"]=gis4[1]+","+gis4[2]
#gis4["2"]=gis4[3]+","+gis4[4]
#gis4["3"]=gis4[5]+","+gis4[6]
#gis4["4"]=gis4[7]+","+gis4[8]
#gis4=gis4.drop([1,2,3,4,5,6,7,8],axis=1)


# In[156]:

gis_1=gis4[["A_node","B_node",1,2]].values.tolist()
gis_2=gis4[["A_node","B_node",3,4]].values.tolist()
gis_3=gis4[["A_node","B_node",5,6]].values.tolist()
gis_4=gis4[["A_node","B_node",7,8]].values.tolist()
gis_f=[None]*len(gis_1)*4
gis_f[::4]=gis_1
gis_f[1::4]=gis_2
gis_f[2::4]=gis_3
gis_f[3::4]=gis_4
gis_f[:3]


# In[157]:

gis=pd.DataFrame.from_records(gis_f).dropna(axis=0, how='any').rename_axis({0:"A_node",1:"B_node",2:"X",3:"Y"},axis=1)
gis['key']=gis["A_node"]+"_"+gis["B_node"]


# In[164]:

gis.head(60)


# ## Merge data

# In[180]:

gps=gis.groupby("key")
li=[]
for i,r in A.iterrows():
    li.append(r.tolist())
    try:
        for ri in gps.groups[r["key"]]:
            li.append(gis.loc[ri,:].tolist())
    except KeyError:
        pass
    li.append(B[B.loc[:,"key"]==r["key"]].values.flatten().tolist()) 


# In[188]:

total=pd.DataFrame(li,columns=["A_node","B_node","X","Y","key"])
total.tail(100)


# ## Write MID/MIF files

# In[ ]:

#mid:
data.to_csv("SATURN_network.MID",index=False,header=False)


# In[186]:

#dfdata=dfdata.set_index(["A_node","B_node"]).sort_index(level=["A_node","B_node"])


# In[187]:

#mif:
with open("SATURN_network.MIF","w") as mid:
    mid.write("Version  1200\nCharset \"WindowsLatin1\"\nDelimiter \",\"\nCoordSys Earth Projection 8, 79, \"m\", -2, 49, 0.9996012717, 400000, -100000 Bounds (-7845061.1011, -15524202.1641) (8645061.1011, 4470074.53373)\nColumns 4\n  A_Node Integer\n  B_Node Integer\n  data_1 Float\n  data_2 Float\nData\n\n")
    gps=total.groupby('key')
    for k,v in gps.groups.iteritems():
        mid.write("Pline "+str(len(v))+"\n")
        for index in v:
            mid.write(" "+(total.loc[index,'X']+" ")[:9]+"  "+total.loc[index,'Y']+"\n")
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



