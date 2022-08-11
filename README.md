# fundrich_notifier 基富通價格通知

| Test Status | [![Coverage Status](https://coveralls.io/repos/github/MingLunWu/fund_notification/badge.svg?branch=master)](https://coveralls.io/github/MingLunWu/fund_notification?branch=master) |
|:---:|:---:|
| Release | ![Release Coverage](https://img.shields.io/github/v/release/MingLunWu/fundrich_notifier?style=flat-square) |


`fundrich_notifier` 是針對[基富通](https://www.fundrich.com.tw) 使用者所開發的小工具。

每日將使用者所購買的基金資訊以電子郵件寄送至使用者信箱，資訊包含: 

+ 基金名稱
+ 庫存成本
+ 獲利金額
+ 獲利率

![demo image](https://github.com/MingLunWu/fundrich_notifier/blob/master/image/example.png?raw=true)

# How to Use

## 取得 Mailgun 相關資訊

以 Python 使用 SMTP 寄送信件會被 Google 判定為低安全性使用行為，因此我們需要透過 [Mailgun](https://www.mailgun.com) 這個中繼服務來協助我們寄送信件。

使用前請先至 [Mailgun - Get Started](https://signup.mailgun.com/new/signup)取得下列資訊: 

+ Mailgun Domain
+ Mailgun Token

## 建立 Github Secret

在 Github Secret 建立下列資訊:

| Secret 名稱 | 欄位放置的值 |
|:----------:|:----------:|
| USER_ID | 基富通帳號(身分證字號) |
| PASSWORD | 基富通密碼 |
| MAILGUN_DOMAIN | `Mailgun`提供的Domain |
| MAILGUN_TOKEN | `Mailgun`提供的Token |
| RECIPIENT | 收件者信箱 |

## 執行

當前是透過 `Github Action` 設定排程執行，由於基金淨值每天只更新一次，目前設定為每天早上9:00自動將帳戶內「所有購買的基金資訊」寄送至信箱中。

執行時 `Github Action` 將會自動讀取專案的 `Github Secret`，透過爬蟲取得資訊後，以 `Mailgun`服務寄送至指定信箱。
