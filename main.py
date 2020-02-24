#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email.mime.text import MIMEText
from email.header import Header

from selenium.webdriver import Safari
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import configparser

conf = configparser.ConfigParser()
conf.read("config.ini", encoding='utf-8')
conf = dict(conf.items('password'))

def format_to_value(html):
    """
    將selenium所取得的html code parse為文字資訊。
    html: html code.
    return : {"title1":"value1", "title2":"value2"}
    """
    soup = BeautifulSoup(html)
    title = [x.text for x in soup.find_all("div", class_="text-1")]
    value = [x.text for x in soup.find_all("div", class_="txt-card-value")]
    return dict(zip(title, value))


with Safari() as driver:
    driver.set_window_size(800,600)
    driver.get("https://www.fundrich.com.tw/ECWeb2/#/quotaCompo")
    time.sleep(3)
    # 輸入帳號密碼
    elem_user = driver.find_element_by_css_selector("input[type=text]")
    elem_user.send_keys(conf["user_id"])
    elem_password = driver.find_element_by_css_selector("input[type=password]")
    elem_password.send_keys(conf["password"])
    elem_password.send_keys(Keys.RETURN)
    time.sleep(3)
    driver.get("https://www.fundrich.com.tw/ECWeb2/#/quotaCompo")
    time.sleep(3)
    # 開始Parse HTML.
    fund_name = [x.text for x in driver.find_elements_by_class_name("fundName")]

    elem_fund = driver.find_elements_by_class_name("fundInBox")
    original_html = [x.get_attribute("innerHTML") for x in elem_fund]
    # driver.close()

    """
    message = ""
    
    for idx, a_html in enumerate(original_html):
        if idx % 18 == 0:
            message += "基金名稱: {}\n\n".format(fund_name[int(idx/18)])
        parsed_value = format_to_value(a_html)
        for a_key in parsed_value.keys():
            if a_key != "":
                message += "{} : {}\n".format(a_key, parsed_value[a_key])
    print(message)
    """
    message = "<html><body>"
    for idx, a_html in enumerate(original_html):
        if idx % 9 == 0:
            message += "<br><b>基金名稱: {}</b><br>".format(fund_name[int(idx/18)])
        parsed_value = format_to_value(a_html)
        for a_key in parsed_value.keys():
            if a_key != "":
                if a_key == "參考損益": # 加入顏色變化
                        if "-" in parsed_value[a_key]:
                            message += "{}: <font color='green'>{}</font><br>".format(a_key, parsed_value[a_key])
                        else:
                            message += "{}: <font color='red'>{}</font><br>".format(a_key, parsed_value[a_key])
                else:
                    message += "{}: {}<br>".format(a_key, parsed_value[a_key])
    message += "</body></body>"
    # 第三方 SMTP 服务
    mail_host= "smtp.gmail.com"  
    mail_user= conf["stp_user"]   
    mail_pass= conf["stp_password"]
    
    
    sender = 'from@runoob.com'
    receivers = ['allen6997535@gmail.com']
    
    message = MIMEText(message, 'html', 'utf-8')
    message['From'] = Header("小基富通機器人", 'utf-8')
    message['To'] =  Header("Allen_Wu", 'utf-8')
    
    subject = '本日基富通基金資訊'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP(mail_host, 25) 
        # smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        smtpObj.ehlo()  # 向Gamil傳送SMTP 'ehlo' 命令
        smtpObj.starttls()
        smtpObj.login(mail_user,mail_pass)  
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("發送成功")
    except smtplib.SMTPException:
        print("發送失敗")
        print()