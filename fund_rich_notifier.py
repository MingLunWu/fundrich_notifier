# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import json
import configparser
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import collections

class Fund_Rich_Notifier():
	
	def __init__(self, user_id, password, mail_user, mail_password):
		self.Id = user_id
		self.Password = password
		self.s = None # Request Session

		self.mail_user = mail_user
		self.mail_password = mail_password

		self.LOGIN_URL = "https://www.fundrich.com.tw/FundWeb/WS/loginweb.aspx"
		self.GET_TRADE_URL = "https://www.fundrich.com.tw/ECGWToApi2/api2/GetTradeInfo"
	
	def send_request(self):
		"""
		Log in with Id and Password. Then use token to get transaction data.
		:return: Transaction object. (JSON) Need to be passed to `parse_result()`.
		"""
		assert self.Id is not None or self.Password is not None, "請輸入正確的帳號密碼！"
		
		with requests.Session() as self.s:
			# 進行登入
			header_login = {
				"Accept": "application/json, text/plain, */*",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
				"Connection": "keep-alive",
				"Content-Length": "44",
				"Content-Type": "application/json;charset=UTF-8",
				"Cookie": "_ga=GA1.3.867864378.1568100215; _hjid=0ae8bda1-c159-41ca-a336-cefc6c601d47; _fbp=fb.2.1582533885862.535817344; _gid=GA1.3.1909908572.1583321134; ASP.NET_SessionId=xdny1farozoebcqenfaanmwx; _gat=1; _gat_gtag_UA_75421763_1=1",
				"Host": "www.fundrich.com.tw",
				"Origin": "https://www.fundrich.com.tw",
				"Referer": "https://www.fundrich.com.tw/login.html?redirect=https%3A%2F%2Fwww.fundrich.com.tw%2F",
				"Sec-Fetch-Dest": "empty",
				"Sec-Fetch-Mode": "cors",
				"Sec-Fetch-Site": "same-origin",
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
			}
			payload_data = {
				"Id": self.Id,
				"Password": self.Password
			}
			
			#進行登入，成功後會回傳基本資料及Token.
			res_login = self.s.post(self.LOGIN_URL, headers = header_login, json=payload_data)
			
			assert res_login.status_code == 200, "登入失敗！帳號密碼可能輸入錯誤！請重新確認！"

			# 稍後會使用到res中的"Token"欄位。
			res_login = json.loads(res_login.text)

			header_check ={
				"cept": "application/json, text/plain, */*",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
				"Connection": "keep-alive",
				"Content-Length": "453",
				"Content-Type": "application/json;charset=UTF-8",
				"Cookie": "_ga=GA1.3.867864378.1568100215; _hjid=0ae8bda1-c159-41ca-a336-cefc6c601d47; _fbp=fb.2.1582533885862.535817344; _gid=GA1.3.1909908572.1583321134; ASP.NET_SessionId=xdny1farozoebcqenfaanmwx; _gat=1",
				"Host": "www.fundrich.com.tw",
				"Origin": "https://www.fundrich.com.tw",
				"Referer": "https://www.fundrich.com.tw/ECWeb2/",
				"Sec-Fetch-Dest": "empty",
				"Sec-Fetch-Mode": "cors",
				"Sec-Fetch-Site": "same-origin",
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
			}

			payload_data_check = {
				"VENDER_ID":"",
				"BF_NO":res_login["BFNo"],
				"BaseData":{
					"LangCode":"string",
					"UserCode":res_login["BFNo"],
					"HostName":"string",
					"WebIP":"string",
					"TokenId":res_login["Token"],
					"SessionId":"string",
					"LocalTime":"2019-01-24T01:44:45.197Z",
					"AccountId":"SW",
					"AccountKey":"70539165",
					"BrowserInfo":"string",
					"RequestValue":"string",
					"TraceId":"string"
				}
			}

			res_fund = self.s.post(self.GET_TRADE_URL,headers= header_check, json=payload_data_check)
			res_fund = json.loads(res_fund.text)
			return res_fund
	
	def parse_result(self, transaction_json):
		"""
		Parse useful information from original transaction json data.
		:return: List of fund informaiton.
		"""
		assert type(transaction_json) is dict
		res_detail = transaction_json["Data"]["TRADE_LISTS"]
		parsed_res = [{key: tmp[key] for key in tmp.keys() & {"FUND_SH_NM", "FUND_CURRENCY_NM","RSP_TWD_BAL_COST","RSP_MARKET_VALUE","RSP_GL_AMT","RSP_ROI_RATE_DIV","RSP_R_UNIT"}} for tmp in res_detail]
		return parsed_res
	
	def transition_to_html(self, json_data):
		html = """<table border="1px solid">"""
		translation_dict = collections.OrderedDict()
		translation_dict["FUND_SH_NM"]="基金名稱"
		translation_dict["RSP_R_UNIT"]="庫存單位數"
		translation_dict["FUND_CURRENCY_NM"]="計價幣別"
		translation_dict["RSP_TWD_BAL_COST"]="總庫存成本"
		translation_dict["RSP_MARKET_VALUE"]="總帳面市值"
		translation_dict["RSP_GL_AMT"]="參考損益"
		translation_dict["RSP_ROI_RATE_DIV"] = "交易報酬率"

		for a_fund in json_data:
			for a_key in translation_dict.keys():
				if a_key != "RSP_GL_AMT" and a_key != "RSP_ROI_RATE_DIV":
					html+="""<tr><td>{}</td><td>{}</td></tr>""".format(translation_dict[a_key], a_fund[a_key])
				else:
					if a_fund[a_key] < 0:
						html+="""<tr><td>{}</td><td><font color="green">{}</font></td></tr>""".format(translation_dict[a_key], a_fund[a_key])
					else:
						html+="""<tr><td>{}</td><td><font color="red">{}</font></td></tr>""".format(translation_dict[a_key], a_fund[a_key])
		
		html+="""</table>"""
		return html
	
	def send_mail(self, html, receivers=['allen6997535@gmail.com']):
		# 第三方 SMTP 服务
		mail_host="smtp.gmail.com"  #设置服务器
		
		sender = 'from@runoob.com'
		
		message = MIMEText(html, 'html', 'utf-8')
		message['From'] = Header("小基富通機器人", 'utf-8')
		message['To'] =  Header("Allen_Wu", 'utf-8')
		
		subject = '本日基富通基金資訊'
		message['Subject'] = Header(subject, 'utf-8')
		
		try:
			smtpObj = smtplib.SMTP(mail_host, 25) 
			# smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
			smtpObj.ehlo()  # 向Gamil傳送SMTP 'ehlo' 命令
			smtpObj.starttls()
			smtpObj.login(self.mail_user,self.mail_password)  
			smtpObj.sendmail(sender, receivers, message.as_string())
			print("郵件發送成功")
		except smtplib.SMTPException:
			print("Error: 無法發送郵件")
		

if __name__ == "__main__":
	conf = configparser.ConfigParser()
	conf.read("config.ini", encoding='utf-8')
	conf = dict(conf.items('password'))

	n = Fund_Rich_Notifier(conf["user_id"], conf["password"], conf["stp_user"], conf["stp_password"])	
	res = n.send_request()
	parsed_res = n.parse_result(res)
	html = n.transition_to_html(parsed_res)
	n.send_mail(html)
