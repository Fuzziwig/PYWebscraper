import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import re
import os
import subprocess

#function for making lists of all the resources based on soup
def find_list_resources (tag, attribute,soup):
   list = []
   for x in soup.findAll(tag):
       try:
           list.append(x[attribute])
       except KeyError:
           pass
   return(list)

#function for extracting filename from url
def get_filename_from_cd(cd):
    if not cd:
        return None
    fname = re.findall(r'.*/(.+)$', cd)
    if len(fname) == 0:
        return None
    return fname[0]

url = 'https://www.toptal.com/developers/gitignore'
#uncomment this line to take user input
#url = input()

try:
    #get our index page (cant fetch filename from url so its index)
    response = requests.get(url, allow_redirects=True)
    response.raise_for_status()
    #get all resources needed for offline view
    soup = BeautifulSoup(response.content, features="html.parser")
    resources = []
    resources.extend(find_list_resources('img',"src",soup))   
    #resources.extend(find_list_resources('script',"src",soup))    
    resources.extend(find_list_resources("link","href",soup))
    resources.extend(find_list_resources("video","src",soup))         
    resources.extend(find_list_resources("audio","src",soup)) 
    resources.extend(find_list_resources("iframe","src",soup))
    resources.extend(find_list_resources("embed","src",soup))
    resources.extend(find_list_resources("object","data",soup))         
    resources.extend(find_list_resources("source","src",soup))
    #get current directory to be added to index resources
    cwd = "file:///"+str(os.getcwd())+"\\"
    #convert index from byte object to string so we can replace resource sources
    indexfile = response.content.decode('utf-8')
    #download resources and change resource src in index accordingly for offline view
    for i in resources:
        fl = url + '/'+ i
        subresponse = requests.get(fl, allow_redirects=True)
        filename = get_filename_from_cd(fl)
        open(get_filename_from_cd(fl), 'wb').write(subresponse.content)
        indexfile = indexfile.replace(i, cwd+filename)
    #save modified index page with new res sources
    with open("index.html", "w") as text_file:
       text_file.write(indexfile)
    #add stuff to git
    subprocess.call('git add .', cwd=os.getcwd())
    subprocess.call('git commit -m "webscraper commit', cwd=os.getcwd())
    subprocess.call('git push origin main', cwd=os.getcwd())
      
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}') 
else:
    print('Success!')




