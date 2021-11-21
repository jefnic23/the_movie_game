function populateTable(data) {
    var table = document.querySelector('#lobby');
    for (let i=0; i < data.rows.length; i++) {
        var roomname = data.rows[i].roomname;
        var password = data.rows[i].password;
        var players = data.rows[i].count;
        var status = data.rows[i].status;
        var items = ['', roomname, players, status]
        for (let j=0; j < items.length; j++) {
            var td = document.createElement('td');
            td.innerHTML = items[j];
            row.appendChild(td);
        }
        table.appendChild(row); 
    }
}

populateTable(data);