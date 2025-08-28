import datetime
import json
from typing import Any, Dict

import requests

from src.raif_client.grid_parsers import parse_grid_data
from src.raif_client.helpers import argon2_hash_hex, strip_bom

BASE_URL = "https://rol.raiffeisenbank.rs/Retail/Protected/Services/"

ENDPOINTS = {
    "SystemParameters": "RetailLoginService.svc/GetSystemParametersCached",
    "SaltedPassword": "RetailLoginService.svc/SaltedPassword",
    "LoginFont": "RetailLoginService.svc/LoginFont",

    "GetAllAccountBalance": "DataService.svc/GetAllAccountBalance",
    "GetTransactionalAccountTurnover": "DataService.svc/GetTransactionalAccountTurnover",
}

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
}


def create_session_with_cookies() -> requests.Session:
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    return s


def get_system_parameters_cached(session: requests.Session) -> Dict[str, Any]:
    return _invoke(session, "SystemParameters", {})


def login(session: requests.Session, username: str, password: str) -> None:
    """
    Perform Argon2 salted login.
    Mutates the passed session to carry authentication state.
    Raises RuntimeError on failure.
    """
    session.headers.update(DEFAULT_HEADERS)

    # Step 1: Check salted support
    result = _invoke(session, "SaltedPassword", {"userName": username})
    if type(result) is not bool or not result:
        raise RuntimeError("Only salted login is supported")

    # Step 2: Perform Argon2 salted login
    password_hex = argon2_hash_hex(password, username)
    login_result = _invoke(
        session,
        "LoginFont",
        {"username": username, "password": password_hex, "sessionID": 1},
    )
    _handle_login_response(session, login_result, "UsernamePassword")


def get_all_account_balance(session: requests.Session) -> list[dict[str, str]]:
    response = _invoke(
        session,
        "GetAllAccountBalance",
        {"gridName": "RetailAccountBalancePreviewFlat-L"},
    )
    return parse_grid_data(response, "RetailAccountBalancePreviewFlat-L")


def get_transactional_account_turnover(session: requests.Session, account: dict[str, str]) -> list[dict[str, str]]:
    today = datetime.date.today()
    one_year_before = today - datetime.timedelta(days=365)
    response = _invoke(
        session,
        "GetTransactionalAccountTurnover",
        {
            "gridName": "RetailAccountTurnoverTransactionPreviewMasterDetail-S",
            "accountNumber": account["AccountNumber"],
            "productCoreID": account["ProductCodeCore"],
            "filterParam": {
                "CurrencyCodeNumeric": account["CurrencyCodeNumber"],
                "FromDate": one_year_before.strftime("%d.%m.%Y"),
                "ToDate": today.strftime("%d.%m.%Y"),
                "ItemType": "",
                "ItemCount": "",
                "FromAmount": "",
                "ToAmount": "",
                "PaymentPurpose": ""
            },
        },
    )
    return parse_grid_data(response[0][1:][0], "RetailAccountTurnoverTransactionPreviewMasterDetail-S")


def _invoke(session: requests.Session, method: str, data: Dict[str, Any]) -> Any:
    if method not in ENDPOINTS:
        raise ValueError(f"Unknown method: {method}")
    url = BASE_URL.rstrip("/") + '/' + ENDPOINTS[method]
    resp = session.post(url, data=json.dumps(data))
    resp.raise_for_status()
    return json.loads(strip_bom(resp.text))


def _handle_login_response(session: requests.Session, user: Dict[str, Any], login_type: str) -> None:
    if user.get("PinMustBeChanged"):
        raise RuntimeError("Account requires PIN change")

    if user.get("LoginError"):
        le = user["LoginError"]
        if le.get("WrongPassword"):
            raise RuntimeError("Wrong password")
        if le.get("UserBlocked"):
            raise RuntimeError("User blocked")
        if le.get("UserTempBlocked"):
            mins = user.get("TempBlockPeriodInMinutes")
            raise RuntimeError(f"User temporarily blocked ({mins} min)")
        raise RuntimeError("Login error")

    if user.get("ValidationErrors"):
        raise RuntimeError(f"Validation errors: {user['ValidationErrors']}")

    # Success: set cookies and headers for session continuity
    session.cookies.set("loginType", login_type)
    if user.get("RequestToken"):
        session.headers["X-Request-Token"] = user["RequestToken"]
