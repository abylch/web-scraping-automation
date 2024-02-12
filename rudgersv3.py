# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 18:38:32 2022

@author: abylc
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import urllib.request
import csv
import json
from openpyxl import Workbook
from openpyxl.styles import Font
import pandas as pd
import time 
import re

# disable image load
option = webdriver.ChromeOptions()
chrome_prefs = {}
option.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, chrome_options=option)
# driver.maximize_window()
#######some sites if the size of window not big enought the button not reachable
#driver.set_window_size(250,600)



data = {}

def pub_count(pubs):
    p_list = pubs
    counter = 0
    for i in p_list:
        for x in range(1960, 2022):
            x_str = str(x)
            if x_str in i:
                counter += i.count(x_str)
    return counter

def name_in_pubs(name, pubs):
    counter = 0
    namex = name
    namey = name.upper()
    for i in pubs:
        if namex in i or namey in i:
            counter += i.count(namex)
            counter += i.count(namey)
    return counter

def department_func(temp):
    x = temp.lower()
    if "law" in x:
        return "Law"
    if "biology" in x or "biological" in x:
        return "Biology"
    if "psychology" in x:
        return "Psychology"
    if "computer science" in x:
        return "Computer Science"
    if "philosophy" in x:
        return "Philosophy"
    
def rank_func(temp):
    x = temp.lower()
    if "adjunct" in x:
        return "Adjunct Professor"
    elif "emeritus" in x or "emerita" in x:
        return "Professor Emeritus"
    elif "associate" in x:
        return "Associate Professor"
    elif "assistant" in x:
        return "Assistant Professor"
    elif "professor" in x:
        return "Professor"
    else:
        return "other"

def word_counter(words):
    x = words
    if x == "non available":
        x = ["non available", "non available"]
        return x
    # \d\.\s+ – numbered bullets
    # [a-z]\)\s+ – small letter bullets with closing brace
    # •\s+ – usual bullet
    # [A-Z]\.\s+ – upper case bullets with dots
    # [IVX]+\.\s+ – Roman numbered bullets
    
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(x)
    
    x = x.replace('/\d\.\s+|[a-z]\)\s+|•\s+|[A-Z]\.\s+|[IVX]+\.\s+/g', " ")
    x = x.replace("[^\w\s]", " ")
    x = x.replace('/\d\.\s+|[a-z]\)\s+|•\s+|[A-Z]\.\s+|[IVX]+\.\s+/g', "")
    # [^\w\s] means any alphanumeric character and is equal to the character set [a-zA-Z0-9_]
    # from punctuation to space if --> land-use instead of landuse, --> land use
    # [^\w\s] means any alphanumeric character and is equal to the character set [a-zA-Z0-9_]
    x = re.sub("[^\w\s]", " ", x)
    
   
    print("check if remove bullets pass")
    
    
    #double check
    # [^\w\s] means any alphanumeric character and is equal to the character set [a-zA-Z0-9_]
    string_no_punctuation = re.sub("[^\w\s]", "", x)
    word_list_clean = string_no_punctuation.split()
    # from list to string
    x = ""
    x = ' '.join(word_list_clean)
    
    # REmove single_spaces 
    x = " ".join(x.split())
    # counts words
    word_list = x.split()
    number_of_words = len(word_list)
    word_count = number_of_words
    count_fix = [word_count, x]
    print("check def word_counter:", word_count, x)
    if word_count > 0:
        return count_fix
    else:
        x = ["non available", "non available"]
        return x
        

def api_gender(name):
    if "-" in name:
        namex = name.replace("-", " ")
        namex = name.split()[0]
    else:
        namex = name
    #api gender + probability
    api_web_url = "https://api.genderize.io?name=" + namex
    print(api_web_url)
    # open a connection to a URL using urllib
    try:
        with urllib.request.urlopen(api_web_url) as response:
            json_data = response.read().decode("utf-8")
            obj = json.loads(json_data)
            gender = obj["gender"]
            probability = obj["probability"]
            list_gender = [gender, probability]
            # if api doesn't recognice name of the resercher returns prob = 0
            if list_gender[1] == 0:
                list_gender = ["non available", "non available"]
                return list_gender
            else:
                return list_gender
    except Exception as e:
        print(e)
        list_gender = ["unable to get data from api", "unable to get data from api"]
        return list_gender

