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

var socket = io();

$('#submitPoof').submit(function (e) {

    e.preventDefault();

    $('#exampleModal').modal('show');
    
    command = {}
    command.name = $('#inputName')[0].value;
    command.count = $('#poofCount')[0].value;
    command.length = $('#poofLength')[0].value;
    command.style = $('#poofStyle')[0].value;
    command.timing = $('#poofTiming')[0].value;

    console.log(command);

    socket.emit('poof', command);

    return false;
});


socket.on('poof', function(msg){
    console.log('broadcast ' + JSON.stringify(msg));
    var time = new Date();
    var hour = time.getHours();
    var minutes = time.getMinutes();
    console.log('broadcast ' + JSON.stringify(msg));
    command = hour + ':' + minutes + ' - ' + msg['name'] + ' poofed ' + msg['count'] + ' times\n';
    $('#queueText')[0].prepend(command);
});
