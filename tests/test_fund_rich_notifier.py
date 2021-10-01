from typing import Dict, Type

from src.fund_rich_notifier import check, parse_result, Fund_Rich_Notifier, transition_to_html, check_env_var_exist
from collections import namedtuple
from pytest_mock import mocker
import pytest
import os

@pytest.fixture()
def mock_response() -> Dict:
    mock_response = {
        'Data': {
            'TWD_BAL_COST_AMT': 104220.0,
            'TWD_MARKET_VALUE_AMT': 103834.0,
            'TWD_ROI_RATE_DIV_AMT': 0.2897,
            'TWD_ROI_RATE_AMT': -0.3703,
            'TWD_GL_AMT_DIV_AMT': 302.0,
            'TWD_GL_AMT_AMT': -386.0,
            'PROF_TYPE_CHART': [
                {'PROF_TYPE': '01',
                'PROF_TYPE_NM': '股票型',
                'MARKET_VALUE': 77397.0,
                'PERCENTAGE': 74.54},
                {'PROF_TYPE': '02',
                'PROF_TYPE_NM': '債券型',
                'MARKET_VALUE': 26437.0,
                'PERCENTAGE': 25.46}
            ],
            'FUND_DROPDOWN_LISTS': [
                {'FUND_ID': '005007', 
                'FUND_SH_NM': '摩根東協基金-摩根東協(美元)(累計) '},
                {'FUND_ID': '029066', 'FUND_SH_NM': '聯博-全球高收益債券基金AA(穩定月配)級別美元'},
                {'FUND_ID': '042104', 'FUND_SH_NM': '貝萊德世界科技基金 A2 美元'},
                {'FUND_ID': '042131', 'FUND_SH_NM': '貝萊德世界健康科學基金 A2 美元'}],
            'CRNCY_CD_DROPDOWN_LISTS': [
                {'CRNCY_CD': 'TWD', 'CRNCY_CD_NM': '台幣'}],
            'TRADE_LISTS': [
                {
                    'FH_CD': '005',
                    'FUND_ID': '005007',
                    'CRNCY_CD': 'TWD',
                    'FUND_CURRENCY': 'USD',
                    'NAV_B': 148.01,
                    'NAV_DATE': '2021-09-28T00:00:00',
                    'EX_RATE': 27.8025,
                    'AVG_COST': 144.195,
                    'BAL_UNIT': 1.733,
                    'R_UNIT': 1.733,
                    'ETD_BAL_COST': 7000.0,
                    'FUND_CURRENCY_BAL_COST': 249.89,
                    'TWD_BAL_COST': 7000.0,
                    'MARKET_VALUE': 7131.0,
                    'DIV_CASH': 0.0,
                    'ROI_RATE_DIV': 1.8714,
                    'ROI_RATE': 1.8714,
                    'GL_AMT': 131.0,
                    'IS_CLOING': False,
                    'FUND_SH_NM': '摩根東協基金-摩根東協(美元)(累計) ',
                    'FUND_RISK_MSG': '摩根東協基金',
                    'DIVIDEND_TYPE': 'N',
                    'PROF_TYPE': '01',
                    'PROF_TYPE_NM': '股票型',
                    'EC_REDEM_YN': True,
                    'EC_SWITCH_YN': True,
                    'UNIT_DEC': 3,
                    'CRNCY_CD_NAV_DEC': 0,
                    'FUND_CURRENCY_NAV_DEC': 2,
                    'AVG_NAV_DEC': 4,
                    'FUND_CURRENCY_NM': '美金',
                    'CRNCY_CD_NM': '台幣',
                    'RSP_AVG_COST': 143.7706,
                    'RSP_BAL_UNIT': 8.476,
                    'RSP_R_UNIT': 8.476,
                    'RSP_ETD_BAL_COST': 34220.0,
                    'RSP_FUND_CURRENCY_BAL_COST': 1218.6,
                    'RSP_TWD_BAL_COST': 34220.0,
                    'RSP_MARKET_VALUE': 34879.0,
                    'RSP_DIV_CASH': 0.0,
                    'RSP_ROI_RATE_DIV': 1.9257,
                    'RSP_ROI_RATE': 1.9257,
                    'RSP_GL_AMT': 659.0,
                    'IS_ALLOT': 'Y',
                    'IS_RSP': 'Y',
                    'IS_ALERT_SET': 'Y',
                    'ALERT_TYPE': '1',
                    'ALERT_HIGH_SETTING': 20.0,
                    'ALERT_LOW_SETTING': None,
                    'ALERT_TARGET': 'Y',
                    'EC_REDEM_DESC': None,
                    'EC_SWITCH_DESC': None,
                    'ALERT_EMAIL_YN': 'N',
                    'AVG_NAV_CHART': 143.8427,
                    'EC_SWITCH_MSG_TYPE': ''}], 
            'FUND_ID_CHART': [
                {'FUND_ID': '005007',
                'FUND_SH_NM': '摩根東協基金-摩根東協(美元)(累計) ',
                'MARKET_VALUE': 42010.0,
                'PERCENTAGE': 40.46}]
            },
        'Message': None,
        'IsSuccessful': True,
        'ResultCode': '0',
        'AP': '172.18.25.99',
        'WarningMessage': None}
    return mock_response

