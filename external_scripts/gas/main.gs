function test() {
  doPost({
    parameter: { hash: 'put' },
    postData: {
      contents: '{"transactions": [ put ]}',
    }
  })
}

function doPost(e) {
  const rawJson = e.postData.contents;
  const hash = e.parameter.hash;

  verifyHash(rawJson, hash);

  putData(rawJson);
}

function verifyHash(rawJson, receivedHash) {
  const salt = PropertiesService.getScriptProperties().getProperty('INTEGRITY_HASH_SALT');

  const bytes = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    salt + rawJson,
    Utilities.Charset.UTF_8
  );

  const calculatedHash = Utilities.base64Encode(bytes);

  if (calculatedHash !== receivedHash) {
    throw Error("Integrity check failed");
  }
}

function putData(rawJson) {
  const data = JSON.parse(rawJson);

  putTransactions(data.transactions);
}

function putTransactions(transactions) {
  const KEY = 'TransactionID';

  ensure(transactions.every(x => !!x[KEY]), "Transaction id is empty");

  const isSorted = transactions
    .every((_, i, lst) => i < 1 || convertDateToIso(lst[i].ValueDate) <= convertDateToIso(lst[i - 1].ValueDate));
  ensure(isSorted);

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Transactions');
  const columns = sheet.getRange('1:1').getValues()[0].filter(x => !!x);

  const transactionIdColumnIndex = columns.indexOf(KEY) + 1;
  ensure(transactionIdColumnIndex >= 0, `Column ${KEY} not found`);

  const existingTransactionIds = sheet
    .getRange(1, transactionIdColumnIndex, sheet.getMaxRows())
    .getValues()
    .map(x => x[0]);
  const newValues = transactions.filter(newTr => !existingTransactionIds.includes(newTr[KEY]));
  if (!newValues.length) {
    console.log('There are no new transactions');
    return;
  }

  console.log('New transactions:', newValues.length);
  const table = newValues.map(val => obj2row(columns, val));
  sheet.insertRowsAfter(1, table.length);
  sheet.getRange(2, 1, table.length, table[0].length).setValues(table);
}