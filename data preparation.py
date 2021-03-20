#!/usr/bin/env python
# coding: utf-8

# Data preparation and customer analytics 

# In[1]:


import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import datetime as dt
import warnings
warnings.filterwarnings('ignore')
import numpy as np


# Import The Customer Purchase Data

# In[2]:


purchase = pd.read_csv('QVI_purchase_behaviour.csv')
purchase.reset_index(inplace=True)
purchase = purchase.rename(columns={'level_0':'LYLTY_CARD_NBR','level_1':'LIFESTAGE','QVI_purchase_behaviour':'PREMIUM_CUSTOMER'} )
purchase = purchase.drop(index = 0)
purchase.reset_index(drop=True)
purchase = purchase.astype({'LYLTY_CARD_NBR': 'int64'},copy=True)
print(purchase.head(10))


# **Data exploration**
# **Examining the customer data**

# In[3]:


lifestage = purchase.groupby(['LIFESTAGE']).count().reset_index()
lifestage = lifestage.sort_values(by = ['LYLTY_CARD_NBR'], ascending=False)
print(lifestage)
lifestagecustomer = lifestage['LIFESTAGE'].values
lifestagecount = lifestage['LYLTY_CARD_NBR'].values
explode = (0.1,0.1,0,0,0,0,0)
plt.figure(figsize = (10,8))
plt.pie(lifestagecount,labels = lifestagecustomer,autopct = '%d%%', explode=explode,shadow=True)
plt.axis('equal')
plt.title('Distribution of The Customer Lifestage',fontsize = 18)
plt.show()


# In[4]:


premium = purchase.groupby(['PREMIUM_CUSTOMER']).count().reset_index()
premium = premium.sort_values(by = ['LYLTY_CARD_NBR'], ascending=False)
print(premium)
Premiumcustomer = premium['PREMIUM_CUSTOMER'].values
premiumcount = premium['LYLTY_CARD_NBR'].values
explode = (0.1,0,0)
plt.figure(figsize = (10,8))
plt.pie(premiumcount,labels = Premiumcustomer,autopct = '%d%%', explode=explode,shadow=True)
plt.axis('equal')
plt.title('Distribution of The Customer Segement',fontsize = 18)
plt.show()


# Import The Transaction Data
# change excel int into date

# In[5]:


transaction = pd.read_csv('QVI_transaction_data.csv')
transaction['DATE'] = pd.TimedeltaIndex(transaction['DATE'], unit='d') + dt.datetime(1899, 12, 30)
transaction = transaction.sort_values(by=['DATE'])
product_list = transaction.groupby(['PROD_NAME']).count().reset_index()
print(product_list)


# **Examining the transaction data**

#  check whether non-chips products are in the list 

# In[6]:


transaction = transaction[~transaction['PROD_NAME'].str.contains('Salsa')]
print(transaction.head(10))


# remove salsa

# Let see is there any outliers.

# In[7]:


transaction.describe()


# the maximum of product quantity could be an outlier.

# In[8]:


transaction.loc[transaction['PROD_QTY'] == 200]
transaction.loc[transaction['LYLTY_CARD_NBR'] == 226000]


# There are only two transaction for this customer so this is not an ordinary transaction habit so we drop the row 

# In[9]:


transaction = transaction[transaction['LYLTY_CARD_NBR'] != 226000]
transaction.describe()


# In[10]:


Daily_transaction = transaction.groupby(['DATE'])['TXN_ID'].count().reset_index()
Daily_transaction = Daily_transaction.set_index(pd.DatetimeIndex(Daily_transaction['DATE'].values))
print(Daily_transaction)
x = Daily_transaction.index
y = Daily_transaction['TXN_ID']
plt.figure(figsize = (10,8))
plt.plot(x,y)
plt.show()


# We can see that there is a dramatically increase in December and this is because of Christmas.

# Create a new column of size 

# In[11]:


transaction['Size'] = transaction['PROD_NAME'].str.extract('(\d+)')
transaction = transaction.astype({'Size': 'int64'},copy=True)
print(transaction)
transaction['Size'].describe()


# Lets see the frequency of different package size 

# In[12]:


size = transaction.groupby(['Size'])['PROD_NAME'].count().reset_index()
size = size.rename(columns = {'PROD_NAME':'Frequency'})
print(size)


# In[13]:


plt.hist(transaction['Size'],bins = 20, edgecolor='black')
plt.title("Distribution of PackageSize", fontsize = 16)
plt.xlabel("Packagesize", fontsize = 16)
plt.ylabel("Frequency", fontsize = 16)


# The largest size is 380g and the smallest size is 70g

# Lets rename the brand name 

# In[14]:


transaction["Brand"]= transaction["PROD_NAME"].str.split(" ",1).str[0]
print(transaction)


# In[15]:


brand  = transaction.groupby(["Brand"]).count().reset_index()
brand = brand.sort_values(by=['Brand'])
print(brand)


# Seems like there are some brands are written by different name 
# lets rename them 

# In[16]:


transaction.loc[transaction["Brand"] == 'Doritos'] = 'Dorito'
transaction.loc[transaction["Brand"] == 'GrnWves'] = 'Grain'
transaction.loc[transaction["Brand"] == 'Infzns'] = 'Infuzions'
transaction.loc[transaction["Brand"] == 'NCC'] = 'Natural'
transaction.loc[transaction["Brand"] == 'RRD'] = 'Red'
transaction.loc[transaction["Brand"] == 'Smiths'] = 'Smith'
transaction.loc[transaction["Brand"] == 'Snbts'] = 'Woolworths'
transaction.loc[transaction["Brand"] == 'WW'] = 'WW'
brand  = transaction.groupby(["Brand"]).count().reset_index()
brand = brand.sort_values(by=['Brand'])
print(brand)


# **Merge two Data**

# In[17]:


new_data = pd.merge(transaction,purchase,how = 'left')
new_data = new_data.dropna()
print(new_data.head())


# In[18]:


new_data['TOT_SALES'] = pd.to_numeric(new_data['TOT_SALES'])
print(new_data.head())


# **Data analysis on customer segments**

# After the cleaning the data,,we can define some metrics of interest to the client:
# 1.Which customer segement spends the most on chips(describing by lifestage and how premium their purchasing bahaviour is)
# 2.How many customers are in each segment
# 3.How mant chip are bought per customer by segment
# 4.Whats the average chip price by customer segment 
# Futher discussion
# 1.What is the spending proportion on chip over the whole grocery spending

# In[19]:


life_premium = new_data.groupby(['LIFESTAGE','PREMIUM_CUSTOMER'])['TOT_SALES'].sum().unstack()
print(life_premium)
Lifestage = ['MIDAGE SINGLES/COUPLES','NEW FAMILIES','OLDER FAMILIES','OLDER SINGLES/COUPLES','RETIREES','YOUNG FAMILIES','YOUNG SINGLES/COUPLES']
Budget = life_premium['Budget']
Mainstream = life_premium['Mainstream']
Premium = life_premium['Premium']
Total_sales = new_data['TOT_SALES'].sum()
x = range(7)
pre_bottom = np.add(Budget,Mainstream)
plt.figure(figsize = (10,8))
plt.bar(x,Budget)
plt.bar(x,Mainstream,bottom = Budget)
plt.bar(x,Premium,bottom = pre_bottom)
ax = plt.subplot()
plt.xticks(rotation=90)
ax.set_xticks(range(len(Lifestage)))
ax.set_xticklabels(Lifestage)
for rect in ax.patches:
    # Find where everything is located
    height = rect.get_height()
    width = rect.get_width()
    x = rect.get_x()
    y = rect.get_y()
    
    # The height of the bar is the data value and can be used as the label
    label_text = f'{round(((height/Total_sales)*100),2)}%'  # f'{height:.2f}' to format decimal values
    
    # ax.text(x, y, text)
    label_x = x + width / 2
    label_y = y + height / 2

    # plot only when height is greater than specified value
    if height > 0:
        ax.text(label_x, label_y, label_text, ha='center', va='center', fontsize=8)
plt.legend(['Budeget','Mainstream','Premium'])
plt.title('Sales distribution',fontsize = 18)
plt.xlabel('Type of Customers',fontsize = 18)
plt.ylabel('Sales',fontsize = 18)
plt.show()


# Therefore,our sales are coming mainly from Budget-older families,Mainstream -retirees and Mainstream - Young Singles/couples.
# Lets see is this due to the number of customer in these segement 

# In[20]:


life_premium_count = new_data.groupby(['LIFESTAGE','PREMIUM_CUSTOMER'])['LYLTY_CARD_NBR'].nunique().unstack()
print(life_premium_count)


