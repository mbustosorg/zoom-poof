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

import argparse
import logging
import os
import requests
import time

from pythonosc import osc_message_builder
from pythonosc import udp_client
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
from gpiozero import LED, Button

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('POOF')
logger.setLevel(logging.INFO)

ZOOM_URL = os.getenv('ZOOM_URL')
logger.info(f'ZOOM_URL={ZOOM_URL}')

queue = []
relays = [LED(17, active_high=False), LED(27, active_high=False), LED(23, active_high=False), LED(24, active_high=False)]
remotes = [Button(16), Button(20), Button(21), Button(26)]
led_play = None


def broadcast_color(red: int, green: int, blue: int):
    """ Send out color """
    msg = osc_message_builder.OscMessageBuilder(address='/color')
    msg.add_arg(red)
    msg.add_arg(green)
    msg.add_arg(blue)
    led_play.send(msg.build())


def handle_poof(unused_addr, name, count, length, style, timing):
    """ Handle the poof command """
    try:
        logger.info(f'Received Command - ({name}, {count}, {length}, {style}, {timing})')
        queue.append((name, count, length, style, timing))
        with open('seq.txt', 'r') as file:
            seq = int(file.read())
        seq += 1
        #response = requests.post(ZOOM_URL + str(seq), data=f'{name} poofed {count} time for {length}s each', headers={'content-type': 'text/plain'})
        #with open('seq.txt', 'w') as file:
        #    file.write(str(seq))
        #logger.info(f'Sequence: {seq}')
        #logger.info(response)
    except ValueError as e:
        logger.error(e)

        
async def run_command(command):
    """ Run 'command' """
    logger.info(f'Run Command {command}')
    timing = float(command[2])
    count = int(command[1])
    style = command[3]
    timing_style = command[4]
    cylon_index = 0
    cylon_direction = 1
    for i in range(count):
        if 'Full' in style:
            [x.on() for x in relays]
            broadcast_color(0, 50, 0)
        elif 'Alternating' in style:
            relays[0].on()
            relays[1].on()
            relays[2].off()
            relays[3].off()
            broadcast_color(0, 50, 0)
        elif 'Cylon' in style:
            relays[cylon_index].on()
            if cylon_index == 0:
                broadcast_color(0, 50, 0)
            elif cylon_index == 1:
                broadcast_color(0, 0, 50)
            elif cylon_index == 2:
                broadcast_color(50, 0, 50)
            elif cylon_index == 3:
                broadcast_color(50, 50, 50)

        await asyncio.sleep(timing)

        if 'Full' in style:
            [x.off() for x in relays]
            broadcast_color(0, 0, 50)
            await asyncio.sleep(timing)
        elif 'Alternating' in style:
            relays[0].off()
            relays[1].off()
            relays[2].on()
            relays[3].on()
            broadcast_color(0, 0, 50)
            await asyncio.sleep(timing)

        elif 'Cylon' in style:
            [x.off() for x in relays]

        if 'Accelerating' in timing_style:
            timing = max(0.05, timing - float(i + 1) / float(count) * timing)
        if 'Cylon' in style:
            cylon_index = cylon_index + cylon_direction
            if cylon_index == 4:
                cylon_direction = -1
                cylon_index = 2
            elif cylon_index == -1:
                cylon_direction = 1
                cylon_index = 1
    [x.off() for x in relays]
    broadcast_color(50, 0, 0)
    logger.info(f'Complete')
    

async def main_loop():
    """ Main execution loop """
    [x.off() for x in relays]
    while True:
        if len(queue) > 0:
            logger.info(f'{len(queue)} commands in the queue')
            await asyncio.create_task(run_command(queue.pop(0)))
        await asyncio.sleep(0.1)
        for i in range(0, 4):
            if not remotes[i].is_pressed and relays[i].is_lit:
                logger.info(f'Remote off {i}')
                broadcast_color(50, 0, 0)
                relays[i].off()
            elif remotes[i].is_pressed and not relays[i].is_lit:
                logger.info(f'Remote on {i}')
                broadcast_color(30, 30, 30)
                relays[i].on()


async def init_main(args, dispatcher):
    """ Initialization routine """
    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, loop)
    transport, protocol = await server.create_serve_endpoint()

    await main_loop()

    transport.close()


if __name__ == "__main__":

#    with open('seq.txt', 'w') as file:
#        file.write('0')
        
    [x.off() for x in relays]

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.0.100", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9999, help="The port to listen on")
    parser.add_argument("--color_ip", default="192.168.0.100", help="IP for color server")
    parser.add_argument("--color_port", type=int, default=9997, help="Port for color server")
    args = parser.parse_args()

    led_play = udp_client.UDPClient(args.color_ip, args.color_port)

    dispatcher = Dispatcher()
    dispatcher.map("/poof", handle_poof)

    logger.info(f'Serving on {args.ip}:{args.port}')

    asyncio.run(init_main(args, dispatcher))
