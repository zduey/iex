var data = source.data;
var filetext = 'time,display_time,price\n';
for (i=0; i < data['time'].length; i++) {
    if (data['time'][i] === data['time'][i-1]) {
        continue;
    }
    
    var currRow = [data['time'][i].toString(),
                   data['display_time'][i].toString(),
                   data['price'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var filename = 'prices.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
}

else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}