# In[21]:


Life = ['MIDAGE SINGLES/COUPLES','NEW FAMILIES','OLDER FAMILIES','OLDER SINGLES/COUPLES','RETIREES','YOUNG FAMILIES','YOUNG SINGLES/COUPLES']
Budget_count = life_premium_count['Budget']
Mainstream_count = life_premium_count['Mainstream']
Premium_count = life_premium_count['Premium']
Total_count = new_data['LYLTY_CARD_NBR'].nunique()
print(Total_count)
x = range(7)
pre_bottom_count = np.add(Budget_count,Mainstream_count)
plt.figure(figsize = (10,8))
plt.bar(x,Budget_count)
plt.bar(x,Mainstream_count,bottom = Budget_count)
plt.bar(x,Premium_count,bottom = pre_bottom_count)
ax1 = plt.subplot()
plt.xticks(rotation=90)
ax1.set_xticks(range(len(Lifestage)))
ax1.set_xticklabels(Life)
for rect in ax1.patches:
    # Find where everything is located
    height = rect.get_height()
    width = rect.get_width()
    x = rect.get_x()
    y = rect.get_y()
    
    # The height of the bar is the data value and can be used as the label
    label_text = f'{round(((height/Total_count)*100),2)}%'  # f'{height:.2f}' to format decimal values
    
    # ax.text(x, y, text)
    label_x = x + width / 2
    label_y = y + height / 2

    # plot only when height is greater than specified value
    if height > 0:
        ax1.text(label_x, label_y, label_text, ha='center', va='center', fontsize=8)
plt.legend(['Budeget','Mainstream','Premium'])
plt.title('Cutomers distribution',fontsize = 18)
plt.xlabel('Type of Customers',fontsize = 18)
plt.ylabel('Count',fontsize = 18)
plt.show()


# From the above chart,we can see that there are more Mainstream - Young Singles/couples and Mainstream-retiress buy chips therefore this contribute to the reason why there are more sales to these customer but this is not the major driver for for the Budget- Older families segment.

# Higer sales might also due to the more units of chips being bought per customer

# In[22]:


chips_per_customers = new_data.groupby(['LIFESTAGE','PREMIUM_CUSTOMER'])['PROD_QTY'].sum().unstack()
chips_per_customers = chips_per_customers/life_premium_count
print(chips_per_customers)
ax2 = chips_per_customers.plot.bar(figsize = (10,8))
ax2.legend(['Budeget','Mainstream','Premium'])
ax2.set_title('Unit per Cutomers ',fontsize = 18)
ax2.set_xlabel('Type of Customers',fontsize = 18)
ax2.set_ylabel('Unit',fontsize = 18)


# Therefore older family and young family are generally buying more chips

# **Investigating Sales per Customers**

# In[23]:


sales_per_customers = new_data.groupby(['LIFESTAGE','PREMIUM_CUSTOMER'])['TOT_SALES'].sum().unstack()
sales_per_customers = sales_per_customers/life_premium_count/chips_per_customers
print(sales_per_customers)


# In[24]:


ax3 = sales_per_customers.plot.bar(figsize = (10,8))
ax3.legend(['Budeget','Mainstream','Premium'])
ax3.set_title('price per Cutomers spent on an unit chip ',fontsize = 18)
ax3.set_xlabel('Type of Customers',fontsize = 18)
ax3.set_ylabel('Sales',fontsize = 18)


# Mainstream - midage and young singles and couples are more willing to pay more per packet of chips compared to their budget and premium counterparts.
# This may due to their premium counterpart are more willing to buy healthy grocery while budge counterparts prefer buying necessities.

# **Deep dive into specific customer segments for insights**
#  Budget-older families,Mainstream -retirees and Mainstream - Young Singles/couples.

# In[25]:


Budget_older_families = new_data.loc[(new_data['PREMIUM_CUSTOMER'] == 'Budget') & (new_data['LIFESTAGE'] == 'OLDER FAMILIES')]
print(Budget_older_families)


# In[26]:


Budget_older_families_count = Budget_older_families.groupby(['Brand'])['PROD_QTY'].sum().reset_index()
Budget_older_families_count = Budget_older_families_count.sort_values(by = ['PROD_QTY'], ascending=False)
Budget_older_families_count['PROD_QTY'] = (Budget_older_families_count['PROD_QTY']/Budget_older_families_count['PROD_QTY'].sum())*100