def links(url, name):
    namex = name
    counter = 0
    driver.get(url)
    # waits 5 secs
    time.sleep(5)
    links = []
    ### if site has button load more peolple ex. biology department
    flag = 0
    while flag == 0:
        try:
            click = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'button')]  [contains(text(),'Load More People')]")))
            click.click()
            counter += 1
            time.sleep(5)
        except:
            print("no button load more people, pass, number of buttons pressed:", counter)
            flag = 1
            counter = 0
            pass
    time.sleep(5)
    elements = driver.find_elements(By.CLASS_NAME, namex)
    for elem in elements:
        link = elem.find_element(By.TAG_NAME, "a").get_attribute('href')
        links.append(link)
        print(link)
        counter +=1
        # test first 5 links
        # if counter == 20:
        #     return links
    return links


url = "https://philosophy.rutgers.edu/people/regular-faculty"
philosophy_links = links(url, "newstitle")
url = "https://sasn.rutgers.edu/faculty-staff?chkf=665--2#"
biology_links = links(url, "node-title")
url = "https://www.cs.rutgers.edu/people/professors"
cs_links = links(url, "newstitle")
url = "https://psych.rutgers.edu/people/facultyblog"
psychology_links = links(url, "newstitle")
url = "https://law.rutgers.edu/directory/subtype/lawfaculty"
law_links = links(url, "name")


def philosophy_res(links):
    urls = links
    data = {}
    
    for href in urls:
        publications = []
        expertise = []
        specialties = ""
        institution = ""
        department = ""
        num_of_publ = 0
        bio_word_count = ""
        list_li = []
        bio = ""
        # test for one resume only
        # if href != "https://philosophy.rutgers.edu/people/regular-faculty/regular-faculty-profile/182-regular-faculty-full-time/780-sider-ted":
        #     continue

        try:
            driver.get(href)
            fields_container = driver.find_element(By.CLASS_NAME, "fields-container")
            elements = fields_container.find_elements(By.TAG_NAME, "li")
            for elem in elements:
                x = elem.text
                list_li.append(x)
            
            #gets the data from list
            counter = 0
            for i in list_li:
                # print(i)
                if counter == 1:
                    name = i
                    print("name", i)
                elif counter == 2:
                    title = rank_func(i)
                    print("title", title)
                elif "Specialties:" in i:
                    specialties = i[13:]
                    print("specialties", specialties)
                counter += 1
            counter = 0
            
            try:
                dep = driver.find_element(By.XPATH, "//div[@class='name-primary']")
                temp = dep.find_element(By.TAG_NAME, "a").text
                department = department_func(temp)
                data[name].update({"department": department})
                
            except:
                print("checkpoint exception department no data")
                pass
            
            try:
                temp = driver.find_element(By.XPATH, "//a[@href='http://www.rutgers.edu']").text
                institution = temp.split()[0]
                data[name].update({"institution": institution})
                
            except:
                print("checkpoint exception institution no data")
                pass
            
            
            
            data.update({name:{"name": name, "institution": institution, "department": department,
                            "link": href, "title": title, "number of publications": "non available",
                            "expertise": specialties, "bio_word_count": "", "gender": "", "probability": ""}})
        
                
        except:
            print("checkpoint exception fields_container no data")
            pass
        
        try:
            articleBody = driver.find_element(By.XPATH, "//div[@itemprop='articleBody']")
            elements = articleBody.find_elements(By.TAG_NAME, "p")
            for elem in elements:
                x = elem.text
                word_list = x.split()
                number_of_words = len(word_list)
                if number_of_words > 5:
                    bio = bio + " " + x
                    
            #### check if good because ronald chen - expertise
            data[name].update({"expertise": specialties + " " + bio})
            
        except:
            print("checkpoint bio no data")
            pass
            
        try:
            #count words to describe expertise
            temp = data[name].get("expertise")
            count_fix = word_counter(temp)
            bio_word_count = count_fix[0]
            expertise = count_fix[1]
            data[name].update({"bio_word_count": bio_word_count})
            data[name].update({"expertise": expertise})
        except:
            print("checkpoint counter bio_word_count no  data")
            pass
        try:
            api_gen = api_gender(data[name].get("name").split()[0])
            
            # update dictionary with gender n prob
            data[name].update({"gender": api_gen[0]})
            data[name].update({"probability": api_gen[1]})
        except:
            print("unable to get data from api")
            pass
        
        try:
            #try serach for publishings in other site
            new_url = driver.find_element(By.XPATH, "//*[contains(@href, '/publications/')][contains(text(), 'Publications')]").get_attribute('href')
            
            ######## very !!!!!! IMPORTANT !!!!! get new url if opens other page
            ### is not click in the same page
            driver.get(new_url)
            time.sleep(2) 
            
            articleBody_publs = driver.find_element(By.XPATH, "//div[@itemprop='articleBody']")
            elements = articleBody_publs.find_elements(By.TAG_NAME, "li")
          
            counter = 0
            for i in elements:
                print(i.text)
                publications.append(i.text)
                if len(i.text.split()) > 1:
                    counter += 1
                else:
                    continue
            if counter > 0:
                num_of_publ = counter
            else:
                num_of_publ = "non available"
            
            
            counter = pub_count(publications)
            if counter != 0:
                num_of_publ = min(num_of_publ, counter)
            counter = 0
            
            data[name].update({"number of publications": num_of_publ})
            print("check num_of_publ:", num_of_publ)
            
        except:
            num_of_publ = "non available"
            print("checkpoint exception no button load for Publications or data")
            pass
        
    print(data)
    return data   





def biology_res(links):
    
    urls = links
    data = {}
    
    for href in urls:
        publications_li = []
        publications_p = []
        expertise = ""
        institution = ""
        department = ""
        num_of_publ = 0
        bio_word_count = ""
        list_li = []
        # test for one resume only
        # if href != "https://sasn.rutgers.edu/about-us/faculty-staff/radek-dobrowolski":
        #     continue

        try:
            driver.get(href)
            
            name = driver.find_element(By.CLASS_NAME, "page-header").text
            
            box = driver.find_element(By.XPATH, "//div[@class='views-row']")
            elements = box.find_elements(By.CLASS_NAME, "field-content")
            for elem in elements:
                x = elem.text
                list_li.append(x)
            
            title = rank_func(list_li[0])
            department = department_func(list_li[2])
            print(name, title, department)
            
            if "-" in list_li[0]:
                expertise = re.sub(r'^.*?- ', '', list_li[0])
        
        except:
            print("checkpoint exception region highlights no data")
            pass
        
        try:
            api_gen = api_gender(name.split()[0])
          
            print("test api", api_gen)
            
        except:
            print("checkpoint exception api_gen no data")
            pass
            
        try:
            box = driver.find_elements(By.XPATH, "//div[@class='field field--name-body field--type-text-with-summary field--label-hidden field--item']")
            
            print("check len box bio", len(box))
            if len(box) <= 2:
                if expertise == "":
                    expertise = "non available"
                print("expertise", expertise)
            else:
                elements = box[1].find_elements(By.TAG_NAME, "p")
                for elem in elements:
                    x = elem.text
                    list_li.append(x)
                    expertise += (" " + x)
                if len(expertise) < 20:
                    expertise = ""
                    elements = box[1].find_elements(By.TAG_NAME, "div")
                    for elem in elements:
                        x = elem.text
                        list_li.append(x)
                        expertise += (" " + x + " ")
            print("expertise", expertise)
                
        except:
            print("checkpoint exception expertise no data")
            pass
        
        
        #### experimental <li> <???>
        #try for bio <li>
        try:
            if expertise == "":
                print("check len box bio", len(box))
                if len(box) <= 2:
                    if expertise == "":
                        expertise = "non available"
                    print("expertise", expertise)
                else:
                    elements = box[1].find_elements(By.TAG_NAME, "li")
                    for elem in elements:
                        x = elem.text
                        list_li.append(x)
                        expertise += (" " + x)
                    if len(expertise) < 20:
                        expertise = ""
                        elements = box[1].find_elements(By.TAG_NAME, "div")
                        for elem in elements:
                            x = elem.text
                            list_li.append(x)
                            expertise += (" " + x + " ")
                print("expertise", expertise)
            
        except:
            
            print("checkpoint exception expertise <li> no data")
            pass
            
            
        #try for expertise if <???> 
        try:
            if expertise == "":
                print("check len box bio", len(box))
                if len(box) <= 2:
                    if expertise == "":
                        expertise = "non available"
                    print("expertise", expertise)
                else:
                    
                    elements = box[1].find_elements(By.XPATH, "//div[2][@class='field field--name-body field--type-text-with-summary field--label-hidden field--item']")
                    
                    for elem in elements:
                        x = elem.text
                        
                        list_li.append(x)
                        expertise += (" " + x)
                
                    
                print("expertise", expertise)
                
            
        except:
            print("checkpoint exception bio <????> no data")  
        
        
        
        
        
        
        
        ### end of bio
        try:
            count_fix = word_counter(expertise)
            bio_word_count = count_fix[0]
            expertise = count_fix[1]
            
            print("bio_word_count: ", bio_word_count)
            
        except:
            print("checkpoint exception bio_word_count no data")
            pass
            
        try:
            
            box = driver.find_element(By.XPATH, "//div[@class='field field--name-field-publications field--type-text-long field--label-above']//*[@class = 'field--item']")
            
            try:
                namex = name.split()[-1]
                name_in_pubs_count = 0
                counter2 = 0
                counter = 0
                elements = box.find_elements(By.TAG_NAME, "li")
                for elem in elements:
                    x = elem.text
                    publications_li.append(x)
                    print("elem test li publ:", x)
                
                counter2 = pub_count(publications_li)
            except:
                counter2 = 0
                counter = 0
                publications_li = []
                pass
            
            try:
                elements = box.find_elements(By.TAG_NAME, "p")
                time.sleep(2)
                for elem in elements:
                    x = elem.text
                    publications_p.append(x)
                    print("elem test p publ:", x)
                
                counter = pub_count(publications_p)
            except:
                pass
      
            
            if counter2 > counter:
                name_in_pubs_count = name_in_pubs(namex, publications_li)
                if name_in_pubs_count == 0:
                    num_of_publ = counter2
                    pub_counter_to_check = counter2
                    publications = publications_li
                elif counter2 > 3:
                    num_of_publ = min(name_in_pubs_count, counter2)
                    pub_counter_to_check = counter2
                    publications = publications_li
                else:
                    num_of_publ = name_in_pubs_count
                    pub_counter_to_check = counter2
                    publications = publications_li
            else:
                name_in_pubs_count = name_in_pubs(namex, publications_p)
                if name_in_pubs_count == 0:
                    num_of_publ = counter
                    pub_counter_to_check = counter
                    publications = publications_p
                elif counter > 3:
                    num_of_publ = min(name_in_pubs_count, counter)
                    pub_counter_to_check = counter
                    publications = publications_p
                else:
                    num_of_publ = name_in_pubs_count
                    pub_counter_to_check = counter
                    publications = publications_p
                    
    

            check_list = [name_in_pubs_count, pub_counter_to_check]

            counter = 0
            for i in publications:
                if len(i.split()) > 2:
                    counter += 1
                else:
                    continue
            if counter > 2:
               num_of_publ = min(check_list, key=lambda x:abs(x-counter))
            if num_of_publ == 0:
                num_of_publ = counter
            counter = 0
            
            
            
            
            
            print("num_of_publ:", num_of_publ)
        except:
            num_of_publ = "non available"
            print("checkpoint exception publications no data", num_of_publ)
            
        try:
            box = driver.find_element(By.XPATH, "//a[@href='http://www.rutgers.edu/']")
            institution = box.text.split()[1]
            print("institution", institution)
        except:
            print("checkpoint exception institution no data")
            
        
        data.update({name:{"name": name, "institution": institution, "department": department,
                        "link": href, "title": title, "number of publications": num_of_publ,
                        "expertise": expertise, "bio_word_count": bio_word_count, "gender": api_gen[0], "probability": api_gen[1]}}) 
        print(data)
    
    return data 

def  cs_res(links):
    urls = links
    data = {}
    
    for href in urls:
        publications = []
        expertise = ""
        institution = ""
        department = ""
        num_of_publ = 0
        bio_word_count = ""
        list_li = []
        # test for one resume only
        # if href != "https://www.cs.rutgers.edu/people/professors/details/karl-stratos":
        #     continue

        try:
            driver.get(href)
            
            box = driver.find_element(By.CLASS_NAME, "fields-container")
            
            # box = driver.find_element(By.XPATH, "//div[@class='views-row']")
            elements = box.find_elements(By.TAG_NAME, "li")
          
            for elem in elements:
                x = elem.text
                list_li.append(x)
                # print("test fields-container elem:", x)
                if "specialty" in x.lower() or "research" in x.lower() or len(x.split()) > 22:
                    if "Research Group(s):" in x:
                        expertise += (" " + "Research Groups")
                        rgs = box.find_elements(By.XPATH, '//a[contains(@href,"/research/")and not(@class)]')
                        for j in rgs:
                            y = j.text
                            expertise += (" " + y)
                    else:
                        expertise += (" " + x)
            if expertise == "":
                expertise = "non available"
            
            print("expertise: ", expertise)
            
            # api gender doesn't gets "-" in the name
            name = list_li[1].replace("-", " ")
            
            title = rank_func(list_li[2])
            
            #if no picture in resercher site
            if "POSITION:" in name:
                name = list_li[0].replace("-", " ")
                title = rank_func(list_li[1])
            
            box = driver.find_element(By.XPATH, "//div[@class='custom bottom-title contact-us']")
            dep = box.find_element(By.TAG_NAME, "p").text
            
            department = department_func(dep)
            institution = dep.split()[4][:-1]
            print(name, title, department, institution)  
        
        except:
            print("checkpoint exception name, title, department, institution no data")
            pass
        
        try:
            
            box = driver.find_element(By.XPATH, "//*[@id='rt-mainbody']//*[@itemprop='articleBody']")
            art = box.text
            if len(art.split()) > 20:
                if expertise == "non available":
                    expertise = ""
                    
                expertise = expertise + " " + art
            
        except:
            print("checkpoint exception  data")
            pass
        
        try:
            api_gen = api_gender(name.split()[0])
          
            print("test api", api_gen)
            
        except:
            print("checkpoint exception api_gen no data")
            pass
        
        try:
            count_fix = word_counter(expertise)
            bio_word_count = count_fix[0]
            expertise = count_fix[1]
            print("test word_counter:", bio_word_count)
        except:
            print("checkpoint exception word_counter no data")
            pass
        
        data.update({name:{"name": name, "institution": institution, "department": department,
                        "link": href, "title": title, "number of publications": "non available",
                        "expertise": expertise, "bio_word_count": bio_word_count, "gender": api_gen[0], "probability": api_gen[1]}})
        # print(data)
    
    return data

