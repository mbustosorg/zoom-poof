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
import math
import os
import requests
import time

from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
import ledshim
from gpiozero import LED, Button

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('IMU')
logger.setLevel(logging.INFO)

ZOOM_URL = os.getenv('ZOOM_URL')
logger.info(ZOOM_URL)

queue = []
relays = [LED(17, active_high=False), LED(27, active_high=False), LED(23, active_high=False), LED(24, active_high=False)]
remotes = [Button(16, pull_up=False), Button(20, pull_up=False), Button(21, pull_up=False), Button(26, pull_up=False)]


def display_status(display_range, red, green, blue):
    """ Update the display """
    for i in display_range:
        ledshim.set_pixel(i, red, green, blue)
    ledshim.show()

    
def handle_poof(unused_addr, name, count, length, style, timing):
    """ Handle the poof command """
    try:
        logger.info(f'Received Command - ({name}, {count}, {length}, {style}, {timing})')
        queue.append((name, count, length, style, timing))
        with open('seq.txt', 'r') as file:
            seq = int(file.read())
        seq += 1
        #esponse = requests.post(ZOOM_URL + str(seq), data=f'{name} poofed {count} time for {length}s each', headers={'content-type': 'text/plain'})
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
            display_status(range(0, 28), 255, 0, 0)
        elif 'Alternating' in style:
            relays[0].on()
            relays[1].on()
            relays[2].off()
            relays[3].off()
            display_status(range(0, 14), 255, 0, 0)
            display_status(range(14, 28), 0, 255, 0)
        elif 'Cylon' in style:
            relays[cylon_index].on()
            display_status(range(0, 28), 0, 255, 0)
            display_status(range(cylon_index * 7, (cylon_index + 1) * 7), 255, 0, 0)
        await asyncio.sleep(timing)
        if 'Full' in style:
            [x.off() for x in relays]
            display_status(range(0, 28), 0, 255, 0)
        elif 'Alternating' in style:
            relays[0].off()
            relays[1].off()
            relays[2].on()
            relays[3].on()
            display_status(range(0, 14), 0, 255, 0)
            display_status(range(14, 28), 255, 0, 0)
        elif 'Cylon' in style:
            [x.off() for x in relays]
            display_status(range(0, 28), 0, 255, 0)
        await asyncio.sleep(timing)
        if 'Accelerating' in timing_style:
            timing *= 0.5 # max(0.0, timing - float(i + 1) / float(count) * timing)
        if 'Cylon' in style:
            cylon_index = cylon_index + cylon_direction
            if cylon_index == 4:
                cylon_direction = -1
                cylon_index = 2
            elif cylon_index == -1:
                cylon_direction = 1
                cylon_index = 1
    [x.off() for x in relays]
    display_status(range(0, 28), 0, 0, 255)
    logger.info(f'Complete')
    

async def main_loop():
    """ Main execution loop """
    [x.off() for x in relays]
    while True:
        if len(queue) > 0:
            logger.info(f'{len(queue)} commands in the queue')
            await asyncio.create_task(run_command(queue.pop(0)))
        await asyncio.sleep(1)
        if remotes[0].is_pressed:
            handle_poof(None, 'remote', 10, 1.0, 'Full', 'Accelerating')
        elif remotes[1].is_pressed:
            handle_poof(None, 'remote', 10, 2.0, 'Cylon', 'Accelerating')
        elif remotes[2].is_pressed:
            handle_poof(None, 'remote', 10, 3.0, 'Alternating', 'Accelerating')
        elif remotes[3].is_pressed:
            handle_poof(None, 'remote', 10, 3.0, 'Cylon', 'Accelerating')


async def init_main(args, dispatcher):
    """ Initialization routine """
    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, loop)
    transport, protocol = await server.create_serve_endpoint()

    await main_loop()

    transport.close()


if __name__ == "__main__":

    with open('seq.txt', 'w') as file:
        file.write('0')
        
    [x.off() for x in relays]
    display_status(range(0, 28), 0, 0, 255)

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.0.101", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9999, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = Dispatcher()
    dispatcher.map("/poof", handle_poof)

    logger.info(f'Serving on {args.ip}:{args.port}')

    asyncio.run(init_main(args, dispatcher))
