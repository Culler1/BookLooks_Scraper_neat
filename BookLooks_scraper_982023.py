import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdb
from datetime import date
from datetime import datetime
import glob 
import os
import warnings
warnings.filterwarnings('ignore')
import io
from PyPDF2 import PdfReader

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
pdf_links = []
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
for i in range(0,27):
    url = links[i]
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.content,'html')
    caption = soup.find_all("td")
    n=0
    while n <len(caption):
        string1 = caption[n].text
        string2 = caption[n].find('a').get('href')
        string2 = "http://booklooks.org/"+string2
        n=n+4
        title.append(string1)
        pdf_links.append(string2)
    
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
    d = {'title':title, 'author':author, 'rating':rating, 'slick_sheet':slick_sheet,'pdf_links':pdf_links}
df1 = pd.DataFrame(data=d)
df1=df1[df1.title!='---']
df1.reset_index(inplace=True)
df1.drop(columns={'index'},inplace=True)

def extract_book_info(pdf_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(pdf_url, headers=headers)
        if response.status_code == 200:
            pdf_data = io.BytesIO(response.content)
            pdf_reader = PdfReader(pdf_data)
            if pdf_reader.pages:
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
                book_info = {}
                book_info['pdf_links'] = pdf_url

                # Extract title
                title_end_index = text.find("Book Summary:")
                title = text[:title_end_index].strip()
                book_info['Title'] = title

                # Extract book summary
                summary_start_index = text.find('Book Summary:')
                summary_end_index = text.find('Summary of Concerns:')
                if summary_start_index != -1:
                    summary = text[summary_start_index + len('Book Summary:'):summary_end_index].strip()
                else:
                    summary = None
                book_info['Book_Summary'] = summary

                # Extract summary of concerns
                concerns_start_index = text.find('Summary of Concerns:') + len('Summary of Concerns:')
                concerns_end_index = text.find('Mitigating Factor:') if 'Mitigating Factor:' in text else None
                concerns = text[concerns_start_index:concerns_end_index].strip()
                book_info['Summary_of_Concerns'] = concerns

                # Extract mitigating factor
                mitigating_factor_start_index = text.find('Mitigating Factor:')
                if mitigating_factor_start_index != -1:
                    mitigating_factor_end_index = text.find('By')
                    mitigating_factor = text[mitigating_factor_start_index + len('Mitigating Factor:'):mitigating_factor_end_index].strip()
                else:
                    mitigating_factor = None
                book_info['Mitigating_Factor'] = mitigating_factor

                # Extract reading level
                reading_level_start_index = text.rfind('\n', 0, summary_start_index) + 1
                reading_level_end_index = text.find('By', summary_end_index)
                reading_level = text[reading_level_start_index:reading_level_end_index].strip()
                book_info['Reading_Level'] = reading_level

                # Extract author
                author_start_index = text.find('By') + len('By')
                author_end_index = text.find('ISBN:')
                author = text[author_start_index:author_end_index].strip()
                book_info['Author'] = author

                # Extract ISBN
                isbn_start_index = text.find('ISBN:') + len('ISBN:')
                isbn = text[isbn_start_index:].strip()
                book_info['ISBN'] = isbn

                return book_info
            else:
                print("No pages found in the PDF.")
        else:
            print(f"Failed to fetch the PDF. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
    return None

# Iterate through df1's pdf_links and extract book information
book_info_list = []
for pdf_url in df1['pdf_links']:
    book_info = extract_book_info(pdf_url)
    if book_info:
        book_info_list.append(book_info)

# Create a DataFrame from the extracted book information
df2 = pd.DataFrame(book_info_list)

# Merge df1 and df2 based on a common identifier, such as the PDF URL
merged_df = df1.merge(df2, on='pdf_links', how='left')
merged_df['Reading_Level']=merged_df.Title.str.split("\n \n",expand=True)[1].str.split("  ",expand=True)[0]

read_level_corrections={"Easy R eader":"Easy Reader",'Adult Gr aphic Novel':'Adult Graphic Novel','Easy':"Easy Reader",'Easy Read er':"Easy Reader", 
                       "Juve nile":'Juvenile','Juve nile Graphic':"Juvenile Graphic Novel",'Juveni le':"Juvenile",'LOOKING FOR \nALASKA':'',
                       ' \nYoung Adult':"Young Adult",'[Add a caption for your photo here.]':"",'You ng A dult ':"Young Adult",
                       "You ng Adult":"Young Adult",'You ng Adult Graphic Novel':"Young Adult Graphic Novel",'Young A dult':"Young Adult",
                       'Young Ad ult':"Young Adult",'You ng A dult':"Young Adult","Young A dult Graphic Novel":"Young Adult Graphic Novel",
                       "Young Adult Gr aphic Novel":"Young Adult Graphic Novel","Young Adult Grap hic Novel":"Young Adult Graphic Novel",
                       "Young Adult Graphi c Novel":"Young Adult Graphic Novel","Young Adult Graphic No vel":"Young Adult Graphic Novel",
                       "Young Adult Graphic Nov el":"Young Adult Graphic Novel"}
merged_df["Reading_Level"]=merged_df.Reading_Level.replace(read_level_corrections)
merged_df['bs_test1']=merged_df.Title.str.split(" Book",expand=True)[1].str.split(":",expand=True)[1]
merged_df['book_summary']=merged_df.Book_Summary.fillna(merged_df.bs_test1)
merged_df.drop(columns={"Book_Summary",'bs_test1','Author','Title','slick_sheet'},inplace=True)
merged_df['soc_test']=merged_df.Summary_of_Concerns.str.split("y:",expand=True)[1].str.split(":",expand=True)[1].str.split("\nBy",expand=True)[0]
merged_df['SoC']=merged_df.soc_test.fillna(merged_df.Summary_of_Concerns)
merged_df['SoC']=merged_df.SoC.str.split('\nBy',expand=True)[0]
merged_df = merged_df.drop(columns={"soc_test",'Summary_of_Concerns'}).rename(columns={"SoC":"Summary_of_Concerns"})

# Function to get the creation date from a PDF
def get_creation_date(pdf_url):
    try:
        response = requests.get(pdf_url, headers=headers)
        if response.status_code == 200:
            pdf_data = io.BytesIO(response.content)
            pdf_reader = PdfReader(pdf_data)
            if '/CreationDate' in pdf_reader.metadata:
                creation_date = pdf_reader.metadata['/CreationDate']
                # Remove single quotes around timezone offset
                creation_date = creation_date.replace("'", "")
                # Convert the date to a more readable format (you may need to adjust this based on the actual format)
                creation_date = datetime.strptime(creation_date, "D:%Y%m%d%H%M%S%z")
                return creation_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                print("Creation date not found in PDF metadata.")
        else:
            print(f"Failed to fetch the PDF. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
    return None

# Add a new column with the creation date from the PDFs
merged_df['creation_date'] = merged_df['pdf_links'].apply(get_creation_date)
# Function to get the creation date from a PDF
def get_mod_date(pdf_url):
    try:
        response = requests.get(pdf_url, headers=headers)
        if response.status_code == 200:
            pdf_data = io.BytesIO(response.content)
            pdf_reader = PdfReader(pdf_data)
            if '/ModDate' in pdf_reader.metadata:
                mod_date = pdf_reader.metadata['/ModDate']
                # Remove single quotes around timezone offset
                mod_date = mod_date.replace("'", "")
                # Convert the date to a more readable format (you may need to adjust this based on the actual format)
                mod_date = datetime.strptime(mod_date, "D:%Y%m%d%H%M%S%z")
                return mod_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                print("Mod date not found in PDF metadata.")
        else:
            print(f"Failed to fetch the PDF. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
    return None

# Add a new column with the creation date from the PDFs
merged_df['mod_date'] = merged_df['pdf_links'].apply(get_mod_date)
merged_df['title_author']=merged_df.title+" "+merged_df.author
merged_df = merged_df[merged_df.title_author.notna()]
today = datetime.now()
today_string = today.strftime('%Y-%m-%d')
file_name = f"booklooks_{today_string}.csv"
merged_df.to_csv(file_name,index=None)