print(Budget_older_families_count)


# We can see that the Budget-older families more likely to purchase Kettle and least likely to purchase Sunbites.

# In[27]:


Budget_older_families_size = Budget_older_families.groupby(['Size'])['PROD_QTY'].sum().reset_index()
Budget_older_families_size = Budget_older_families_size.sort_values(by = ['PROD_QTY'], ascending=False)
Budget_older_families_size['PROD_QTY'] = (Budget_older_families_size['PROD_QTY']/Budget_older_families_size['PROD_QTY'].sum())*100

print(Budget_older_families_size)


# We can see that the Budget-older families most likely to purchase 175g and least likely to purchase 70g.

# In[28]:


Mainstream_retirees = new_data.loc[(new_data['PREMIUM_CUSTOMER'] == 'Mainstream') & (new_data['LIFESTAGE'] == 'RETIREES')]
print(Mainstream_retirees.head())


# In[29]:


Mainstream_retirees_count = Mainstream_retirees.groupby(['Brand'])['PROD_QTY'].sum().reset_index()
Mainstream_retirees_count = Mainstream_retirees_count.sort_values(by = ['PROD_QTY'], ascending=False)
Mainstream_retirees_count['PROD_QTY'] = (Mainstream_retirees_count['PROD_QTY']/Mainstream_retirees_count['PROD_QTY'].sum())*100

print(Mainstream_retirees_count)


# We can see that the Mainstrean-retirees more likely to purchase Kettle and least likely to purchase French.

# In[30]:


Mainstream_retirees_size = Mainstream_retirees.groupby(['Size'])['PROD_QTY'].sum().reset_index()
Mainstream_retirees_size = Mainstream_retirees_size.sort_values(by = ['PROD_QTY'], ascending=False)
Mainstream_retirees_size['PROD_QTY'] = (Mainstream_retirees_size['PROD_QTY']/Mainstream_retirees_size['PROD_QTY'].sum())*100

print(Mainstream_retirees_size)


# We can see that the Mainstrean-retirees most likely to purchase 175g and least likely to purchase 90g.

# In[31]:


Mainstream_Young_Singles_couples = new_data.loc[(new_data['PREMIUM_CUSTOMER'] == 'Mainstream') & (new_data['LIFESTAGE'] == 'YOUNG SINGLES/COUPLES')]
print(Mainstream_retirees.head())


# In[32]:


Mainstream_Young_Singles_couples_count = Mainstream_Young_Singles_couples.groupby(['Brand'])['PROD_QTY'].sum().reset_index()
Mainstream_Young_Singles_couples_count = Mainstream_Young_Singles_couples_count.sort_values(by = ['PROD_QTY'], ascending=False)
Mainstream_Young_Singles_couples_count['PROD_QTY'] = (Mainstream_Young_Singles_couples_count['PROD_QTY']/Mainstream_Young_Singles_couples_count['PROD_QTY'].sum())*100

print(Mainstream_Young_Singles_couples_count)


# We can see that the Mainstream-Young Singles couples are more likely to purchase Kettle and least likely to purchase Woolworths.

# In[33]:


Mainstream_Young_Singles_couples_size = Mainstream_Young_Singles_couples.groupby(['Size'])['PROD_QTY'].sum().reset_index()
Mainstream_Young_Singles_couples_size = Mainstream_Young_Singles_couples_size.sort_values(by = ['PROD_QTY'], ascending=False)
Mainstream_Young_Singles_couples_size['PROD_QTY'] = (Mainstream_Young_Singles_couples_size['PROD_QTY']/Mainstream_Young_Singles_couples_size['PROD_QTY'].sum())*100

print(Mainstream_Young_Singles_couples_size)


# We can see that 27% of the Mainstream_Young_Singles_couples more likely to purchase 175g and least likely to purchase 125g.

# Conclusion
# Sales have mainly been due to Budget - older families, Mainstream - young singles/couples, and Mainstream
# -retirees shoppers.
# We found that the high spend in chips for mainstream young singles/couples and retirees is due to the great number of customer in these segments.
# Mainstream, midage and young singles and couples are also more likely to pay more per packet of chips. 
# This is indicating their buying behaviour.
# We have also discovered that kettle is the most popular chips brand over these segements and 175g is the most often size that customer would buy so we can have more promotion on kettle and 175g chips.