def  psycho_res(links):
    urls = links
    data = {}
    
    for href in urls:
        publications = []
        expertise = ""
        institution = ""
        department = ""
        num_of_publ = 0
        bio_word_count = ""
        list_li = []
        # test for one resume only
        # if href != "https://psych.rutgers.edu/people/chair-v-cs/department-leadership-profile/108-arthur-tomie":
        #     continue

        try:
            driver.get(href)
            
            box = driver.find_element(By.CLASS_NAME, "fields-container")
            
            elements = box.find_elements(By.TAG_NAME, "li")
        
            for elem in elements:
                x = elem.text
                list_li.append(x)
                if "Areas:" in x:
                    expertise = x
             
            # api gender doesn't gets "-" in the name
            name = list_li[1].replace("-", " ")
            title = rank_func(list_li[2])
            print("name n title: ", name, title)
            
            try:
                art = driver.find_element(By.XPATH, "//*[@itemprop='articleBody']")
                expertise += " " + art.text
                if len(expertise.split()) < 2:
                    expertise = "non available"
            except:
                if expertise == "":
                    expertise = "non available"
                pass
            print("expertise: ", expertise)
            
            try:
                
                box = driver.find_elements(By.XPATH, "//*[@id='contact']//strong")
                dep = box[0].text
                department = department_func(dep)
                
                box = driver.find_element(By.XPATH, "//*[@id='rt-copyright']/div/div[1]/p")
                inst = box.text
                institution = inst.split()[2][:-1]
                
                # print("check dep and inst", dep, inst)
                
            except:
                print("checkpoint exception department, institution no data")
                pass
            
            print(name, title, department, institution)  
        
        except:
            print("checkpoint exception name, title, department, institution no data")
            pass
        
        try:
            api_gen = api_gender(name.split()[0])
          
            print("test api", api_gen)
            
        except:
            print("checkpoint exception api_gen no data")
            pass
        
        try:
            count_fix = word_counter(expertise)
            bio_word_count = count_fix[0]
            expertise = count_fix[1]
            
            print("test word_counter:", bio_word_count)
        except:
            print("checkpoint exception word_counter no data")
            pass
        
        try:
            #try serach for publishings in other site
            new_url = driver.find_element(By.XPATH, "//span[contains(@class,'field-value')]//a[starts-with(text(),'https://sites.rutgers.edu/')]").get_attribute('href')
            
            ######## very !!!!!! IMPORTANT !!!!! get new url if opens other page
            ### is not click in the same page
            driver.get(new_url)
            time.sleep(2) 
            
            try:
                #try if there is publications button
                click = driver.find_element(By.XPATH, "//*[contains(text(), 'Publications')]")
                click.click()
                time.sleep(2)
            except:
                print("checkpoint exception no button clicked in upper menu for Publications")
                pass
            
            #try publication counter
            publs = driver.find_element(By.XPATH, "//div[@class='container content-page-container ']")
            publs_list = publs.find_elements(By.TAG_NAME, "p")
           
            
            counter = 0
            for i in publs_list:
                print(i.text)
                if len(i.text.split()) > 15:
                    publications.append(i.text)
                    counter += 1
                else:
                    continue
            if counter > 0:
                num_of_publ = counter
                namex = name.split()[-1]
                temp = pub_count(publications)
                temp2 = name_in_pubs(namex, publications)
                print("pub_count, name_in_pubs publs count func check:", temp, temp2)
                # if counter == temp2:
                    
                if temp != 0 and temp2 != 0:
                    temp3 = min(temp, temp2)
                elif temp == 0:
                    temp3 = temp2
                elif temp2 == 0:
                    temp3 = temp
                if counter == temp2:
                    num_of_publ = counter
                elif temp3 < num_of_publ:
                    num_of_publ = temp3
            else:
                num_of_publ = "non available"
            counter = 0
            
            print("check num_of_publ:", num_of_publ)
            
        except:
            num_of_publ = "non available"
            print("checkpoint exception no button load for Publications or data")
            pass
            
            
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        data.update({name:{"name": name, "institution": institution, "department": department,
                        "link": href, "title": title, "number of publications": num_of_publ,
                        "expertise": expertise, "bio_word_count": bio_word_count, "gender": api_gen[0], "probability": api_gen[1]}})
        # print(data)
    
    return data


