#!/usr/bin/python3
"""
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
"""

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
msg.add_arg(fs['style'].value)
msg.add_arg(fs['timing'].value)
queue_client.send(msg.build())

print("Content-type:text/html\r\n")
