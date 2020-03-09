import configparser
from fund_rich_notifier import Fund_Rich_Notifier

conf = configparser.ConfigParser()
conf.read("config.ini", encoding='utf-8')
conf = dict(conf.items('password'))

n = Fund_Rich_Notifier(conf["user_id"], conf["password"], conf["stp_user"], conf["stp_password"])	
res = n.send_request()
parsed_res = n.parse_result(res)
html = n.transition_to_html(parsed_res)
n.send_mail(html)