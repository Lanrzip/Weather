"""
若要使用短信功能请更改send_message函数中的相应参数
"""

import re
import time
import requests
from lxml import etree
from twilio.rest import Client
import pandas as pd


class Weather:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    }

    def sub_blank(self, text):
        return re.sub(r"\s", "", text)

    def parse_url(self, url):
        response = requests.get(url, headers=self.headers)
        text = response.content.decode('utf-8')
        html = etree.HTML(text)
        day_list = html.xpath("//div[@class='hanml']/div")
        tomorrow = day_list[1]
        province_list = tomorrow.xpath("./div")
        for province in province_list:
            city = province.xpath(".//tr")
            first = True
            province = self.sub_blank("".join(city[2].xpath("./td[1]//text()")))
            for tr in city[2:]:
                detail = {}
                tds = tr.xpath(".//td")

                name = self.sub_blank("".join(tds[-8].xpath(".//text()")))
                condition = tds[-7].xpath(".//text()")[0]
                wind = self.sub_blank("".join(tds[-6].xpath(".//text()")))
                high_temp = tds[-5].xpath(".//text()")[0]
                condition_night = tds[-4].xpath(".//text()")[0]
                wind_night = self.sub_blank("".join(tds[-3].xpath(".//text()")))
                low_temp = tds[-2].xpath(".//text()")[0]
                detail['省/直辖市'] = province
                detail['城市'] = name
                detail['白天天气'] = condition
                detail['白天风况'] = wind
                detail['最高气温'] = high_temp
                detail['夜间天气'] = condition_night
                detail['夜间风况'] = wind_night
                detail['最低气温'] = low_temp
                self.city_list.append(detail)
                
    def job(self):
        self.city_list = []
        self.last_time = time.time()
        area_list = ['hb', 'db', 'hd', 'hz', 'hn', 'xb', 'xn']
        for area in area_list:
            self.parse_url(f"http://www.weather.com.cn/textFC/{area}.shtml")

    def send_message(self, city, city_list):
        df = pd.DataFrame(city_list)

        city = city
        cond = df.query("城市 == @city").squeeze().astype(str).to_list()
        text = "\n" + cond[1] + "白天天气：" + cond[2] + " " + cond[3] + \
               " " + "最高气温" + cond[4] + "°C" + "\n    " + \
               "夜间天气：" + cond[5] + " " + cond[6] + \
               " " + "最低气温" + cond[7] + "°C"

        # 需更改的参数
        account = "ACCOUNT"
        token = "TOKEN"
        from_ = "FROM"
        to = "TO"

        client = Client(account, token)
        message = client.messages.create(to=to,
                                         from_=from_,
                                         body=text)


if __name__ == '__main__':

    weather = Weather()
    weather.job()
    weather.send_message('济南', weather.city_list)
    while True:
        if time.time() - weather.last_time >= 86400:
            weather.job()
            print('最新爬取时间更新到{}'.format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                     time.localtime(weather.last_time))))

            weather.send_message('济南', weather.city_list)

        else:
            time.sleep(1)
