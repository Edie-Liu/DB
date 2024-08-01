import calendar
import pymssql
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# 根據自己的Database來填入資訊
db_settings = {
    "host": "127.0.0.1",
    "user": "",
    "password": "",
    "database": "",
    "charset": "utf8"
}

#特殊節日
holiday_dir = {}

# 爬蟲
def crawler():

    # 這邊是用Edge作為範例，可以依照你使用瀏覽器的習慣做修改
    options = Options()
    
    options.add_argument("--headless")  # 執行時不顯示瀏覽器
    options.add_argument("--disable-notifications")  # 禁止瀏覽器的彈跳通知
    #options.add_experimental_option("detach", True)  # 爬蟲完不關閉瀏覽器
    driver = webdriver.Edge(options=options)

    driver.get("https://www.wantgoo.com/global/holiday/twse")
    try:
        # 等元件跑完再接下來的動作，避免讀取不到內容
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//tbody[@id='holidays']//tr//th")))        
        holiday_list = driver.find_elements(By.XPATH,"//tbody[@id='holidays']//tr")
        print(holiday_list)
        for holiday in holiday_list:
            WebDriverWait(holiday, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "th")))
            WebDriverWait(holiday, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))
            date_str = holiday.find_element(By.TAG_NAME, "th").text.split(" ")[0]
            explain = holiday.find_element(By.TAG_NAME, "td").text.replace("\"","")

            if date_str != '': 
                date_time_obj = datetime.strptime(date_str, '%Y/%m/%d').strftime('%Y%m%d')
                holiday_dir[date_time_obj] = explain
    except TimeoutException as e:
        print(e)    
    #edge.close()
        
    work_count = 0

    try:
        conn = pymssql.connect(**db_settings)
        command = "INSERT INTO [dbo].[calendar] (date, day_of_stock, other) VALUES (%s, %d, %s)"
        with conn.cursor() as cursor:
            for month in range(1,13):
                for date in range(1, calendar.monthrange(2024,month)[1]+1):
                    date_str = f"2024{month:02d}{date:02d}"
                    weekday = calendar.weekday(2024,month,date)  #取得星期，星期一為0
                    
                    if date_str in holiday_dir:  #若日期為特殊假日
                        cursor.execute(command, (date_str, -1, holiday_dir[date_str]))
                    elif weekday == 5 or weekday == 6:  #若日期為周末
                        cursor.execute(command, (date_str, -1, ""))
                    else:
                        work_count += 1
                        cursor.execute(command, (date_str, work_count, ""))
                    
                    conn.commit()
    except Exception as e:
        print(e)

    try:
        conn = pymssql.connect(**db_settings)
        command = "INSERT INTO [dbo].[year_calendar] (year, total_day) VALUES (%d, %d)"
        with conn.cursor() as cursor:
            cursor.execute(command, (2024, work_count))
            conn.commit()
    except Exception as e:
        print(e)

crawler()
