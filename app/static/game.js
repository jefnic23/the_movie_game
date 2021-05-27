var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

function joinRoom(room) {
    socket.emit('join', {'room': room, 'username': username});
}

let room = 'Lounge';
joinRoom('Lounge');

socket.on('joined', data => {
    var div = document.createElement('div');
    var img = document.createElement('img');
    var player = document.createElement('h2');
    div.setAttribute("class", "card");
    img.setAttribute("src", avatar);
    img.setAttribute("class", "card-icon");
    player.innerHTML = data.username;
    div.append(img);
    div.append(player);
    document.querySelector('#avatar-container').append(div);
    if (data.players.length === 2 && data.current_player === username) {
        document.getElementById("searchbar").disabled = false;
        document.getElementById("searchbtn").disabled = false;
    }
});

var form = document.getElementById("search_form");
function handleForm(event) {
    event.preventDefault();
}
form.addEventListener("submit", handleForm);

const genres = [16, 99, 10402, 10770];
var results_container = document.getElementById("results-container");
var results = document.createElement("ul");
results.setAttribute("id", "results");

function successCB(data) {
    data = JSON.parse(data);
    for (var i = 0; i < data.results.length; i++) {
        let d = {}
        if (data.results[i].media_type === "movie" && data.results[i].genre_ids.length && !data.results[i].genre_ids.some(r => genres.includes(r)) && !data.results[i].video) {
            var name = data.results[i].title;
            var id = data.results[i].id;
            var media_type = data.results[i].media_type;
            var year = new Date(data.results[i].release_date).getFullYear();
            var popularity = data.results[i].popularity;
            d.name = name;
            d.id = id;
            d.media_type = media_type;
            d.year = year;
            d.popularity = popularity;
            search.push(d);

            var li = document.createElement('li');
            var a = document.createElement('a');
            a.innerHTML = `${data.results[i].title} (${year})`;
            a.setAttribute('value', id);
            a.setAttribute('href', "#");
            a.setAttribute('onClick', 'selectResult(this)');
            li.appendChild(a);
            results.appendChild(li);
        } else if (data.results[i].media_type === "person" && data.results[i].known_for_department === "Acting") {
            var name = data.results[i].name;
            var id = data.results[i].id;
            var media_type = data.results[i].media_type;
            var popularity = data.results[i].popularity;
            d.name = name;
            d.id = id;
            d.media_type = media_type;
            d.popularity = popularity;
            search.push(d);

            var li = document.createElement('li');
            var a = document.createElement('a')
            a.innerHTML = name;
            a.setAttribute('value', id);
            a.setAttribute('href', "#");
            a.setAttribute('onClick', 'selectResult(this)');
            li.appendChild(a);
            results.appendChild(li);
        }
    }
    results_container.appendChild(results)
}
        
function errorCB(data) {
    console.log("Error callback: " + data);
}

var search = []
function getQuery() {
    results.innerHTML = '';
    var q = document.getElementById("searchbar").value;
    theMovieDb.search.getMulti({'query': q}, successCB, errorCB);
}

var game_container = document.getElementById("game-container");
var game = document.createElement("ul");
game.setAttribute("id", "game");

function selectResult(item) {
    var id = item.getAttribute('value');
    socket.emit('search', {'guess': search[search.findIndex(x => x.id == id)], 'username': username, 'room': room});
}

function enableSearch(current, username) {
    if (current === username) {
        document.getElementById("searchbar").disabled = false;
        document.getElementById("searchbtn").disabled = false;
    } else {
        document.getElementById("searchbar").disabled = true;
        document.getElementById("searchbtn").disabled = true;
    }
}

function enableChallenge(current, username, round_index) {
    if (round_index > 1 && current === username) {
        document.getElementById('challengebtn').hidden = false;
        document.getElementById('challengebtn').disabled = false;
    } else {
        document.getElementById('challengebtn').hidden = true;
        document.getElementById('challengebtn').disabled = true;
    }
}

function veto() {
    socket.emit("veto", {'room': room});
}

function challenge() {
    socket.emit("challenge", {'room': room});
}

const TIME_LIMIT = 20;
let timePassed = 0;
let timeLeft = TIME_LIMIT;
let timerInterval = null; 

function timesUp() {
    clearInterval(timerInterval);
    timePassed = 0;
    timeLeft = TIME_LIMIT;
    document.getElementById("timer").innerHTML = timeLeft;
}

function timer() {
    timerInterval = setInterval(() => {
        timePassed += 1;
        timeLeft = TIME_LIMIT - timePassed;
        document.getElementById("timer").innerHTML = timeLeft;
        if (timeLeft === 0) {
            timesUp();
        }
    }, 1000);
}

socket.on("vetoed", data => {
    timesUp();
    game.innerHTML = '';
    results.innerHTML = '';
    document.getElementById('vetobtn').hidden = true;
    document.getElementById('vetobtn').disabled = true;
    enableSearch(data.current_player, username);
});

socket.on("challenged", data => {
    timesUp();
    enableSearch(data.current_player, username);
    document.getElementById('challengebtn').hidden = true;
    document.getElementById('challengebtn').disabled = true;
    timer();
});

socket.on('answer', data => {
    // console.log(`current player: ${data.current_player}`);
    timesUp();
    if (data.round_index === 1 && data.current_player === username) {
        document.getElementById('vetobtn').hidden = false;
        document.getElementById('vetobtn').disabled = false;
    } else {
        document.getElementById('vetobtn').hidden = true;
        document.getElementById('vetobtn').disabled = true;
    }

    if (data.round_over) {
        enableSearch(data.current_player, username);  
        game.innerHTML = '';
        results.innerHTML = '';
        alert(`sorry, ${data.player} rollcall: ${data.score}`);
        socket.emit('restart');
    } else {
        enableSearch(data.current_player, username);
        enableChallenge(data.current_player, username, data.round_index);
        results.innerHTML = '';
        var li = document.createElement("li");
        li.innerHTML = data.answer.name;
        game.appendChild(li);
        game_container.appendChild(game);
        if (data.round_index - 1 !== 0) {
            alert('correct!');
        }
        timer();
    }
});