
# coding: utf-8

# In[588]:

import pandas as pd


# ## Read Network data

# In[589]:

fp_data=r"Input_files/Flowdata.KP"
col_names=['A_node','B_node','data_1','data_2']
col_widths=[5,5,18,10]
data=pd.read_fwf(fp_data,widths=col_widths, names=col_names,delim_whitespace=True)
data[["A_node","B_node"]]=data[["A_node","B_node"]].astype(str)


# In[590]:

data.info()


# In[591]:

data.head()


# ## Read Coordinate data

# In[592]:

fp_coo=r"Input_files/Coords.XY"
col_names=['node','X','Y']
coo=pd.read_csv(fp_coo,names=col_names,skiprows=1,skipfooter=1,engine='python',skipinitialspace=True)


# In[593]:

coo.info()


# In[594]:

coo.tail()


# ## Create first GIS data (straight links)

# In[595]:

straight0=data[["A_node","B_node"]]
straight1=straight0.merge(coo,how="left",left_on="A_node",right_on="node")
straight2=straight0.merge(coo,how="left",left_on="B_node",right_on="node")


# In[596]:

straight=pd.concat([straight1,straight2]).drop(['node'],axis=1).rename_axis({"X":1,"Y":2},axis=1)


# In[597]:

straight.info()


# ## Read GIS data (curvy links)

# In[598]:

fp_gis="Input_files/Network_Shaping.gis"
col_widths=[5,5,10,10,10,10,10,10,10]
gis=pd.read_fwf(fp_gis,widths=col_widths,skiprows=14,skipfooter=2,header=None)


# In[599]:

gis.info()


# In[600]:

gis[11]=gis[0]+gis[1]
gis['key']=gis[0].isnull().cumsum()
gis=gis[[0,1,11,2,3,4,5,6,7,8,'key']]


# In[601]:

gis.head()


# In[602]:

gis_header= gis[gis[0].isnull()]
gis_header=gis_header.drop([0,11,3,4,5,6,7,8],axis=1)
gis_header.columns=["A_node","B_node","key"]
gis=gis.drop([0,1],axis=1)


# In[603]:

gis_header.head()


# In[604]:

gis.head()


# In[605]:

#gis2 = gis_header.merge(gis[gis[11].notnull()], on='key').set_index(["A_node","B_node"])
#gis2.index = gis2.index.map('_'.join)
#gis2=gis2.drop(['key'],axis=1).rename_axis([0]).reset_index()
#gis2=gis2.drop(['key'],axis=1).reset_index()
gis2 = gis_header.merge(gis[gis[11].notnull()], on='key')
gis2=gis2.drop(['key'],axis=1)


# In[606]:

gis2.head()


# In[627]:

gis2.info()


# In[607]:

gis_1=gis2[["A_node","B_node",11,2]].rename_axis({11:1},axis=1)
gis_2=gis2[["A_node","B_node",3,4]].rename_axis({3:1,4:2},axis=1)
gis_3=gis2[["A_node","B_node",5,6]].rename_axis({5:1,6:2},axis=1)
gis_4=gis2[["A_node","B_node",7,8]].rename_axis({7:1,8:2},axis=1)
gis3=pd.concat([gis_1,gis_2,gis_3,gis_4])
gis3.dropna(axis=0, how='any',inplace=True)


# In[608]:

gis3.info()


# In[609]:

gis4=gis3[["B_node","A_node",1,2]].rename_axis({"B_node":"A_node","A_node":"B_node"},axis=1)
gis5=pd.concat([gis3,gis4])


# In[610]:

gis5.info()


# ## Merge data

# In[611]:

direction=data[["A_node","B_node"]]
direction["key"]=direction["A_node"]+"_"+direction["B_node"]


# In[612]:

straight_curvy=pd.concat([straight,gis5])
straight_curvy["key"]=straight_curvy["A_node"]+"_"+straight_curvy["B_node"]


# In[613]:

straight_curvy.info()


# In[614]:

df=direction.merge(straight_curvy,how="left",on="key")


# In[615]:

df.info()


# In[616]:

df=df[['A_node_x','B_node_x',1,2]].rename_axis({'A_node_x':'A_node','B_node_x':'B_node',1:"X",2:"Y"},axis=1)


# In[617]:

df=df.sort_values(['A_node','B_node'], ascending=[True, True]).reset_index(drop=True)


# In[618]:

df.head()


# In[619]:

df['key']=df["A_node"]+"_"+df["B_node"]
data['key']=data["A_node"]+"_"+data["B_node"]
dfdata=df.merge(data,how='left',on='key').drop(['A_node_y','B_node_y'],axis=1).rename_axis({'A_node_x':'A_node','B_node_x':'B_node'},axis=1)


# In[620]:

dfdata.head()


# ## Write MID/MIF files

# In[662]:

df_sub1=dfdata.iloc[:,5:]
df_sub2=dfdata.iloc[:,:2]
df_mid=df_sub2.merge(df_sub1,left_index=True,right_index=True)
df_mid.head()


# In[663]:

#mid:
df_mid.drop_duplicates().to_csv("SATURN_network.MID",index=False,header=False)


# In[664]:

#dfdata=dfdata.set_index(["A_node","B_node"]).sort_index(level=["A_node","B_node"])


# In[665]:

#mif:
with open("SATURN_network.MIF","w") as mid:
    mid.write("Version  1200\nCharset \"WindowsLatin1\"\nDelimiter \",\"\nCoordSys Earth Projection 8, 79, \"m\", -2, 49, 0.9996012717, 400000, -100000 Bounds (-7845061.1011, -15524202.1641) (8645061.1011, 4470074.53373)\nColumns 4\n  A_Node Integer\n  B_Node Integer\n  data_1 Float\n  data_2 Float\nData\n\n")
    gps=dfdata.groupby('key')
    for k,v in gps.groups.iteritems():
        mid.write("Pline "+str(len(v))+"\n")
        for point in v:
            mid.write(" "+(str(dfdata.loc[point,'X'])+" ")[:9]+"  "+str(dfdata.loc[point,'Y'])+"\n")
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



