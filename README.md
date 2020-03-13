# fund_notification
這個Script是用來替代[基富通](www.fundrich.com.tw)先前所推出的「基金淨值通知」Line bot。
會自動登入後取得所需的基金資訊，將其寄送至使用者的信箱。
## How to use
### Package
``` pip install -r requirements.txt ```
### 撰寫config.ini
需要將以下資訊寫到```config.ini```檔案中：
+ 基富通：
    - 基富通帳號
    - 基富通密碼
+ SMTP： (寄送給你資訊的信箱)
    - 信箱帳號
    - 信箱密碼

格式請按照以下: 
```python
[password]
user_id = <Your fundrich user_id>
password = <Your fundrich passwor>
stp_user = <Your stp mail user>
stp_password = <Your stp mail password>
```

## 更改main.py中的receiver
將`main.py`中的`receiver`變數改為自己的email欄位。

## 執行main.py
`python main.py`
