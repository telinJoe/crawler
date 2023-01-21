from selenium import webdriver
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import datetime
import time
import json

#crawler class 爬蟲套件
class crawler:
    #@staticmethod
    #擷取今日電力資訊 1.日期 2.更新時間 3.目前用電量 4.使用率 5.預估最高用電 6.尖峰使用率 7.今日最大供電能力 8.供電色號
    def electricityinfo_current(self, strDate = datetime.datetime.today().date()):
        #今日日期
        dataTimeStampP1 = 'null'
        #更新時間
        dataTimeStampP2 = 'null'
        #目前用電量
        latest_load = 'null'
        #使用率
        latest_load_perc = 'null'
        #預估最高用電
        load_forecast_max = 'null'
        #尖峰使用率
        load_forecast_max_perc = 'null'
        #今日最大供電能力
        supply_arranged_max = 'null'
        #供電狀況
        lightState = 'null'
        # 擷取次數
        num = 0
        try:
            print('--cralwer start--')
            options = Options()
            options.add_argument('--headless')
            chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=options)
            while num < 3:
                print('try '+str(num+1))
                driver.get("https://www.taipower.com.tw/d006/loadGraph/loadGraph/load_briefing3.html")
                driver.implicitly_wait(10)
                time.sleep(1)
                dataTimeStampP1 = driver.find_element(By.ID, 'dataTimeStampP1').text
                dataTimeStampP2 = driver.find_element(By.ID, 'dataTimeStampP2').text.replace("更新", "")
                latest_load = driver.find_element(By.ID, 'latest_load').text.replace(",", "")
                latest_load_perc = driver.find_element(By.ID, 'latest_load_perc').text + "%"
                load_forecast_max = driver.find_element(By.ID, 'load_forecast_max').text.replace(",", "")
                load_forecast_max_perc = driver.find_element(By.ID, 'load_forecast_max_perc').text + "%"
                supply_arranged_max = driver.find_element(By.ID, 'supply_arranged_max').text.replace(",", "")
                #lighttext = driver.find_element(By.ID, 'lighttext').text[0:4]
                num += 1
                #確認是否擷取到數據 沒有最多retry三次
                if not latest_load == 'null' and not latest_load_perc == 'null' and not load_forecast_max == 'null' and not load_forecast_max_perc == 'null' and not supply_arranged_max == 'null':
                    value = float(supply_arranged_max) - float(latest_load)
                    percent = (value/float(supply_arranged_max)) * 100
                    if percent > 10:
                        lightState = '#00DD00'
                    elif 10 > percent >= 6:
                        lightState = '#FFFF00'
                    elif percent < 6 and value > 90:
                        lightState = '#FFA500'
                    elif 90 > value >= 50:
                        lightState = '#FF0000'
                    elif value < 50:
                        lightState = '#444444'
                    break
        #網頁擷取錯誤例外處理
        except:
            print('error occured')
            pass
        print('--cralwer end--')
        data = {'dataTimeStampP1': dataTimeStampP1, 'dataTimeStampP2': dataTimeStampP2, 'latest_load': latest_load, 'latest_load_perc': latest_load_perc, 'load_forecast_max': load_forecast_max, 'load_forecast_max_perc': load_forecast_max_perc, 'supply_arranged_max': supply_arranged_max, 'lightState': lightState}
        return data

    # 擷取昨日電力供需資訊 1.昨日日期 2.昨日最高用電量 3.尖峰備轉容量率
    def electricityInfo_yday(self, strDate=datetime.datetime.today().date()):
        #昨日日期
        ydaytime = 'null'
        #昨日最高用電量
        load_max_yday = 'null'
        #尖峰備轉容量率
        rsv_perc_yday = 'null'
        #擷取次數
        num = 0
        try:
            print('--cralwer start--')
            options = Options()
            options.add_argument('--headless')
            chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=options)
            while num < 3:
                print('try ' + str(num + 1))
                driver.get("https://www.taipower.com.tw/d006/loadGraph/loadGraph/load_reserve_.html")
                driver.implicitly_wait(10)
                time.sleep(1)
                ydaytime = driver.find_element(By.ID, 'ydaytime').text
                load_max_yday = driver.find_element(By.ID, 'load_max_yday').text.replace(",", "")
                rsv_perc_yday = driver.find_element(By.ID, 'rsv_perc_yday').text + "%"
                num += 1
                # 確認是否擷取到數據 沒有最多retry三次
                if not ydaytime == 'null' and not load_max_yday == 'null' and not rsv_perc_yday == 'null':
                    break
        # 網頁擷取錯誤例外處理
        except:
            print('error occured')
            pass
        print('--cralwer end--')
        data = {'ydaytime': ydaytime, 'load_max_yday': load_max_yday, 'rsv_perc_yday': rsv_perc_yday}
        return data

    # 擷取未來電力供需資訊(一周) 1.更新日期 2.日期 3.day 4.淨尖峰供電能力 5.尖峰負載 6.備轉容量 7.備轉容量率 8.備轉容量供電色號
    def electricityInfo_future(self, strDate = datetime.datetime.today().date()):
        data = []
        try:
            print('--cralwer start--')
            options = Options()
            options.add_argument('--headless')
            chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=options)
            for i in range(1, 8):
                #更新日期
                datetime = 'null'
                #日期
                dateStr = 'null'
                #day
                dayStr = 'null'
                #淨尖峰供電能力
                supply = 'null'
                #尖峰負載
                load = 'null'
                #備轉容量
                value = 'null'
                #備轉容量率
                percent = 'null'
                # 備轉容量燈號
                lightState = 'null'
                #擷取次數
                num = 0
                while num < 3:
                    print('try ' + str(num + 1))
                    driver.get("https://www.taipower.com.tw/d006/loadGraph/loadGraph/load_forecast_.html")
                    driver.implicitly_wait(10)
                    #time.sleep(1)
                    datetime = driver.find_element(By.ID, 'datetime').text
                    dateStr = driver.find_element(By.ID, 'date'+str(i)).text[0:5]
                    dayStr = driver.find_element(By.ID, 'date'+str(i)).text[7:10]
                    supply = driver.find_element(By.ID, 'supply'+str(i)).text
                    load = driver.find_element(By.ID, 'load'+str(i)).text
                    value = int(driver.find_element(By.ID, 'value'+str(i)).text)
                    percent = float(driver.find_element(By.XPATH, '//*[@id="percent'+str(i)+'"]/td').text.strip('%'))
                    num += 1
                    # 確認是否擷取到數據 沒有最多retry三次
                    if not dateStr == 'null' and not dayStr == 'null' and not supply == 'null' and not load == 'null' and not value == 'null' and not percent == 'null':
                        if percent > 10:
                            lightState = '#00DD00'
                        elif 10 > percent >= 6:
                            lightState = '#FFFF00'
                        elif percent < 6 and value > 90:
                            lightState = '#FFA500'
                        elif 90 > value >= 50:
                            lightState = '#FF0000'
                        elif value < 50:
                            lightState = '#444444'
                        data.append({'datetime': datetime, 'dateStr': dateStr, 'dayStr': dayStr, 'supply': supply, 'load': load, 'value': value, 'percent': str(percent) + "%", 'lightState': lightState})
                        break
                # 確認是否擷取到數據 沒有最多retry三次
                if num == 3:
                    data.append({'datetime': datetime, 'dateStr': dateStr, 'dayStr': dayStr, 'supply': supply, 'load': load, 'value': value, 'percent': percent, 'lightState': lightState})
        # 網頁擷取錯誤例外處理
        except:
            print('error occured')
            pass
        print('--cralwer end--')
        return data

    # 擷取太陽能 1.更新日期 2.裝置容量 3.淨發電量 4.裝置容量淨發電量比
    def solar_info(self, strDate=datetime.datetime.today().date()):
        #更新日期
        datetime = 'null'
        #裝置容量
        capacity_stored = 'null'
        #淨發電量
        electricity_stored = 'null'
        #裝置容量/淨發電量比
        percent = 'null'
        # 擷取次數
        num = 0
        try:
            print('--cralwer start--')
            options = Options()
            options.add_argument('--headless')
            chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=options)
            while num < 3:
                print('try ' + str(num + 1))
                driver.get("https://www.taipower.com.tw/d006/loadGraph/loadGraph/genshx_.html")
                driver.implicitly_wait(10)
                #time.sleep(1)
                datetime = driver.find_element(By.ID, 'datetime').text
                capacity_stored = driver.find_element(By.XPATH, '//*[@id="unitgentab"]/tbody/tr[185]/td[2]').text
                capacity_stored = float(capacity_stored[0:capacity_stored.find('(')])
                electricity_stored = driver.find_element(By.XPATH, '//*[@id="unitgentab"]/tbody/tr[185]/td[3]').text[0:5]
                electricity_stored = float(electricity_stored[0:electricity_stored.find('(')])
                num += 1
                # 確認是否擷取到數據 沒有最多retry三次
                if not datetime == 'null' and not capacity_stored == 'null' and not electricity_stored == 'null':
                    if electricity_stored == 0.0:
                        percent = round(capacity_stored/100, 2)
                    else:
                        percent = round((electricity_stored/capacity_stored)*100, 2)
                    break
        # 網頁擷取錯誤例外處理
        except:
            print('error occured')
            pass
        data = {'datetime': datetime, 'capacity_stored': str(capacity_stored), 'electricity_stored': str(electricity_stored), 'percent': str(percent) + "%"}
        print('--cralwer end--')
        return data

    #擷取電力交易平台平均結清價格 1.調頻備轉 2.即時備轉 3.補充備轉
    def electricity_deal(self, strDate = datetime.datetime.today().date()):
        #調頻備轉
        FMTransferAvePrice = 'null'
        #即時備轉
        realtimeTransferAvePrice = 'null'
        #補充備轉
        fartherTransferAvePrice = 'null'
        # 擷取次數
        num = 0
        try:
            print('--cralwer start--')
            options = Options()
            options.add_argument('--headless')
            chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=options)
            while num < 3:
                print('try ' + str(num + 1))
                driver.get("https://etp.taipower.com.tw/")
                driver.implicitly_wait(10)
                #time.sleep(1)
                FMTransferAvePrice = driver.find_element(By.XPATH, '//table[@class="announce_board" and position()=1]/tbody/tr[2]/td[2]').text
                realtimeTransferAvePrice = driver.find_element(By.XPATH, '//table[@class="announce_board" and position()=1]/tbody/tr[3]/td[2]').text
                fartherTransferAvePrice = driver.find_element(By.XPATH, '//table[@class="announce_board" and position()=1]/tbody/tr[4]/td[2]').text
                num += 1
                # 確認是否擷取到數據 沒有最多retry三次
                if not FMTransferAvePrice == 'null' and not realtimeTransferAvePrice == 'null' and not fartherTransferAvePrice == 'null':
                    break
        # 網頁擷取錯誤例外處理
        except:
            print('error occured')
            pass
        data = {'FMTransferAvePrice': FMTransferAvePrice, 'realtimeTransferAvePrice' :realtimeTransferAvePrice, 'fartherTransferAvePrice': fartherTransferAvePrice}
        print('--cralwer end--')
        return data

    #擷取電力交易平台即時備轉 當天24小時1.小時 2.得標容量(國營) 3.得標容量(民營) 4.得標容量(非交易) 5.結清價格
    def electricity_deal_realtimeStored(self, erer, strDate=datetime.datetime.today().date()):
        uml = r'https://etp.taipower.com.tw/'
        hourlyList = []
        futures = []
        options = Options()
        options.add_argument('--headless')
        chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
        pool = ThreadPoolExecutor(max_workers=4)
        # 多工執行
        for i in range(0, 24, 6):
            future = pool.submit(erer, chrome_service, options, i, '6')
            futures.append(future)
        pool.shutdown()
        for fu in futures:
            print(fu.result())
            hourlyList.extend(fu.result())
        #date = np.array(hourlyList).ravel()
        print('--cralwer end--')
        return hourlyList

    # 擷取電力交易平台補充備轉 當天24小時1.小時 2.得標容量(國營) 3.得標容量(民營) 4.得標容量(非交易) 5.結清價格
    def electricity_deal_replenishStore(self, strDate=datetime.datetime.today().date()):
        hourlyList = []
        futures = []
        options = Options()
        options.add_argument('--headless')
        chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
        pool = ThreadPoolExecutor(max_workers=4)
        # 多工執行
        for i in range(0, 24, 6):
            future = pool.submit(self.eacHourValue, chrome_service, options, i, '7')
            futures.append(future)
        pool.shutdown()
        for fu in futures:
            hourlyList.append(fu.result())
        date = np.array(hourlyList).ravel()
        print('--cralwer end--')
        return date

    def eacHourValue(self, chrome_service, options, h, n):
        driver = webdriver.Chrome(service=chrome_service, options=options)
        driver.get('https://etp.taipower.com.tw/')
        driver.implicitly_wait(10)
        #time.sleep(1)
        hourlyList = []
        actions = ActionChains(driver)
        print('start', h, 'h value get')
        for i in range(h, h + 6):
            StateOwnedStored = 'null'
            # 得標容量(民營)
            investorownedStored = 'null'
            # 得標容量(非交易)
            nodealStored = 'null'
            # 結清價格
            price = 'null'
            for j in range(0, 2):
                actions.move_to_element(driver.find_element(By.XPATH,'(//*[@class="recharts-layer recharts-bar-rectangles"])[' + n + ']/*/*[' + str(i + 1) + ']'))
                actions.perform()
                time.sleep(0.2)
            StateOwnedStored = driver.find_elements(By.CLASS_NAME, "recharts-tooltip-item-value")[0].text
            investorownedStored = driver.find_elements(By.CLASS_NAME, "recharts-tooltip-item-value")[1].text
            nodealStored = driver.find_elements(By.CLASS_NAME, "recharts-tooltip-item-value")[2].text
            price = driver.find_elements(By.CLASS_NAME, "recharts-tooltip-item-value")[3].text
            hourly = {'hour': str(i), 'StateOwnedStored': str(StateOwnedStored), 'investorownedStored': str(investorownedStored), 'nodealStored': str(nodealStored), 'price': str(price)}
            hourlyList.append(hourly)
        print('end', h, 'h value get')
        return hourlyList

    # 擷取交通部氣象局彰化縣鹿港鎮 1.地區 2.明天日期 3.時段 4.溫度 5.降雨機率
    def cwb_LugangInfo(self, strDate=datetime.datetime.today().date()):
        cwbinfoList = []
        PC3_D = '1' if datetime.datetime.now().hour >= 22 else '2'
        IDList = [[PC3_D, '00', '00', '03'], [PC3_D, '03', '00', '03'], [PC3_D, '06', '06', '09'], [PC3_D, '09', '06', '09'], [PC3_D, '12', '12', '15'], [PC3_D, '15', '12', '15'], [PC3_D, '18', '18', '21'], [PC3_D, '21', '18', '21']]
        print('--cralwer start--')
        options = Options()
        options.add_argument('--headless')
        chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)
        for i in range(len(IDList)):
            # 明天日期
            date = 'null'
            # 時段
            period = 'null'
            # 溫度
            temperature = 'null'
            # 降雨機率
            PofP = 'null'
            # 擷取次數
            num = 0
            cwbinfo = {'district': '彰化縣鹿港鎮', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
            try:
                while num < 3:
                    print('try ' + str(num + 1))
                    driver.get("https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=1000702")
                    driver.implicitly_wait(10)
                    #time.sleep(1)
                    date = driver.find_element(By.ID, 'PC3_D' + IDList[i][0] + '').text.replace("\n", " ")
                    period = driver.find_element(By.XPATH, '//*[@id="PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span').text
                    temperature = driver.find_element(By.XPATH, '//*[@headers="PC3_T PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span[1]').text
                    PofP = driver.find_element(By.XPATH, '//*[@headers="PC3_Po PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][2] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][3] + '"]').text
                    num += 1
                    # 確認是否擷取到數據 沒有最多retry三次
                    if not date == 'null' and not period == 'null' and not temperature == 'null' and not PofP == 'null':
                        cwbinfo = {'district': '彰化縣鹿港鎮', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
                        break
                cwbinfoList.append(cwbinfo)
            # 網頁擷取錯誤例外處理
            except:
                print('error occured')
                pass

        data = cwbinfoList
        print('--cralwer end--')
        return data

    # 擷取交通部氣象局雲林縣崙背鄉 1.地區 2.明天日期 3.時段 4.溫度 5.降雨機率
    def cwb_LunbeiInfo(self, strDate=datetime.datetime.today().date()):
        cwbinfoList = []
        PC3_D = '1' if datetime.datetime.now().hour >= 22 else '2'
        IDList = [[PC3_D, '00', '00', '03'], [PC3_D, '03', '00', '03'], [PC3_D, '06', '06', '09'], [PC3_D, '09', '06', '09'], [PC3_D, '12', '12', '15'], [PC3_D, '15', '12', '15'], [PC3_D, '18', '18', '21'], [PC3_D, '21', '18', '21']]
        print('--cralwer start--')
        options = Options()
        options.add_argument('--headless')
        chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)
        for i in range(len(IDList)):
            # 明天日期
            date = 'null'
            # 時段
            period = 'null'
            # 溫度
            temperature = 'null'
            # 降雨機率
            PofP = 'null'
            # 擷取次數
            num = 0
            cwbinfo = {'district': '雲林縣崙背鄉', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
            try:
                while num < 3:
                    print('try ' + str(num + 1))
                    driver.get("https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=1000912")
                    driver.implicitly_wait(10)
                    #time.sleep(1)
                    date = driver.find_element(By.ID, 'PC3_D' + IDList[i][0] + '').text.replace("\n", " ")
                    period = driver.find_element(By.XPATH, '//*[@id="PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span').text
                    temperature = driver.find_element(By.XPATH, '//*[@headers="PC3_T PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span[1]').text
                    PofP = driver.find_element(By.XPATH, '//*[@headers="PC3_Po PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' +IDList[i][2] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][3] + '"]').text
                    num += 1
                    # 確認是否擷取到數據 沒有最多retry三次
                    if not date == 'null' and not period == 'null' and not temperature == 'null' and not PofP == 'null':
                        cwbinfo = {'district': '雲林縣崙背鄉', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
                        break
                cwbinfoList.append(cwbinfo)
            # 網頁擷取錯誤例外處理
            except:
                print('error occured')
                pass

        data = cwbinfoList
        print('--cralwer end--')
        return data

# 擷取交通部氣象局嘉義縣布袋鎮 1.地區 2.明天日期 3.時段 4.溫度 5.降雨機率
    def cwb_BudaiInfo(self, strDate=datetime.datetime.today().date()):
        cwbinfoList = []
        PC3_D = '1' if datetime.datetime.now().hour >= 22 else '2'
        IDList = [[PC3_D, '00', '00', '03'], [PC3_D, '03', '00', '03'], [PC3_D, '06', '06', '09'], [PC3_D, '09', '06', '09'], [PC3_D, '12', '12', '15'], [PC3_D, '15', '12', '15'], [PC3_D, '18', '18', '21'], [PC3_D, '21', '18', '21']]
        print('--cralwer start--')
        options = Options()
        options.add_argument('--headless')
        chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)
        for i in range(len(IDList)):
            # 明天日期
            date = 'null'
            # 時段
            period = 'null'
            # 溫度
            temperature = 'null'
            # 降雨機率
            PofP = 'null'
            # 擷取次數
            num = 0
            cwbinfo = {'district': '嘉義縣布袋鎮', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
            try:
                while num < 3:
                    print('try ' + str(num + 1))
                    driver.get("https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=1001003")
                    driver.implicitly_wait(10)
                    #time.sleep(1)
                    date = driver.find_element(By.ID, 'PC3_D' + IDList[i][0] + '').text.replace("\n", " ")
                    period = driver.find_element(By.XPATH, '//*[@id="PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span').text
                    temperature = driver.find_element(By.XPATH, '//*[@headers="PC3_T PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span[1]').text
                    PofP = driver.find_element(By.XPATH, '//*[@headers="PC3_Po PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' +IDList[i][2] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][3] + '"]').text
                    num += 1
                    # 確認是否擷取到數據 沒有最多retry三次
                    if not date == 'null' and not period == 'null' and not temperature == 'null' and not PofP == 'null':
                        cwbinfo = {'district': '嘉義縣布袋鎮', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
                        break
                cwbinfoList.append(cwbinfo)
            # 網頁擷取錯誤例外處理
            except:
                print('error occured')
                pass

        data = cwbinfoList
        print('--cralwer end--')
        return data

# 擷取交通部氣象局臺南市七股區 1.地區 2.明天日期 3.時段 4.溫度 5.降雨機率
    def cwb_QiguInfo(self, strDate=datetime.datetime.today().date()):
        cwbinfoList = []
        PC3_D = '1' if datetime.datetime.now().hour >= 22 else '2'
        IDList = [[PC3_D, '00', '00', '03'], [PC3_D, '03', '00', '03'], [PC3_D, '06', '06', '09'], [PC3_D, '09', '06', '09'], [PC3_D, '12', '12', '15'], [PC3_D, '15', '12', '15'], [PC3_D, '18', '18', '21'], [PC3_D, '21', '18', '21']]
        print('--cralwer start--')
        options = Options()
        options.add_argument('--headless')
        chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)
        for i in range(len(IDList)):
            # 明天日期
            date = 'null'
            # 時段
            period = 'null'
            # 溫度
            temperature = 'null'
            # 降雨機率
            PofP = 'null'
            # 擷取次數
            num = 0
            cwbinfo = {'district': '臺南市七股區', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
            try:
                while num < 3:
                    print('try ' + str(num + 1))
                    driver.get("https://www.cwb.gov.tw/V8/C/W/Town/Town.html?TID=6701500")
                    driver.implicitly_wait(10)
                    #time.sleep(1)
                    date = driver.find_element(By.ID, 'PC3_D' + IDList[i][0] + '').text.replace("\n", " ")
                    period = driver.find_element(By.XPATH, '//*[@id="PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span').text
                    temperature = driver.find_element(By.XPATH, '//*[@headers="PC3_T PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][1] + '"]/span[1]').text
                    PofP = driver.find_element(By.XPATH, '//*[@headers="PC3_Po PC3_D' + IDList[i][0] + ' PC3_D' + IDList[i][0] + 'H' +IDList[i][2] + ' PC3_D' + IDList[i][0] + 'H' + IDList[i][3] + '"]').text
                    num += 1
                    # 確認是否擷取到數據 沒有最多retry三次
                    if not date == 'null' and not period == 'null' and not temperature == 'null' and not PofP == 'null':
                        cwbinfo = {'district': '臺南市七股區', 'date': date, 'period': period, 'temperature': temperature, 'PofP': PofP}
                        break
                cwbinfoList.append(cwbinfo)
            # 網頁擷取錯誤例外處理
            except:
                print('error occured')
                pass

        data = cwbinfoList
        print('--cralwer end--')
        return data

    # 擷取今日電力供需資訊函數 1.備轉容量率
    def electricity_today(self, strDate=datetime.datetime.today().date()):
        # 備轉容量率
        reserve = 'null'
        # 擷取次數
        num = 0
        try:
            print('--cralwer start--')
            while num < 3:
                print('try ' + str(num + 1))
                options = Options()
                options.add_argument('--headless')
                chrome_service = fs.Service(executable_path=ChromeDriverManager().install())
                driver = webdriver.Chrome(service=chrome_service, options=options)
                driver.get("https://www.taipower.com.tw/d006/loadGraph/loadGraph/load_reserve_.html")
                driver.implicitly_wait(10)
                #time.sleep(1)
                reserve = driver.find_element(By.XPATH, '//*[@id="reserve"]/span').text
                num += 1
                # 確認是否擷取到數據 沒有最多retry三次
                if not reserve == 'null':
                    break
        # 網頁擷取錯誤例外處理
        except:
            print('error occured')
            pass

        date = {'reserve': reserve}
        print('--cralwer end--')
        return date