import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdb
from datetime import date
import glob 
import os
from PyPDF2 import PdfReader
import urllib
import inspect

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
df = pd.DataFrame(data=d)

badPDF = 'http://booklooks.org/data/files/Book Looks Reports/Allegedly.pdf'
pdf_links=[]
for i in range(len(links)):
    url = links[i]
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.content,'html')
    for line in soup.find_all('a')[35:-2]:
        pdf_links.append(path+line.get('href'))
        pdf_links = list(set(pdf_links))
    if badPDF in pdf_links:
        pdf_links.remove(badPDF)
pdf_path = 'BookLooks_reports/'
if os.path.exists(pdf_path)==False:
    os.mkdir(pdf_path)


os.chdir(pdf_path)
for i in range(len(pdf_links[:-1])):
    url = pdf_links[i]
    #filepath = pdf_path+url.split('/')[-2]+"/" 
    r = requests.get(url= url, headers=headers)
    with open(str(url.split('/')[-1]), 'wb') as f:
        f.write(r.content)
os.chdir('..')