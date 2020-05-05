
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
    command = msg['name'] + ' poofed ' + msg['count'] + ' times\n';
    $('#queueText')[0].prepend(command);
});
