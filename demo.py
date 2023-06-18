import csv
import time
# from selenium import WebElement
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

job_roles = ['Python Developer', 'Manager', 'Computer Operator', 'Data Entry', 'Java Developer','Data Analyst','network engineer', 'Web Developer', 'cloud engineer', 'Database Administrator']
job_loc = ['Delhi', 'Mumbai', 'Pune', 'Bangalore','Kanpur', 'Kolkata', 'chandigarh']
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service("D:\Applications\Chrome Driver\chromedriver.exe"))

driver.get('https://in.indeed.com/')

what = driver.find_element(by='xpath', value="//input[@name='q']")
what.send_keys("" + job_roles[4])
where = driver.find_element(by='xpath', value="//input[@name='l']")
where.send_keys("" + job_loc[1])
search_button = driver.find_element(by='xpath', value='//*[@type="submit"]')
search_button.click()

head = ['Job Title', 'Company', 'Location', 'Salary', 'Description', 'URL']
with open('Job_roles.csv', 'a', newline='', encoding='utf-8') as file1:
    writor = csv.DictWriter(file1, head)
    # writor.writeheader()

    for iteration in range(0, 2):
        try:
            indeed_cards = driver.find_elements(by="xpath",
                                                value="//h2[@class='jobTitle css-1h4a4n5 eu4oa1w0']//a | //h2[@class='jobTitle jobTitle-newJob css-bdjp2m eu4oa1w0']//a")
            next_page = driver.find_element(by="xpath", value="//a[@class='css-13p07ha e8ju0x50']")
            next_page_link = next_page.get_attribute('href')
            urls = []
            for card_url in indeed_cards:
                urls.append(card_url.get_attribute('href'))
            companies = driver.find_elements("xpath", "//span[@class='companyName']")
            companylist = []
            for comp in companies:
                companylist.append(comp.text)
            locations = driver.find_elements("xpath", "//div[@class='companyLocation']")
            locationlist = []
            for loc in locations:
                locationlist.append(loc.text)
        except NoSuchElementException:
            pass
        for one_card in indeed_cards:
            try:
                job_data = {'Job Title': '', 'Company': '', 'Location': '', 'Salary': '', 'Description': '',
                            'URL': ''}
                card_no = indeed_cards.index(one_card)
                url = urls[card_no]

                company = companylist[card_no]
                job_data.update({'Company': company})
                # print(job_data['Company'])

                location = locationlist[card_no]
                job_data.update({'Location': location})
                # print(job_data['Location'])

                driver.get(url)

                job_title = driver.find_element("xpath", "//div[@class='jobsearch-JobInfoHeader-title-container ']")
                job_data.update({'Job Title': job_title.text})
                # print(job_data['Job Title'])
                try:
                    findsal = driver.find_element("xpath",
                                                  "//div[@class='css-fhkva6 eu4oa1w0'][contains(text(),'Salary')]")
                    if findsal.text == 'Salary':
                        salary = driver.find_element("xpath", "//span[@class='css-2iqe2o eu4oa1w0']")
                        job_data.update({'Salary': salary.text})
                except NoSuchElementException:
                    pass

                desc_ele = driver.find_element("xpath", "//div[@class='jobsearch-jobDescriptionText']")
                desc = desc_ele.text
                weird_char = '`'
                job_data.update({'Description': desc.replace('\n', weird_char)})

                job_data.update({'URL': url})
                # print(job_data)
                driver.get(next_page_link)
            except NoSuchElementException:
                pass
            # print(job_data)
            if job_data['Job Title'] != '' and job_data['Location'] != '' and job_data['Description'] != '':
                writor.writerow(job_data)

    file1.close()