def  law_res(links):
    urls = links
    data = {}
    
    for href in urls:
        publications = []
        expertise = ""
        institution = ""
        department = ""
        num_of_publ = 0
        bio_word_count = ""
        # list_li = []
        # test for one resume only
        # if href != "https://law.rutgers.edu/directory/view/afilalo":
        #     continue

        try:
            
            driver.get(href)
            name = driver.find_element(By.CLASS_NAME, "page-title").text
            temp = driver.find_element(By.XPATH, "//span[@itemprop='name']").text
            temp2 = driver.find_element(By.CLASS_NAME, "title").text
            department = department_func(temp)
            institution = temp.split()[0]
            title = rank_func(temp2)
            # api gender doesn't gets "-" in the name
            name = name.replace("-", " ")
        
        except:
            print("checkpoint exception name, title, department, institution no data")
            pass
        
        try:
            # Expertise
            click = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[1][contains(@class,'tab-option')][contains(text(),'Expertise')]")))
            click.click()
            time.sleep(2)
            tab_item = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'expertise-areas')]")))
        except:
            pass
            
        try:
            expertise_list = tab_item.find_elements(By.TAG_NAME, "li")
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
           
            time.sleep(2)
            for elem in expertise_list:
                x = elem.text
                print("expertise list test:", x)
                expertise += " " + x + " "
        
           
        
        except:
            print("checkpoint exception expertise no data") 
            pass
        # add sypnosis to expaertise if ther is
        try:
            synopsis = driver.find_element(By.CLASS_NAME, "synopsis").text
            expertise += " " + synopsis
        except:
           print("checkpoint exception expertise problem with list")
           pass
       
        print("name n title, expertise: ", name, title, department, institution, expertise)
        if expertise == "":
            expertise = "non available"
        
        try:
            #try if there is Biography button
            click = driver.find_element(By.XPATH, "//ul[@class = 'resp-tabs-list']//*[contains(text(), 'Biography')]")
            click.click()
            time.sleep(2)
            
            elem = driver.find_element(By.XPATH, "//*[@class = 'content' and div[contains(text(),'Biography')]]")
            
            bio_text = elem.text
            print("test bio_text = elem.text:", bio_text)
            expertise = expertise + " " + bio_text
            # bio_elems = elem.find_elements(By.TAG_NAME, "p")
            # bio_text = ""
            # for i in bio_elems:
            #     bio_text += i.text + " "
            
        except:
            print("checkpoint exception button clicked in menu for Biographys")
            pass
        
        try:
            api_gen = api_gender(name.split()[0])
          
            print("test api", api_gen)
            
        except:
            print("checkpoint exception api_gen no data")
            pass
        
        try:
            count_fix = word_counter(expertise)
            bio_word_count = count_fix[0]
            expertise = count_fix[1]
            
            print("test word_counter:", bio_word_count)
        except:
            print("checkpoint exception word_counter no data")
            pass
        
        try:
            #try serach for Publications button
            click = driver.find_element(By.XPATH, "//ul[@class = 'resp-tabs-list']//*[contains(text(), 'Publications')]")
            click.click()
            time.sleep(2)
            
            tab_item = driver.find_element(By.XPATH, "//*[@class = 'content' and div[contains(text(),'Publications')]]")
            
            try:
                
                em_tags = tab_item.find_elements(By.TAG_NAME, "em")
                counter = 0
                for i in em_tags:
                    if len(i.text.split()) > 1:
                        counter += 1
                em_tags_count = counter
                counter = 0
                
                counter_p = 0
                elements = tab_item.find_elements(By.TAG_NAME, "p")
                for elem in elements:
                    x = elem.text
                    publications.append(x)
                    if len(x.split()) > 2:
                        counter_p += 1
                
                counter_li = 0
                elements = tab_item.find_elements(By.TAG_NAME, "li")
                for elem in elements:
                    x = elem.text
                    publications.append(x)
                    if len(x.split()) > 7:
                        counter_li += 1  
                    
                #COUNT PUBLICATIONS in one <p> EX. CAMILLE SPINELLO
                #FOR LAURA COHEN TRY COUNTING <P> WHERE HAS in TEXT ")"
                # COUNTS PARENTESIS IN TEXT
                if len(publications) > 1:
                    counter =0
                    for i in publications:
                        if ")." in i:
                            counter += i.count(').')
                            counter += i.count(');')
                            counter += i.count('),')
                            continue
                        if ")" in i:
                            counter += 1
                            continue
                        else:
                            continue
                    num_of_publ = counter
                    counter = 0
                else:
                    counter =0
                    for i in publications:
                        counter += i.count(').')
                        counter += i.count(');')
                        counter += i.count('),')
                    num_of_publ = counter
                    if counter > 0:
                        num_of_publ = counter
                    counter = 0
                
                counter = 0   
                for i in publications:
                    word_list = i.split()
                    number_of_words = len(word_list)
                    temp = number_of_words
                    if temp > 7:
                        counter += 1
                    else:
                        continue
                if counter > num_of_publ:
                    num_of_publ = counter
                counter = 0
                
                #checks em_tags_count
                if em_tags_count > num_of_publ:
                    num_of_publ = em_tags_count
                
                num_of_publ = max(num_of_publ, counter_p)
                counter_p = 0
                
                #checks if <li> max
                num_of_publ = max(num_of_publ, counter_li)
            except: 
                pass
            
        except:
            num_of_publ = "non available"
            print("checkpoint exception no button load for Publications or data")
            pass
            
            
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        data.update({name:{"name": name, "institution": institution, "department": department,
                        "link": href, "title": title, "number of publications": num_of_publ,
                        "expertise": expertise, "bio_word_count": bio_word_count, "gender": api_gen[0], "probability": api_gen[1]}})
        print(data)
    
    return data

