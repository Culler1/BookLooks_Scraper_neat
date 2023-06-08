import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdb
from datetime import date
import glob 
import os
import warnings
warnings.filterwarnings('ignore')

url = 'http://booklooks.org/book-reports'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
r = requests.get(url=url, headers=headers)
soup = BeautifulSoup(r.content,'html')
#caption = soup.find_all("td")
links=[]
path='http://booklooks.org/'
for line in soup.find_all('a')[8:-2]:
    links.append(path+line.get('href'))
today=date.today()
url = []
title = []
author = []
rating = []
slick_sheet = []
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
for i in range(0,27):
    url = links[i]
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.content,'html')
    caption = soup.find_all("td")
    n=0
    while n <len(caption):
        string1 = caption[n].text
        n=n+4
        title.append(string1)
    
    n=1
    while n <len(caption):
        string1 = caption[n].text
        n=n+4
        author.append(string1)
    
    n=2
    while n <len(caption):
        string1 = caption[n].text
        n=n+4
        rating.append(string1)
    
    n=3
    while n <len(caption):
        string1 = caption[n].text
        n=n+4
        slick_sheet.append(string1)
    d = {'title':title, 'author':author, 'rating':rating, 'slick_sheet':slick_sheet}
df1 = pd.DataFrame(data=d)
df1=df1[df1.title!='---']
df1.reset_index(inplace=True)
df1.drop(columns={'index'},inplace=True)
df1['retrieved_date']=today.strftime("%m/%d/%Y")
df1.to_csv("booklooks_lists//bookLooks_"+str(today.strftime("%m_%d_%Y")+".csv"),index=None)
path = 'booklooks_lists/*.csv'
list_of_files = glob.glob(path)
sorted_files = sorted(list_of_files, key=os.path.getctime)
last_file = pd.read_csv(sorted_files[-2])
first_file=pd.read_csv(sorted_files[0])
first_file = first_file[~first_file.title.str.contains("http")]
pct_over3=((df1[df1.rating.astype(int)>=3].title.count())/(df1.title.count())).round(2)*100
print("There are "+str(len(df1.title))+" books listed on BookLooks as of "+str(today.strftime("%m/%d/%Y"))+".")
print("There were "+str(len(last_file.title))+" files as of "+str(last_file.retrieved_date[0])+".")
#print(df1[~df1.title.isin(last_file.title)].title.to_list()[0]+" by "+df1[~df1.title.isin(last_file.title)].author.to_list()[0]+" was added since that previous scrape.")
print("There have been "+str(df1[~df1.title.isin(first_file.title)].title.count())+" books added since "+first_file.retrieved_date[0])
print("Roughly "+str(pct_over3)+"% of BookLooks' current titles are rated three or higher.")
print(str(df1.author.value_counts().index[0])+" is the most frequently mentioned author with "+str(df1.author.value_counts()[0])+" titles in this list. \n")
url = 'https://en.wikipedia.org/wiki/List_of_most_commonly_challenged_books_in_the_United_States'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
r = requests.get(url=url, headers=headers)
soup = BeautifulSoup(r.content,'html')
table=soup.find("tbody")
table=pd.read_html(url)[0]
table.columns=['title','author','reasons_for_challenge','years_published','alaRank10_19','alaRank00_09','alaRank90_99']
table[table.title.str.contains("Gender")]