# -*- coding: utf-8 -*-
"""Faraday_Prep.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cng9E-Kyw8Wl-zaAro6lIhnZEg80T-X3

# Revenue

## Data Importing - API
"""

# Note: this code was originated by Stephen Sorenson and edited (after he put it together) to complete the project. Many thanks for his work.

# import libraries

import requests
import json
import pandas as pd

# create endpoint for the database
endpoint = 'crm/v3/objects/deals'

key = '3d04d884-7a4d-4a08-ade3-bbe49fce9976'

url = "https://api.hubapi.com/" + endpoint

# create repository for the deals database

deals_df = pd.DataFrame()

after = '0'

while after != 'stop':
  querystring = {"hapikey":key, "properties": ['product_id','dealstage','unit_price','ordered_quantity', 'sales_rep_id', 'amount'],"after":after} #
  headers = {'accept': 'application/json'}

  response = requests.request("GET", url, headers=headers, params=querystring)
  dic = json.loads(response.text)
  dic


  for deal in dic['results']:
    temp_df = pd.DataFrame(deal['properties'], index = [deal['id']])
    deals_df = pd.concat([deals_df, temp_df])

  try:
    after = dic['paging']['next']['after']
  except:
    after = 'stop'

#deals_df

"""


## Data Cleaning"""

# we only care about the deals that actually went through

deals_won_df = deals_df[deals_df['dealstage']=='closedwon']

#Earbuds product ID = 462370
#Watch product ID = 279721
#Monitor product ID = 305973

# create df for each of the products

ebuds_df = deals_won_df[deals_won_df['product_id']=='462370']
watch_df = deals_won_df[deals_won_df['product_id']=='279721']
monitor_df = deals_won_df[deals_won_df['product_id']=='305973']

# calculate the quantity and price

import numpy as np

q_e = np.array(pd.to_numeric(ebuds_df['ordered_quantity'])).reshape(-1, 1)
p_e = np.array(pd.to_numeric(ebuds_df['unit_price'])).reshape(-1, 1)

q_w = np.array(pd.to_numeric(watch_df['ordered_quantity'])).reshape(-1, 1)
p_w = np.array(pd.to_numeric(watch_df['unit_price'])).reshape(-1, 1)

q_m = np.array(pd.to_numeric(monitor_df['ordered_quantity'])).reshape(-1, 1)
p_m = np.array(pd.to_numeric(monitor_df['unit_price'])).reshape(-1, 1)

# plot the distributions of p to q

import matplotlib.pyplot as plt

plt.scatter(p_e,q_e)
plt.scatter(p_w,q_w)
plt.scatter(p_m,q_m)

plt.show()

"""## Analysis"""

# create models for each product

from sklearn.linear_model import LinearRegression

model_e = LinearRegression()
model_e.fit(p_e,q_e)

model_w = LinearRegression()
model_w.fit(p_w,q_w)

model_m = LinearRegression()
model_m.fit(p_m,q_m)

# print coefficients

print(model_e.coef_, model_w.coef_, model_m.coef_)

# print intercepts

print(model_e.intercept_, model_w.intercept_, model_m.intercept_)

# run predictions

price = np.linspace(0,400,100)

eb_quant = model_e.predict(price.reshape(-1, 1))
eb_quant = eb_quant.reshape(len(eb_quant))

w_quant = model_w.predict(price.reshape(-1, 1))
w_quant = w_quant.reshape(len(w_quant))

m_quant = model_m.predict(price.reshape(-1, 1))
m_quant = m_quant.reshape(len(m_quant))

#print(eb_quant, w_quant, m_quant)

# plot the quantity curves
plt.plot(price, eb_quant)
plt.plot(price, w_quant)
plt.plot(price, m_quant)

# create demand curves
eb_demC = pd.DataFrame({'price':price, 'quanity':eb_quant})
eb_demC['predict'] = 'Linnet Bluetooth Earbuds'

w_demC = pd.DataFrame({'price':price, 'quanity':w_quant})
w_demC['predict'] = 'Sidero Smartwatch'

m_demC = pd.DataFrame({'price':price, 'quanity':m_quant})
m_demC['predict'] = 'Vasto Smart Monitor'

# create rev curves
rev_e = price* model_e.predict(price.reshape(-1,1))
rev_w = price* model_w.predict(price.reshape(-1,1))
rev_m = price* model_m.predict(price.reshape(-1,1))

eb_rev = price * eb_quant
w_rev = price * w_quant
m_rev = price * m_quant

# plot curves
plt.plot(price, eb_rev)
plt.plot(price, w_rev)
plt.plot(price, m_rev)

#create the rev curve dfs
revC_eb = pd.DataFrame({'price':price, 'revenue':eb_rev})
revC_eb['product'] = 'Linnet Bluetooth Earbuds'

revC_w = pd.DataFrame({'price':price, 'revenue':w_rev})
revC_w['product'] = 'Sidero Smartwatch'

revC_m = pd.DataFrame({'price':price, 'revenue':m_rev})
revC_m['product'] = 'Vasto Smart Monitor'

"""#Revenue Function"""

# rev optimization
import numpy as np
from sklearn.linear_model import LinearRegression

def revenueOptimizer(deals_won_df,product_id,prdouct_name):

  product_df = deals_won_df[deals_won_df['product_id']==product_id]


  q = np.array(pd.to_numeric(product_df['ordered_quantity'])).reshape(-1, 1)
  p = np.array(pd.to_numeric(product_df['unit_price'])).reshape(-1, 1)
 

  model = LinearRegression()
  model.fit(p,q)

  product_price = np.linspace(0,400,401)
  product_quant = model.predict(product_price.reshape(-1, 1)).reshape(1,-1)[0]
  product_rev = product_price * product_quant

  product_demand = pd.DataFrame({'price':product_price,'quanity': product_quant, 'revenue':product_rev})

  prodcut_max = product_demand[product_demand['revenue'] == product_demand['revenue'].max()]


  product_demand['optimzied_price'] = prodcut_max['price'].iloc[0]
  product_demand['optimzied_quanity'] = prodcut_max['quanity'].iloc[0]
  product_demand['optimzied_revenue'] = prodcut_max['revenue'].iloc[0]

  product_demand['product id'] = product_id
  product_demand['prdouct name'] = prdouct_name

  return(product_demand)

#print for earbuds
revenueOptimizer(deals_won_df, '462370', 'Earbuds')

"""## Export"""

eb_demC.to_csv('EBDemand_Curve.csv', index = False)
w_demC.to_csv('WDemand_Curve.csv', index = False)
m_demC.to_csv('MDemand_Curve.csv', index = False)

revC_eb.to_csv('EBRevenue_Curve.csv', index = False)
revC_w.to_csv('WRevenue_Curve.csv', index = False)
revC_m.to_csv('MRevenue_Curve.csv', index = False)

"""## Other"""

import numpy as np

nuumber_array = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
nuumber_array #1X16 or 1 list of 16

nuumber_array.reshape(4,4) #4X4 or 4 lists of 4

nuumber_array.reshape(2,8) #2X8 or 2 lists of 8

nuumber_array.reshape(16,1) #16X1 or 16 lists of 1

array_2D = nuumber_array.reshape(-1,1) #count of elements X 1 or count of elements lists of 1  
array_2D

array_2D.reshape(1,16) #1 list of 16

array_1D = array_2D.reshape(1,-1) # 1 X count of elements or 1 list of the count of elements 
array_1D

"""# Operations

## SQL Exercise
"""

#save to drive
from google.colab import drive
drive.mount('/content/drive')

cd '/content/drive/MyDrive/Colab Notebooks/STRAT 490R/'

import sqlite3

#create connection to SQL database
cnx = sqlite3.connect('faraday_database.db')

#get employee data
sql = """
select * 
from employees e 
"""

#employee df
df_emp = pd.read_sql(sql,cnx)
df_emp

#input the ids and info from the new table
deals_won_df['sales_rep_id'] = pd.to_numeric(deals_won_df['sales_rep_id'])
deals_won_df['amount'] = pd.to_numeric(deals_won_df['amount'])

DF = deals_won_df.merge(df_emp, how = "left", left_on = 'sales_rep_id', right_on= 'id')
DF

#figure out who's selling the most
DF.groupby(['sales_rep_id','first_name','last_name'])['amount'].max()

"""## Extract from Database"""

from google.colab import drive
drive.mount('/content/drive')

cd '/content/drive/MyDrive/Strat 422 - Advanced Strategy Analytics/2023/Class Content/3.0 Module 1 - Product Diligence/Operation'

import sqlite3
import pandas as pd

cnx = sqlite3.connect('faraday_database.db')

#join the tables to get product and machine part info
sql = """
select pp.product_id, pp.part_id, category, weight, capital_equipment_id  
from parts ps
left join product_parts pp 
	on ps.id = pp.part_id
left join 
	(select product_id, capital_equipment_id 
	from operations o 
	group by product_id) oa
		on oa.product_id = pp.product_id		
			

"""

df_main = pd.read_sql_query(sql,cnx)

df_parts = df_main.pivot_table(index='product_id', columns='category', values = 'weight')

#machine info
df_mech = df_main[['product_id','capital_equipment_id']].groupby(by=['product_id']).mean() #gets only unqiue rows
df_mech

#machine to parts df
df_ready = df_mech.merge(df_parts, left_index= True, right_index=True)
df_ready

df_test = df_ready[df_ready['capital_equipment_id'].isnull()]
df_train = df_ready[df_ready['capital_equipment_id'].notnull()]

#prediction for equipment
df_test

"""## Machine Classification"""

#create decision tree for classification
from sklearn.tree import  DecisionTreeClassifier

y = df_train['capital_equipment_id']
X = df_train.drop(columns=['capital_equipment_id'])

clf = DecisionTreeClassifier().fit(X,y)

X_test = df_test.drop(columns=['capital_equipment_id'])
clf.predict(X_test)

df_test['capital_equipment_id'] = clf.predict(X_test)
df_test

#veiw model
from IPython.display import Image
from sklearn.tree import export_graphviz
import graphviz

dot_data = export_graphviz(clf, out_file=None,
                           feature_names=X.columns, #identifying the explantory columns
                           class_names=['M1','M2','M3'], #identifying the target clasifications
                           filled=True, rounded=True,
                           special_characters=True)



graph = graphviz.Source(dot_data)

Image(graph.render("Faraday", format='png'))

"""## Sankey Query"""

import sqlite3
import pandas as pd

cnx = sqlite3.connect('faraday_database.db')

#model for the Sankey chart
sql = """
select pp.part_id as "Part ID", p.id as "product_id", p.name as "Product", 
	ps.category as "Part Type", ps.costs as "Part Cost", avg_batch_size as "Quantity",
	capital_equipment_id as "Machine", org.name as "Supplier"
from parts ps
left join product_parts pp 
	on ps.id = pp.part_id
left join products p on pp.product_id = p.id 
left join organizations org on ps.supplier_id = org.id	
left join 
	(select product_id, capital_equipment_id, sum(batch_size) as avg_batch_size
	from operations o 
	group by product_id) oa
		on oa.product_id = pp.product_id

"""

df_sankey = pd.read_sql_query(sql,cnx)
df_sankey

"""## Fill Product Data"""

#fill in with the equipment id
right = df_test['capital_equipment_id'].reset_index()
df_sankey = df_sankey.merge(right, how = 'left', on ='product_id') 
df_sankey

df_sankey.loc[df_sankey['Machine'].isnull(),'Machine'] = df_sankey.loc[df_sankey['Machine'].isnull(),'capital_equipment_id']

#discern for each product
df_sankey.loc[df_sankey['product_id'] == 462370,'Quantity'] = round(revenueOptimizer(deals_won_df,'462370','Earbuds')['optimzied_quanity'].iloc[0],0)
df_sankey.loc[df_sankey['product_id'] == 279721,'Quantity'] = round(revenueOptimizer(deals_won_df,'279721','Smartwatch')['optimzied_quanity'].iloc[0],0)
df_sankey.loc[df_sankey['product_id'] == 305973,'Quantity'] = round(revenueOptimizer(deals_won_df,'305973','Smart Monitor')['optimzied_quanity'].iloc[0],0)

df_sankey.loc[df_sankey['Quantity'].isnull(),'Quantity'] = 0

df_sankey['Total Cost'] = df_sankey['Quantity'] * df_sankey['Part Cost']

"""## Sankey"""

#create and export the Sankey chart
df_sankey_t1 = df_sankey.copy()
df_sankey_t1['Table Name'] = 1

df_sankey_t2 = df_sankey.copy()
df_sankey_t2['Table Name'] = 2

DF_sankey = pd.concat([df_sankey_t1, df_sankey_t2])

cd '/content/drive/MyDrive/Colab Notebooks/STRAT 490R/'

DF_sankey.to_csv('Sankey_Chart.csv',index = False)

"""# Market

## Web Scraping
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup

#for the market mapping
url = 'https://stephenms315.github.io/ens/electronicproductreviews'

request = requests.get(url)
source = request.content
soup = BeautifulSoup(source, 'html.parser')

tables = soup.findAll('table', {'class': 'table table-bordered table-hover table-condensed'})

eb_df = pd.read_html(str(tables))[0]
w_df = pd.read_html(str(tables))[1]
m_df = pd.read_html(str(tables))[2]
m_df.head()

# create the dataframes
web_df = pd.DataFrame()
p = 1

for table in tables:
  temp_df = pd.read_html(str(table))[0] #table
  temp_df['Product Type' + str(p)] = 1
  web_df = pd.concat([web_df,temp_df])
  p = p + 1


web_df = web_df.fillna(0)

"""## Standardization"""

from sklearn.preprocessing import MinMaxScaler

df = m_df.copy()

names_col = 'Product'
names = df[names_col]

df_ready = m_df.drop(columns=[names_col])

df_ready

x = MinMaxScaler().fit_transform(df_ready)
x

"""## PCA"""

import seaborn as sns
from sklearn.decomposition import PCA
import numpy as np

#create the principal component analysis
pca = PCA(n_components=2)
model = pca.fit_transform(x)

pca_df = pd.DataFrame(data = model, columns = ['PC1', 'PC2'])
pca_df

#matrix of attributes for each product
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
loading_matrix = pd.DataFrame(loadings, columns=pca_df.columns, index=df_ready.columns)
loading_matrix

loading_matrix.abs().idxmax(1).sort_values()

loading_matrix.abs().idxmax(0).sort_index()

sns.scatterplot(data=pca_df, x='PC1', y='PC2', legend=False)

"""## Clustering"""

from sklearn.cluster import KMeans

X = pca_df

X

#calc sum of squared
Sum_of_squared_distances = []
K = range(2,len(X)-1)
for k in K:
    km = KMeans(n_clusters=k)
    km = km.fit(X)
    Sum_of_squared_distances.append(km.inertia_)

Elbow_df = pd.DataFrame({'K': K, 'SSD': Sum_of_squared_distances})
Elbow_df['Bend'] = Elbow_df['SSD'].shift(1) - Elbow_df['SSD']
Elbow_df

#best number for k
import matplotlib.pyplot as plt
plt.plot(K, Sum_of_squared_distances, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal k')
plt.show()

try:
  k = int(Elbow_df.loc[Elbow_df['Bend'].idxmax()]['K'])
except:
  k = 1
k

km = KMeans(n_clusters=k)
y_km = km.fit_predict(X)
y_km

km_output = df.copy()
km_output['Group'] = y_km
km_output

#product mapping
group_map = pd.merge(km_output, pca_df, how='inner', left_index=True, right_index=True)
group_map

sns.scatterplot(data=group_map , x='PC1', y='PC2', hue = 'Group', legend=False)

"""## Export"""

from google.colab import drive

drive.mount('/content/drive')

cd '/content/drive/MyDrive/Strat 422 - Advanced Strategy Analytics/2023/Class Content/3.0 Module 1 - Product Diligence/Output Data'

group_map.to_csv('m_map.csv',index = False)