######### law
law = law_res(law_links)
df_law = pd.DataFrame.from_dict(law, orient='index')
# drop index col insert counter 0..
df_law.reset_index(drop=True, inplace=True)
# drop title others
df_law = df_law[df_law["title"].str.contains("other") == False]
# # save to excel
# df_law.to_excel("result_law_v4.xlsx", index=False)
# ###########################

######### philosophy
phil = philosophy_res(philosophy_links)
df_phil = pd.DataFrame.from_dict(phil, orient='index')
# drop index col insert counter 0..
df_phil.reset_index(drop=True, inplace=True)
# save to excel
# drop title others
df_phil = df_phil[df_phil["title"].str.contains("other") == False]
# # save to file excel
# df.to_excel("result_philosophy_v4.xlsx", index=False)
# ###########################

######### biology
biol = biology_res(biology_links)
df_biol = pd.DataFrame.from_dict(biol, orient='index')
# drop index col insert counter 0..
df_biol.reset_index(drop=True, inplace=True)
# Drop first column of dataframe
# df = df.iloc[: , 1:]
# drop title others
df_biol = df_biol[df_biol["title"].str.contains("other") == False]
# df.to_excel("result_biology_v5.xlsx", index=False)
# ##################

########## cs
cs = cs_res(cs_links)
df_cs = pd.DataFrame.from_dict(cs, orient='index')
# drop index col insert counter 0..
df_cs.reset_index(drop=True, inplace=True)
# Drop first column of dataframe
# df = df.iloc[: , 1:]
# drop title others
df_cs = df_cs[df_cs["title"].str.contains("other") == False]
# df.to_excel("result_cs_v2.xlsx", index=False)
# ###################

# ########## psychology
psyco = psycho_res(psychology_links)
df_psy = pd.DataFrame.from_dict(psyco, orient='index')
# drop index col insert counter 0..
df_psy.reset_index(drop=True, inplace=True)
# Drop first column of dataframe
# df = df.iloc[: , 1:]
# drop title others
df_psy = df_psy[df_psy["title"].str.contains("other") == False]
# df.to_excel("result_psyco_v2.xlsx", index=False)
# ###################


frames = [df_phil, df_biol, df_cs, df_psy, df_law]
df_all = pd.concat(frames)
df_all.to_excel("result.xlsx", index=False)

driver.close()

