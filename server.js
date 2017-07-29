// server.js
// where your node app starts

// init project
var express = require('express');
var serveIndex = require('serve-index'); //https://github.com/expressjs/serve-index
var app = express();

// we've started you off with Express, 
// but feel free to use whatever libs or frameworks you'd like through `package.json`.
var turf = require('turf');

// http://expressjs.com/en/starter/static-files.html
app.use(express.static('public'));

// Serve URLs like /ftp/thing as public/ftp/thing
app.use('/', serveIndex('public', {'icons': true}))

// http://expressjs.com/en/starter/basic-routing.html
//app.get("/", function (request, response) {
//  response.sendFile(__dirname + '/views/index.html');
//});


// listen for requests :)
var listener = app.listen(process.env.PORT, function () {
  console.log('Your app is listening on port ' + listener.address().port);
});
