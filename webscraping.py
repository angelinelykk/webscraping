#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import requests
from bs4 import BeautifulSoup
import json
import re 
import requests
import time


# In[2]:


#Step 1: from name to google search
def getGoogleSearchURL(company_name, website):
    split_name = company_name.lower().split()
    URL = 'https://www.google.com/search?q='
    for piece in split_name:
        URL += piece
        URL += '+'
    URL += website
    return URL


# In[14]:


#Step 2: from google search to websiteURL
def getURL(googleSearch, website, company_name):
    name = company_name.split()[0].lower()
    page = requests.get(googleSearch)
    soup = BeautifulSoup(page.content, 'html.parser')
    print(soup)
    result_div = soup.find_all('div', attrs = {'class': 'ZINbbc'})
    links = []
    for r in result_div:
        try:
            link = r.find('a', href = True)
            if link != '':
                links.append(link['href'])
        except:
            continue
    clean_links = []
    for link in links:
        clean = re.search('\/url\?q\=(.*)\&sa', link)
        if clean is None:
            continue
        clean_links.append(clean.group(1))
    final = None
    for link in clean_links:
        if website == 'sgpgrid' and 'https://sgpgrid.com/company-details/' in link and name in link:
            final = link
        if website == 'linkedin' and 'https://sg.linkedin.com/company/' in link and name in link:
            final = link
        if website == 'crunchbase' and 'https://www.crunchbase.com/organization/' in link and name in link:
            final = link
    return final


# In[15]:


googleSearch = getGoogleSearchURL('facebook', 'linkedin')
URL = getURL(googleSearch, 'linkedin', 'facebook')
print(googleSearch)
print(URL)


# In[5]:


#crunchbase
def getCrunchbaseURL(company_name):
    googleURL = getGoogleSearchURL(company_name, 'crunchbase')
    URL = getURL(googleURL, 'crunchbase', company_name)
    if URL == None:
        URL = 'No information available'
    return URL


# In[26]:


#Step 3: from sgpgrid URL to company details
def getGridSingleCompanyDetails(URL):
    if URL == None:
        return ['No information', 'No information', 'No information', 'No information', 'No information', 'No information', 'No information', 'No information', 'No information', 'No information', 'No information', 'No information']
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    data = json.loads(soup.find("script", type = "application/json").string)
    manpower = data['props']['initialState']['singleCompany']['company']['numberOfStaff']
    manpower_global = data['props']['initialState']['singleCompany']['company']['numberOfStaffGlobal']
    total_capital = data['props']['initialState']['singleCompany']['company']['totalCapital']
    PUC_ordinary = data['props']['initialState']['singleCompany']['company']['paidupCapitalOrdinaryShares'][0]
    PUC_preference = data['props']['initialState']['singleCompany']['company']['paidupCapitalPreferenceShares'][0]
    PUC_others = data['props']['initialState']['singleCompany']['company']['paidUpCapitalOthersShares'][0]
    business_activity = data['props']['initialState']['singleCompany']['company']['businessActivity']
    primary_described_activity = data['props']['initialState']['singleCompany']['company']['primaryDescribedActivity']
    secondary_described_activity = data['props']['initialState']['singleCompany']['company']['secondaryDescribedActivity']
    website = data['props']['initialState']['singleCompany']['company']['url']
    primarySSIC = data['props']['initialState']['singleCompany']['company']['primarySsicDescription']
    secondarySSIC = data['props']['initialState']['singleCompany']['company']['secondarySsicDescription']
    details = [manpower, manpower_global, total_capital, PUC_ordinary, PUC_preference, PUC_others, business_activity, primary_described_activity, secondary_described_activity, website, primarySSIC, secondarySSIC]
    for index in range(len(details)):
        if details[index] == None:
            details[index] = 'No information'      
    return details


# In[27]:


#step 4: print company details
def printSingleCompany(detailsList):
    websites = ['sgpgrid']
    index = 0
    for details in detailsList:
        print(websites[index])
        print('')
        index += 1
        if details == None:
            print("No information available")
            return None
        print('Manpower: ', details[0])
        print('Manpower Global: ', details[1])
        print('Total Capital: ', details[2])
        print('Paid-up capital(Ordinary shares): ', details[3]['currency'], details[3]['ordinary'])
        print('Paid-up capital(Preference shares): ', details[4]['currency'], details[4]['preference'])
        print('Paid-up capital(Other shares): ', details[5]['currency'], details[5]['others'])
        print('Business Activity: ', details[6])
        print('Primary Described Activity: ', details[7])
        print('Secondary Described Activity: ', details[8])
        print('Website: ', details[9])
        print('______________________________________________________')
    return


# In[28]:


#From company name to information
def getInfo(company_name):
    links = []
    googleSearchGrid = getGoogleSearchURL(company_name, 'sgpgrid')
    gridURL = getURL(googleSearchGrid, 'sgpgrid', company_name)
    gridDetails = getGridSingleCompanyDetails(gridURL)
    return [gridDetails]


# In[29]:


#set up linkedin opening
from selenium import webdriver

driver = webdriver.Chrome("/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/chromedriver_binary/chromedriver")
driver.get('https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin')
username = driver.find_element_by_id('username')
username.send_keys('angelinelyk@berkeley.edu')
password = driver.find_element_by_id('password')
password.send_keys('gea8pjma')
sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
sign_in_button.click()

driver.get('https://www.linkedin.com/company/twitter/?originalSubdomain=sg')


# In[30]:


#Consolidation for linked in
def getLinkedInDetails(company_name):
    googleURL = getGoogleSearchURL(company_name, 'linkedin')
    linkedinURL = getURL(googleURL, 'linkedin', company_name)
    if linkedinURL == None:
        return ['No information', 'No information', 'No information', 'No information']
    details = getSingleLinkedInDetails(linkedinURL)
    return details


# In[31]:


#consolidation
def getSingleLinkedInDetails(URL):
    print(URL)
    getLinkedIn(URL)
    about = getAboutPage()
    getLinkedIn(about)
    details = getAboutDetails()
    details.append(URL)
    return details  


# In[32]:


def getLinkedIn(URL):
    driver.get(URL)


# In[33]:


def getAboutPage():
    links = driver.find_elements_by_xpath("//a[@href]")
    while len(links):
        url = links.pop()
        url = url.get_attribute("href")
        if '/about/' in url:
            return url
    return None


# In[34]:


def getAboutDetails():
    main = driver.find_element_by_id('main')
    mb6 = main.find_element_by_class_name('mb6')
    description = mb6.find_element_by_tag_name('p')
    website = mb6.find_element_by_tag_name('span')
    dd = mb6.find_elements_by_tag_name('dd')
    employees = getEmployees(dd)
    return [description.text, website.text, employees]


# In[35]:


def getEmployees(descriptions):
    employees = None
    while len(descriptions):
        small = descriptions.pop()
        if 'employees' in small.text:
            employees = small.text
            employees = employees.split()
            employees = employees[0]
    return employees


# In[36]:


import pandas as pd
import numpy as np
test = pd.read_csv('/Users/angelinelee/Documents/webscraping/test1.csv')
test_df = pd.DataFrame(test)
test_df['Web Presence'] = None
test_df['Company Background'] = None
test_df['LinkedIn-description'] = None
test_df['Grid-business activity'] = None
test_df['Grid-primary activity'] = None
test_df['Grid-primary SSIC description'] = None
test_df['Grid-secondary activity'] = None
test_df['Grid-secondary SSIC description'] = None
test_df['Has any of the C-suite exited before?'] = None
test_df['LinkedIn Links'] = None
test_df['Subsector'] = None
test_df['Specific subsector'] = None
test_df['Manpower'] = None
test_df['LinkedIn-manpower'] = None
test_df['Grid-manpower'] = None
test_df['Grid-manpower global'] = None
test_df['Level of funding'] = None
test_df['Total Funding'] = None
test_df['Grid-total capital'] = None
test_df['Grid-PUC(ordinary)'] = None
test_df['Grid-PUC(preference)'] = None
test_df['Grid-PUC(others)'] = None
test_df['Crunchbase Link'] = None
test_df['Company Website'] = None
test_df['LinkedIn-website'] = None
test_df['Grid-website'] = None
#test_df.loc[0, 'Grid-manpower'] = 2
print(test_df.shape[0])


# In[37]:


import random
previous_name = None
unique_companies = 0
for index in range(test_df.shape[0]): 
    name = test_df.iloc[index]['Companies'].lower()
    if name != previous_name:
        n = random.randint(0,45)
        time.sleep(n)
        unique_companies += 1
        detailsGrid = getInfo(name)
        test_df.loc[index]['Grid-manpower'] = detailsGrid[0][0]
        test_df.loc[index]['Grid-manpower global'] = detailsGrid[0][1]
        test_df.loc[index]['Grid-total capital'] = detailsGrid[0][2]
        if detailsGrid[0][3] == 'No information':
            test_df.loc[index]['Grid-PUC(ordinary)'] = 'No information'
        if detailsGrid[0][3] != 'No information':
            if detailsGrid[0][3]['ordinary'] != None:
                test_df.loc[index]['Grid-PUC(ordinary)'] = detailsGrid[0][3]['currency'] + ' ' + detailsGrid[0][3]['ordinary']
            if detailsGrid[0][3]['ordinary'] == None:
                test_df.loc[index]['Grid-PUC(ordinary)'] = 'No information'
        if detailsGrid[0][4] == 'No information':
            test_df.loc[index]['Grid-PUC(preference)'] = 'No information'
        if detailsGrid[0][4] != 'No information':
            if detailsGrid[0][4]['preference'] != None:
                test_df.loc[index]['Grid-PUC(preference)'] = detailsGrid[0][4]['currency'] + ' ' + detailsGrid[0][4]['preference']
            if detailsGrid[0][4]['preference'] == None:
                test_df.loc[index]['Grid-PUC(preference)'] = 'No information'
        if detailsGrid[0][5] == 'No information':
            test_df.loc[index]['Grid-PUC(others)'] = 'No information'
        if detailsGrid[0][5] != 'No information':
            if detailsGrid[0][5]['others'] != None:
                test_df.loc[index]['Grid-PUC(others)'] = detailsGrid[0][5]['currency'] + ' ' + detailsGrid[0][5]['others']
            if detailsGrid[0][5]['others'] == None:
                test_df.loc[index]['Grid-PUC(others)'] = 'No information'
        test_df.loc[index]['Grid-business activity'] = detailsGrid[0][6]
        test_df.loc[index]['Grid-primary activity'] = detailsGrid[0][7]
        test_df.loc[index]['Grid-secondary activity'] = detailsGrid[0][8]
        test_df.loc[index]['Grid-website'] = detailsGrid[0][9]
        test_df.loc[index]['Grid-primary SSIC description'] = detailsGrid[0][10]
        test_df.loc[index]['Grid-secondary SSIC description'] = detailsGrid[0][11]
        
        detailsLinkedIn = getLinkedInDetails(name)
        test_df.loc[index]['LinkedIn-manpower'] = detailsLinkedIn[2]
        test_df.loc[index]['LinkedIn-description'] = detailsLinkedIn[0]
        test_df.loc[index]['LinkedIn-website'] = detailsLinkedIn[1]
        test_df.loc[index]['LinkedIn Links'] = detailsLinkedIn[3]
        
        test_df.loc[index]['Crunchbase Link'] = getCrunchbaseURL(name)
        print(unique_companies)
    previous_name = name


# In[38]:


#convert dataframe to excel sheet
test_df.to_excel('/Users/angelinelee/Documents/webscraping/exporttest4.xlsx', index = False, header = True)


# In[ ]:




