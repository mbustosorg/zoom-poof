/*
    Copyright (C) 2020 Mauricio Bustos (m@bustos.org)
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var port = process.env.PORT || 3000;
var fs = require('fs');
var osc = require('osc');
require('log-timestamp');

var oscPort = new osc.UDPPort({
    localAddress: "0.0.0.0",
    localPort: 9998,
    metadata: true
});
oscPort.open();

app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

app.get('/index.js', function(req, res){
  res.sendFile(__dirname + '/index.js');
});

app.get('/floating-labels.css', function(req, res){
    res.writeHead(200, {'Content-type' : 'text/css'});
    var fileContents = fs.readFileSync(__dirname + '/floating-labels.css', {encoding: 'utf8'});
    res.write(fileContents);
    res.end();
});

app.get('/rhb.png', function(req, res){
  res.sendFile(__dirname + '/rhb.png');
});

io.on('connection', function(socket){
    socket.on('poof', function(msg){
	console.log('Command: ' + JSON.stringify(msg));
	io.emit('poof', msg);
	oscPort.send({
	    address: '/poof',
	    args: [
		{type: 's', value: msg['name']},
		{type: 'i', value: msg['count']},
		{type: 'f', value: msg['length']},
		{type: 's', value: msg['style']},
		{type: 's', value: msg['timing']}
	    ]}, '10.0.1.39', 9999);
    });
});

http.listen(port, function(){
  console.log('listening on *:' + port);
});
