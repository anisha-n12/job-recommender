import csv
import time
# from selenium import WebElement
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

job_roles=['Python Developer', 'Manager', 'Computer Operator', 'Data Entry', 'Java Developer','Data Analyst','network engineer', 'Web Developer', 'cloud engineer', 'Database Administrator']
job_loc=['Mumbai', 'Delhi', 'Pune', 'Lucknow','Bangalore','Jaipur', 'Kolkata', 'Chennai','Hyderabad','Chandigarh','Kanpur']
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service("D:\Applications\Chrome Driver\chromedriver.exe"))
driver.get('https://www.linkedin.com')
username = driver.find_element(by='id', value="session_key")
username.send_keys("nemadeanisha@gmail.com")
password = driver.find_element(by='id', value="session_password")
password.send_keys("One@2Three")
sign_button = driver.find_element(by='xpath', value='//*[@type="submit"]')
sign_button.click()

driver.get('https:www.google.com')

search_query = driver.find_element(by='name', value='q')
search_query.send_keys("site:linkedin.com/in/ AND "+job_roles[5]+" AND "+job_loc[0])
search_query.send_keys(Keys.RETURN)

head = ['Name', 'Job Title', 'Company', 'College', 'Location', 'Skills', 'URL']
with open('Profile_data.csv', 'a',newline='',encoding='utf-8') as file1:
    writor = csv.DictWriter(file1, head)
    # writor.writeheader()
    next_link=''
    for page in range(0, 2):
        try:
            linkedin_urls = driver.find_elements(by="xpath", value="//div[@class='v7W49e']//a")
            linkedin_url = []
            next_btn = driver.find_element("xpath", "//td[@class='d6cvqb BBwThe']//a")
            next_link = next_btn.get_attribute('href')
            for x1 in linkedin_urls:
                linkedin_url.append(x1.get_attribute('href'))

            profile_data = {}

            for i in range(0, len(linkedin_url)):
                try:
                    profile_data = {'Name': '', 'Job Title': '', 'Company': '', 'College': '', 'Location': '', 'Skills': [],
                                    'URL': ''}
                    sr = []
                    driver.get(linkedin_url[i])
                    time.sleep(5)
                    name = driver.find_element("xpath", "//div[@class='mt2 relative']//h1")
                    profile_data.update({'Name': name.text})
                    job = driver.find_element(by="xpath", value="//div[@class ='text-body-medium break-words']")
                    profile_data.update({'Job Title': job.text})
                    comcol = driver.find_elements(by="xpath", value="//li[@class='pv-text-details__right-panel-item']")
                    if len(comcol) == 2:
                        profile_data.update({'Company': comcol[0].text, 'College': comcol[1].text})
                    location = driver.find_element(by="xpath",
                                                   value="//span[@class='text-body-small inline t-black--light break-words']")
                    profile_data.update({'Location': location.text})
                    skills = driver.find_elements(by="xpath", value="//div[@class='pvs-list__footer-wrapper']")
                    skill_link = ''
                    if len(skills) != 0:
                        for k in range(0, len(skills) - 1):
                            try:
                                skill_link = skills[k].find_element("partial link text", "skill")
                            except NoSuchElementException:
                                continue

                        if skill_link != '':
                            # print(skill_link)
                            driver.get(skill_link.get_attribute('href'))
                            time.sleep(5)
                            skill = driver.find_elements("xpath", "//span[@class='mr1 hoverable-link-text t-bold']")
                            for ski in skill:
                                if ski.text != '':
                                    strfilter = ski.text
                                    filterlist = strfilter.splitlines()
                                    sr.append(filterlist[0])
                        else:
                            pass
                    profile_data.update({'Skills': sr})

                    profile_data.update({'URL': linkedin_url[i]})
                except NoSuchElementException:
                    pass
                if profile_data['Skills'] != [] and profile_data['Location'] != '':
                    writor.writerow(profile_data)
        except NoSuchElementException:
            pass

        if next_link!='':
            driver.get(next_link)
        else:
            break
    file1.close()
