$('#submitPoof').submit(function () {
    name = $('#inputName')[0].value;
    count = $('#poofCount')[0].value;
    length = $('#poofLength')[0].value;

    console.log(name);
    console.log(count);
    console.log(length);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/cgi-bin/queue.py?name=' + name + '&count=' + count + '&length=' + length);
    xhr.send();

    return false;
});