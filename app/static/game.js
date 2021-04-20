var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

function joinRoom(room) {
    socket.emit('join', {'room': room, 'username': username});
}

let room = 'Lounge';
joinRoom(room);

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
})

var round = [];
var round_index = 0;
var start = '';

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
            var title = data.results[i].title;
            var id = data.results[i].id;
            var media_type = data.results[i].media_type;
            var year = new Date(data.results[i].release_date).getFullYear();
            var popularity = data.results[i].popularity;
            d.title = title;
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
            var actor = data.results[i].name;
            var id = data.results[i].id;
            var media_type = data.results[i].media_type;
            var popularity = data.results[i].popularity;
            d.actor = actor;
            d.id = id;
            d.media_type = media_type;
            d.popularity = popularity;
            search.push(d);

            var li = document.createElement('li');
            var a = document.createElement('a')
            a.innerHTML = actor;
            a.setAttribute('value', id);
            a.setAttribute('href', "#");
            a.setAttribute('onClick', 'selectResult(this)');
            li.appendChild(a);
            results.appendChild(li);
        }
    }
    results_container.appendChild(results)
};
        
function errorCB(data) {
    console.log("Error callback: " + data);
};

var search = []
function getQuery() {
    results.innerHTML = '';
    var q = document.getElementById("search").value;
    theMovieDb.search.getMulti({'query': q}, successCB, errorCB);
};

var game_container = document.getElementById("game-container");
var game = document.createElement("ul");
game.setAttribute("id", "game");

function checkCast(cast, actor) {
    if (cast.includes(actor)) {
        return true;
    } else {
        return false;
    }
};

function checkFilms(films, actor) {
    if (films.includes(actor)) {
        return true;
    } else {
        return false;
    }
};

function getMovie(data) {
    data = JSON.parse(data);
    cast = [];
    for (var i = 0; i < data.cast.length; i++) {
        cast.push(data.cast[i].name);
    } 
    if (checkCast(cast, round[round_index-2])) {
        alert('correct!');
    } else {
        alert('sorry');
        round_index = 0;
        game.innerHTML = '';
    }
};

function getStarring(data) {
    data = JSON.parse(data);
    films = [];
    for (var i = 0; i < data.cast.length; i++) {
        films.push(data.cast[i].title);
    }
    if (checkFilms(films, round[round_index-2])) {
        alert('correct!');
    } else {
        alert('sorry');
        round_index = 0;
        game.innerHTML = '';
    }
};

function selectResult(item) {
    var id = item.getAttribute('value');
    socket.emit('search', search[search.findIndex(x => x.id == id)]);
    search = [];
    round.push(item.innerHTML);
    results.innerHTML = '';
    var li = document.createElement("li");
    li.innerHTML = round[round_index];
    game.appendChild(li);
    game_container.appendChild(game);
    if (round_index > 0) {
        if (item.innerHTML.split(' ').pop() === "(actor)") {
        theMovieDb.people.getMovieCredits({"id": id}, getStarring, errorCB);
        } else {
        theMovieDb.movies.getCredits({"id": id}, getMovie, errorCB);
        }
    }
    round_index++;
};