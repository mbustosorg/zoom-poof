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
from gpiozero import LED

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('IMU')
logger.setLevel(logging.INFO)

ZOOM_URL = os.getenv('ZOOM_URL')
logger.info(ZOOM_URL)

queue = []
bank1 = LED(17)
bank2 = LED(27)

def handle_poof(unused_addr, name, count, length):
    """ Handle the poof command """
    try:
        logger.info(f'Received Command - ({name}, {count}, {length})')
        with open('seq.txt', 'r') as file:
            seq = int(file.read())
        seq += 1
        response = requests.post(ZOOM_URL + str(seq), data=f'{name} poofed {count} time for {length}s each', headers={'content-type': 'text/plain'})
        print(ZOOM_URL + str(seq))
        with open('seq.txt', 'w') as file:
            file.write(str(seq))
        logger.info(f'Sequence: {seq}')
        logger.info(response)
        queue.append((name, count, length))
    except ValueError as e:
        logger.error(e)

async def run_command(command):
    current_milli_time = lambda: int(round(time.time() * 1000))
    current_command = None
    current_start = 0
    logger.info(f'Run Command {command}')
    for i in range(int(command[1])):
        bank1.on()
        bank2.on()
        ledshim.set_all(255, 0, 0)
        ledshim.show()
        await asyncio.sleep(float(command[2]))
        bank1.off()
        bank2.off()
        ledshim.set_all(0, 255, 0)
        ledshim.show()
        await asyncio.sleep(float(command[2]))
    ledshim.set_all(0, 0, 255)
    ledshim.show()
    logger.info(f'Complete')
    

async def main_loop():
    while True:
        if len(queue) > 0:
            logger.info(f'{len(queue)} commands in the queue')
            await asyncio.create_task(run_command(queue.pop(0)))
        await asyncio.sleep(1)

async def init_main(args, dispatcher):
    loop = asyncio.get_event_loop()
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, loop)
    transport, protocol = await server.create_serve_endpoint()

    await main_loop()

    transport.close()


if __name__ == "__main__":

    with open('seq.txt', 'w') as file:
        file.write('0')
        
    ledshim.set_all(0, 0, 255)
    ledshim.show()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="10.0.1.39", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=9999, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = Dispatcher()
    dispatcher.map("/poof", handle_poof)

    logger.info(f'Serving on {args.ip}:{args.port}')

    asyncio.run(init_main(args, dispatcher))
