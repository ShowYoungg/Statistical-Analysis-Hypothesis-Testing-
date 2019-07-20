#!/usr/bin/env python
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[10]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[11]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[12]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    with open ('university_towns.txt') as Text:
        state_and_town = []
        st = []
        for line in Text:
            a = line.split('(')[0]
            if '[edit]' in a:
                state = a.split('[')[0]
                if 'ï»¿' in state:
                    state = state[3:]                
            else:
                st.append([state, a])                
    return pd.DataFrame(st, columns= ['State', 'RegionName'])

# get_list_of_university_towns()


# In[65]:


recession = []
def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    
    ef = pd.read_excel('gdplev.xls')
    ef = ef[['Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6']]
    ef = ef.dropna()
    start = ef[ef['Unnamed: 4'] == '2000q1']    
    ef = ef[(start.index - 7)[0]:]
    rec = False
    for serie in ef.index:
        s = ef.loc[serie].loc['Unnamed: 6']
        if (serie + 1) < 285:
            s1 = ef.loc[serie + 1].loc['Unnamed: 6']
        if (serie - 1) > 219:
            s2 = ef.loc[serie - 1].loc['Unnamed: 6']
        else:
            s2 = 0    
        if s2 != 0:
            if rec == False:        
                if (s2 > s and s > s1):
                    rec = True
                    recession.append([ef.loc[serie+1].loc['Unnamed: 4'], ef.loc[serie+1].loc['Unnamed: 6']])
                elif s > s2 and s1 > s:
                    rec = False
            if rec == True:
                recession.append([ef.loc[serie].loc['Unnamed: 4'], ef.loc[serie].loc['Unnamed: 6']])
                if s > s2 and s1 > s:
                    rec = False
                    recession.append([ef.loc[serie+1].loc['Unnamed: 4'], ef.loc[serie+1].loc['Unnamed: 6']])
    recession.sort(key=lambda x: x[0])
    return recession[0][0]

get_recession_start()


# In[14]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
       
    return recession[len(recession)-1][0]
# get_recession_end()


# In[54]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    recession.sort(key=lambda x: x[1])
    return recession[0][0]
# get_recession_bottom()


# In[16]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    df = pd.read_csv('City_Zhvi_AllHomes.csv')
    ef = pd.DataFrame(df[['State', 'RegionName']])
    ef['State'] = [ states[s] for s in df['State']]
    columns = list(range(2000, 2017))
    columns2 = []
    for a in columns:
        ab = str(a)+'q1'
        b = str(a)+'q2'
        c = str(a)+'q3'
        d = str(a)+'q4'
        columns2.append(ab)
        columns2.append(b)
        columns2.append(c)
        columns2.append(d)
            
        ef[ab] = df[[str(a)+'-01', str(a)+'-02', str(a)+'-03']].mean(axis=1)
        ef[b] = df[[str(a)+'-04', str(a)+'-05', str(a)+'-06']].mean(axis=1)
        if str(a) == '2016':
            ef[c] = df[[str(a)+'-07', str(a)+'-08']].mean(axis=1)
        else:
            ef[c] = df[[str(a)+'-07', str(a)+'-08', str(a)+'-09']].mean(axis=1)
            ef[d] = df[[str(a)+'-10', str(a)+'-11', str(a)+'-12']].mean(axis=1)
    ef = ef.set_index(['State', 'RegionName'])
    return ef
# convert_housing_data_to_quarters()


# In[57]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    university_town = get_list_of_university_towns()
    data = convert_housing_data_to_quarters()
    before = data[data.columns[data.columns.get_loc('2008q3')-1]]

    data['Price Ratio'] = before/data['2009q2']
    data = data.fillna(0)
    data = data.reset_index()
    
    recession.sort(key=lambda x: x[0])
    data = data[[get_recession_start(), get_recession_bottom(), 'Price Ratio']]
    
    r = pd.merge(university_town, data, how='inner', left_index=True, right_index=True)
    rrr = pd.merge(data, r, how='outer', left_index=True, right_index=True)
    rrr = rrr.set_index('RegionName')

    c = rrr.index.unique()
    for cd in c:
        if str(cd) != 'nan':
            rrr = rrr.drop(cd)
    
    r['Change'] = data['2008q3'] - data['2009q2']
    
    r = r.set_index('RegionName')
    dd = convert_housing_data_to_quarters()
    dd = dd[[  get_recession_start(), get_recession_bottom()]]
    data['Change'] = data['2008q3'] - data['2009q2']
    rrr['Change'] = rrr['2008q3_x'] - rrr['2009q2_x']
    
    a = [x for x in r['Change']]
    b = [y for y in rrr['Change']] 
    ab = np.mean(r['Price Ratio'])
    bb = np.mean(rrr['Price Ratio_x'])
    
    if bb < ab:
        better = 'university town'
    else:
        better = 'non-university town'
#     print(str(ab) + ' : ' + str(bb))
            
    p = ttest_ind(a, b)
    
    if p[1] < 0.01:
        difference = True
    else:
        difference = False
    
    return (difference, p[1], better)

# run_ttest()


# In[ ]:





# In[ ]:





# In[ ]:




