# raiex

Raif accounts data exporter

Collects transactions from Raif accounts and exports them to Google Sheets.

## Installation

1. Create GAS project.
   1.1. Create a table with a sheet named `Transactions`.
   1.2. Create an attached GAS project using scripts from the `gas_client` folder.
   1.3. Populate the 'INTEGRITY_HASH_SALT' property in the GAS project with a random string.
   1.4. Deploy the GAS project as a web app and set access to "Anyone, even anonymous".
   1.5. Copy the web app URL.
   1.6. Fill the first row of the `Transactions` sheet with the following headers:

    ```text
    CurrencyCodeNumber;CurrencyCode;ValueDate;ProcessedDate;ChequeCardNumber;TransactionBeneficiary;Reference;DebitAmount;CreditAmount;AmountTotal;Note;TransactionID;TransactionType;Description;BeneficiaryAccount
    ```

2. Copy `.secrets.example` to `.secrets` and fill in the required fields.  
   Use the web app URL from step 1.5 as `GAS_WEB_APP_URL`
   and `INTEGRITY_HASH_SALT` from step 1.3 as `INTEGRITY_HASH_SALT`.
3. Install dependencies
4. Run `main.py`
