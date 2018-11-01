import requests
import urllib
import urllib3
import operator
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


CC_RATIO = [1, 0.1060, 1.2489, 0.1943, 0.0941, 6.9732, 0.0188, 0.00029984, 0.000457,
             0.2475, 1.666, 0.3431, 0.1305, 1.8743, 22.9512, 1.9152, 0.2106, 6.9755,
             0.2125, 0.00217, 0.0115, 5.0345, 0.0100, 0.4722, 2.0719, 1.8592, 0.2254,
             0.8894, 4.5506, 0.827, 1.8987, 5.3009, 0.0618, 0.0061, 1.8734, 1.8173,
             6.9186, 8.9059, 6.9746, 7.8927]


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




# print(len(CC_LIST))
# print(len(CC_RATIO))

cc_ratio_dict = {}
cc_all_dict = {}
for cc, ratio, full in zip(CC_LIST, CC_RATIO, CC_ALL_LIST):
    cc_ratio_dict[cc] = ratio
    cc_all_dict[cc] = full

# print(cc_ratio_dict)
# print(cc_all_dict)

db = client.steam
pay_games = db.raw_data.find({"price": {"$gt": "0"}})
pay_games_id = []
for pay_game in pay_games:
    pay_games_id.append(pay_game['appid'])
# getSteamDB_HistoryPrice()
print(pay_games_id)

res = {}
for cc in CC_LIST:
    res[cc] = []

# pay_games_id = [578080]
for appid in pay_games_id:
    prices = db.raw_history_price.find_one({"appid": appid})
    # print(prices)
    for cc in CC_LIST:
        prices_cc = prices[cc]
        if not len(prices_cc) == 0:
            res[cc].append(prices_cc[-1][-1] * cc_ratio_dict[cc])

for key, val in res.items():
    res[key] = sum(val)/len(val)

sorted_res = sorted(res.items(), key=lambda x: x[1])
print(sorted_res)

res_ls = []
res_data_ls = []
for key,value in sorted_res:
    res_ls.append("\"" + cc_all_dict[key] + "\"")
    res_data_ls.append(str(value))

print(",".join(res_ls))
print(",".join(res_data_ls))

