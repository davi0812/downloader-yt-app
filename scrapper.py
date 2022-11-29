from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import requests
import re
import mysql.connector
from datetime import datetime

mydb = mysql.connector.connect(
    host="159.223.207.111",
    user="sql_dev_mavmedia",
    password="acDf7XtRxeibxyJw",
    database="sql_dev_mavmedia"
)


def insert_db(domain_name, status, description=None, keywords=None, categories=None, price=None, logo_url=None,
              date=None):
    mycursor = mydb.cursor()
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    sql = "INSERT INTO scrapper (domain_name,description,keywords,categories,price,logo_url,status, date) VALUES (%s,%s,%s, " \
          "%s,%s,%s, %s, %s) "
    val = (domain_name, description, keywords, categories, price, logo_url, status, formatted_date)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")


def update_db(domain_name, status, description=None, keywords=None, categories=None, price=None, logo_url=None):
    print("Actualizando")
    mycursor = mydb.cursor(buffered=True)
    sql = "update scrapper set description=%s, keywords=%s, categories=%s, price=%s, logo_url=%s, status=%s where domain_name=%s"
    val = (description, keywords, categories, price, logo_url, status, domain_name)
    mycursor.execute(sql, val)
    mydb.commit()
    print("record updated.")


def save_domains(driver, pages):
    for x in range(1, pages + 1):
        driver.get(f"https://www.brandbucket.com/names?page={x}")
        names = driver.find_elements(By.CSS_SELECTOR, ".domainCardDetail > span:first-child")
        for dom in names:
            link = dom.get_attribute("innerText")
            insert_db(domain_name=link, status="Pending")


def scrape(driver, url):
    print("Scrapping: ", url)
    driver.get(url)

    # domain name
    elem = driver.find_element(By.CSS_SELECTOR, ".productDetailHeader h1 > span")
    dataDomaninName = elem.get_attribute("innerText")

    # description
    elem = driver.find_element(By.CSS_SELECTOR, ".productDesc")
    dataDescription = elem.get_attribute("innerText")

    # keywords
    elem = driver.find_elements(By.CSS_SELECTOR, "#keywordTags a")
    dataKeys = []
    for keyw in elem:
        dataKeys.append(keyw.get_attribute("innerText"))
    dataKeywords = ", ".join(dataKeys)

    # categories
    elem = driver.find_elements(By.CSS_SELECTOR, "#categoryTags a")
    dataCats = []
    for catw in elem:
        dataCats.append(catw.get_attribute("innerText"))
    dataCategories = ", ".join(dataCats)

    # price
    elem = driver.find_element(By.CSS_SELECTOR, ".priceFancy > span")
    dataPrice = elem.get_attribute("innerText")
    elem = driver.find_element(By.CSS_SELECTOR, ".priceFancy div > sup")
    dataPrice += elem.get_attribute("innerText")

    # logo url
    elem = driver.find_element(By.CSS_SELECTOR, ".productSlideLogo > img")
    dataLogoUrl = elem.get_attribute("src")

    # download logo
    response = requests.get(dataLogoUrl)
    lreg = re.findall(r'\w+(?:(?!\.\w+).)*', dataDomaninName)[0]
    logoName = f"logos/sql_{lreg}.png"
    open(logoName, "wb").write(response.content)
    # update database
    update_db(dataDomaninName, "Ready", dataDescription, dataKeywords, dataCategories, dataPrice, dataLogoUrl)


def get_pending(lim1, lim2):
    service = Service(executable_path="chromedriver")
    # proxy_url = "193.233.140.130:8085"
    # proxy = Proxy()
    # proxy.proxy_type = ProxyType.MANUAL
    # proxy.http_proxy = proxy_url
    # proxy.ssl_proxy = proxy_url
    # capabilities = webdriver.DesiredCapabilities.CHROME
    # proxy.add_to_capabilities(capabilities)
    # driver = webdriver.Chrome(service=service, desired_capabilities=capabilities)
    driver = webdriver.Chrome(service=service)
    driver.get('http://whatismyipaddress.com')
    cursor = mydb.cursor(buffered=True)
    cursor.execute(f"SELECT * FROM scrapper where status = 'Pending' limit {lim1}, {lim2}")
    row = cursor.fetchone()
    while row is not None:
        domName = row[1]
        link = f"https://www.brandbucket.com/names/{domName}?source=list"
        scrape(driver, link)
        row = cursor.fetchone()
