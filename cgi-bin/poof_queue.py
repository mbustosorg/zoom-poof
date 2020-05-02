#!/usr/bin/python3

import cgi
from pythonosc import osc_message_builder
from pythonosc import udp_client

fs = cgi.FieldStorage()

ip = '10.0.1.39'
port = 9999

queue_client = udp_client.UDPClient(ip, port)

msg = osc_message_builder.OscMessageBuilder(address='/poof')
msg.add_arg(fs['name'].value)
msg.add_arg(fs['count'].value)
msg.add_arg(fs['length'].value)
queue_client.send(msg.build())

print("Content-type:text/html\r\n")
