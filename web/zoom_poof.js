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
