import logging
from os import environ

from gas_client.client import send_data
from raif_client.client import create_session_with_cookies, login, \
    get_system_parameters_cached, get_all_account_balance, get_transactional_account_turnover


def _get_transactions() -> list[dict]:
    session = create_session_with_cookies()

    system_parameters = get_system_parameters_cached(session)
    logging.info("Fetched system parameters")

    login(session, environ["RAIF_USERNAME"], environ["RAIF_PASSWORD"])
    logging.info("Login successful")

    accounts = get_all_account_balance(session, system_parameters)
    logging.info(f"Found {len(accounts)} accounts")

    flat_transactions = []
    for account in accounts:
        turnover = get_transactional_account_turnover(session, system_parameters, account)
        logging.info(f"Account {account['AccountNumber']} has {len(turnover)} transactions")
        flat_transactions.extend(turnover)

    return flat_transactions


def main():
    try:
        transactions = _get_transactions()
        logging.info(f"Total transactions fetched: {len(transactions)}")

        upload_url = environ.get("GAS_UPLOAD_URL")
        salt = environ.get("INTEGRITY_HASH_SALT")
        send_data(upload_url, salt, transactions)
        logging.info("Transaction export completed successfully")
    except Exception as e:
        logging.exception("Error during transaction export", exc_info=e)
        return 1
    return 0


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv

    load_dotenv(".secrets")

    logging.basicConfig(level=logging.INFO)
    logging.info("Starting transaction export")

    sys.exit(main())