@pytest.fixture()
def mock_personal_data():
    Personal_data = namedtuple("Personal_data", ["id", "password"])
    # Testing Case
    TESTING_ID = "A123456789"
    TESTING_PASSWORD = "password"
    mock_personal_data = Personal_data(TESTING_ID, TESTING_PASSWORD)
    return mock_personal_data

@pytest.fixture()
def mock_fund_rich_notifier(mock_personal_data):
    fr = Fund_Rich_Notifier(mock_personal_data.id, mock_personal_data.password)
    return fr

class Test_Fund_rich_notifier():

    def test_init(self, mock_personal_data):
        # Fixed attribute
        LOGIN_URL = "https://www.fundrich.com.tw/FundWeb/WS/loginweb.aspx"
        GET_TRADE_URL = "https://www.fundrich.com.tw/ECGWToApi2/api2/GetTradeInfo"

        EXPECTED_ID = "A123456789"
        EXPECTED_PASSWORD = "password"

        fr = Fund_Rich_Notifier(mock_personal_data.id, mock_personal_data.password)
        
        assert fr.LOGIN_URL == LOGIN_URL
        assert fr.GET_TRADE_URL == GET_TRADE_URL

        assert fr.Id == EXPECTED_ID
        assert fr.Password == EXPECTED_PASSWORD
    
    def test_send_request(self, mock_fund_rich_notifier, mocker):
        # XXX: 不確定這樣的做法是不是正確的，單純先把request處理的部份 mock 起來
        mocker_method = mocker.patch.object(
            mock_fund_rich_notifier,
            "send_request"
        )
        mock_fund_rich_notifier.send_request()
        assert mocker_method.called

def test_transition_to_html():
    with pytest.raises(TypeError):
        transition_to_html("s")
        transition_to_html(0.02)
        transition_to_html("super")

def test_parse_result(mock_response):
    result = parse_result(mock_response)
    assert result[0]['name'] == '摩根東協基金-摩根東協(美元)(累計) '
    assert result[0]['bal_cost'] == 41220.0
    assert result[0]['amt'] == 790.0
    assert result[0]['rate'] == 1.92

def test_check_env_var_exist():
    TESTING_KEY = "test"
    with pytest.raises(KeyError):
        check_env_var_exist(TESTING_KEY)
    
    os.environ[TESTING_KEY] = "test_value"
    check_env_var_exist(TESTING_KEY)

def test_check():
    ESSENTIAL_VARS = ['user_id', 'password', 'mailgun_domain', 'mailgun_token', 'recipient']

    for var in ESSENTIAL_VARS:
        with pytest.raises(KeyError): # There is no env var, it should throw error
            check_env_var_exist(var)
        os.environ[var] = 'test_value'
    
    assert check()