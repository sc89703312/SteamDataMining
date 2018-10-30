import requests
import urllib
import urllib3
import json
from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)


CC_LIST = ["cn", "ru", "tr", "ar", "in", "pk", "kz", "vn", "id",
           "ua", "my", "mx", "ph", "br", "kw", "qa", "th", "az",
           "uy", "co", "cr", "sg", "cl", "za", "pe", "sa", "tw",
           "hk", "nz", "no", "ae", "ca", "jp", "kr", "il", "pl",
           "ch", "uk", "us", "eu"]

CC_ALL_LIST = ["Chinese Yuan Renminbi", "Russian Ruble", "Turkish Lira", "Argentine Peso", "Indian Rupee", "South Asia - U.S. Dollar", "Kazakhstani Tenge", "Vietnamese Dong", "Indonesian Rupiah",
               "Ukrainian Hryvnia", "Malaysian Ringgit", "Mexican Peso", "Philippine Peso", "Brazilian Real", "Kuwaiti Dinar", "Qatari Riyal", "Thai Baht", "CIS - U.S. Dollar",
               "Uruguayan Peso", "Colombian Peso", "Costa Rican Colon", "Singapore Dollar", "Chilean Peso", "South African Rand", "Peruvian Nuevo Sol", "Saudi Riyal", "Taiwan Dollar",
               "Hong Kong Dollar", "New Zealand Dollar", "Norwegian Krone", "U.A.E. Dirham", "Canadian Dollar", "Japanese Yen", "South Korean Won", "Israeli New Shekel", "Polish Zloty",
               "Swiss Franc", "British Pound", "U.S. Dollar", "Euro"]

url = "https://steamdb.info/api/GetPriceHistory/"
params = {"appid":730, "cc": "cn"}



## 爬取SteamDB中游戏的tags
def test_tag(s):
    return s.string == "store_tags"

filepath = "top100_appids.txt"
file = open(filepath, 'r', encoding="utf-8")
appids = file.readline().split(" ")
print(appids)
print(len(appids))

def getSteamDB_UserTags():
    fo = open('top100_tags.txt', 'a', encoding='utf-8')
    driver = webdriver.PhantomJS("/Applications/phantomjs-2.1.1/bin/phantomjs")
    for appid in appids:
        steam_db_url = "https://steamdb.info/app/" + appid +"/info/"
        print(steam_db_url)
        driver.get(steam_db_url)
        soup = BeautifulSoup(driver.page_source, 'xml')
        data = soup.findAll(test_tag)
        tags_td = data[0].next_sibling.next_sibling
        tags = []
        for ul in tags_td:
            for li in ul:
                tag = li.contents[-1].string
                tags.append(tag)

        tags_str = ",".join(tags)
        print(tags_str)
        fo.write(",".join(tags))
        fo.write("\n")

def getSteamDB_HistoryPrice():
    driver = webdriver.PhantomJS("/Applications/phantomjs-2.1.1/bin/phantomjs")
    db = client.steam
    # fo = open('top100_history_prices.txt')
    # appids = ["730"]
    for appid in appids:
        hp_dict = {"appid": int(appid)}
        for cc in CC_LIST:
            steam_db_url = "https://steamdb.info/api/GetPriceHistory/?appid=" + appid +"&cc=" + cc
            print(steam_db_url)
            driver.get(steam_db_url)
            soup = BeautifulSoup(driver.page_source, 'xml')
            data = soup.find('pre')
            historyPrice = json.loads(data.text)
            if historyPrice['success']:
                hp_list = historyPrice['data']['final']
                hp_dict[cc] = hp_list
        print(hp_dict)
        res = db.raw_history_price.insert_one(hp_dict)
        print(res.inserted_id)




# getSteamDB_HistoryPrice()

