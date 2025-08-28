function ensure(cond, message) {
  if (!cond)
    throw new Error(message ?? "Assertation error");
}

function obj2row(columns, obj) {
  return columns.map(col => obj[col]);
}

function convertDateToIso(date) {
  return date.split(' ')[0].split('.').reverse().join('-');
}
