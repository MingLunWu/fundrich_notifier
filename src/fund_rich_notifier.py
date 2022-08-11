# -*- coding: UTF-8 -*-

from typing import Dict, List
import requests
import json
import collections
from datetime import date
import os

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

def parse_result(transaction_json: Dict) -> List:
	"""Parsed the required information from the response of Fundrich

	Args:
		transaction_json (Dict): The orignial response of Fundrich

	Returns:
		List: List of fund informaiton, each element is a dictionary, 
		containing the following fileds:
			+ name: The name of the fund
			+ bal_cost: Total principle (本金總額)
			+ amt: Total profit and loss (損益總額)
			+ rate: Rate of return (獲益率)

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
		
def transition_to_html(json_data) -> str:
	"""Convert the parsed result into html format

	Args:
		json_data (str): Fund information from parse_result()

	Returns:
		str: Data in html format
	"""	
	html = """<table border="1px solid" style="text-align:center">"""
	translation_dict = collections.OrderedDict()
	translation_dict["name"]="基金名稱"
	translation_dict["bal_cost"]="總庫存成本"
	translation_dict["amt"]="總獲利"
	translation_dict["rate"]="總獲利率"
	
	# xxx: 醜！需要被refactor
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

def send_mail_by_mailgun(html_data: str, mailgun_domain:str, mailgun_token:str, recipient: str):
	"""Send mail via Mailgun service

	Args:
		html_data (str): Html data generated by transition_to_html()
		mailgun_domain: Mailgun domain (Please refer to README.md)
		mailgun_token: Mailgun token (Please refer to README.md)
		recipient: The email address of recipient

	Returns:
		str: requests.resonse
	"""
	return requests.post(
		f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
		auth=("api", mailgun_token),
		data={"from": "基富通自動通知 <mailgun@{}>".format(mailgun_domain),
			"to": [recipient],
			"subject": "自動通知 - {} 基金資訊".format(date.today().strftime("%Y/%m/%d")),
			"html": html_data})

def check_env_var_exist(var_name: str) -> bool:
	"""Confirm that all required environment variables exist


	Args:
		var_name (str): The name of environment variable

	Raises:
		KeyError: If the environement variable is not exists, assert KeyError

	Returns:
		bool: True means the variables exist, otherwise it will be assert error
	"""
	if os.environ.get(var_name) is None:
		raise KeyError("Environment Variable: {} must be set!".format(var_name))
		
	return True

def check() -> bool:
	ESSENTIAL_VAR = ['user_id', 'password', 'mailgun_domain', 'mailgun_token', 'recipient']
	for var in ESSENTIAL_VAR:
		check_env_var_exist(var)
	return True

if __name__ == "__main__":
	
	if check():
		n = Fund_Rich_Notifier(os.environ["user_id"], os.environ["password"])	
		res = n.send_request()
		parsed_res = parse_result(res)
		html = transition_to_html(parsed_res)
		print(send_mail_by_mailgun(html, os.environ['mailgun_domain'], os.environ['mailgun_token'], os.environ['recipient']))
		
