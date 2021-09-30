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
	
	def __init__(self, user_id, password):
		self.Id = user_id
		self.Password = password
		self.s = None # Request Session

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

			######################################
			# 以下區塊需要放置屬於自己的payload_data #
			#####################################
			
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
		result = list()
		res_detail = transaction_json["Data"]["TRADE_LISTS"]
		for fund in res_detail:
			fund_name = fund["FUND_SH_NM"] # 基金名稱
			etd_bal_cost = fund["ETD_BAL_COST"] # 單筆申購本金
			rsp_etd_bal_cost = fund["RSP_ETD_BAL_COST"] # 定期定額本金
			gl_amt = fund["GL_AMT"] # 單筆申購參考損益
			rsp_gl_amt = fund["RSP_GL_AMT"] # 定期定額參考損益

			bal_cost = etd_bal_cost+rsp_etd_bal_cost # 總本金
			amt = gl_amt + rsp_gl_amt # 總損益
			rate = amt / bal_cost

			result.append({"name": fund_name, "bal_cost": bal_cost, "amt": amt, "rate":round(rate*100, 2)})

		return result
	
	def transition_to_html(self, json_data):
		html = """<table border="1px solid" style="text-align:center">"""
		translation_dict = collections.OrderedDict()
		translation_dict["name"]="基金名稱"
		translation_dict["bal_cost"]="總庫存成本"
		translation_dict["amt"]="總獲利"
		translation_dict["rate"]="總獲利率"
		

		for a_fund in json_data:
			for a_key in translation_dict.keys():
				if a_key != "rate" and a_key != "amt":
					html+="""<tr><td>{}</td><td>{}</td></tr>""".format(translation_dict[a_key], a_fund[a_key])
				elif a_key == "rate":
					if a_fund[a_key] < 0:
						html+="""<tr><td>{}</td><td><font color="green">{}%</font></td></tr>""".format(translation_dict[a_key], a_fund[a_key])
					else:
						html+="""<tr><td>{}</td><td><font color="red">{}%</font></td></tr>""".format(translation_dict[a_key], a_fund[a_key])
				else:
					if a_fund[a_key] < 0:
						html+="""<tr><td>{}</td><td><font color="green">{}</font></td></tr>""".format(translation_dict[a_key], a_fund[a_key])
					else:
						html+="""<tr><td>{}</td><td><font color="red">{}</font></td></tr>""".format(translation_dict[a_key], a_fund[a_key])
		html+="""</table>"""
		return html
	
		

if __name__ == "__main__":
	conf = configparser.ConfigParser()
	conf.read("/Users/minglunwu/Documents/fund_notification/config.ini", encoding='utf-8')
	conf = dict(conf.items('password'))

	receivers = [] #這邊填寫你自己的Email.

	n = Fund_Rich_Notifier(conf["user_id"], conf["password"])	
	res = n.send_request()
	parsed_res = n.parse_result(res)
	html = n.transition_to_html(parsed_res)
