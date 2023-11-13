import sys
import os
import traceback
import requests
import asyncio
import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
from fake_useragent import UserAgent
from timeit import default_timer
import logging
import datetime
from dataclasses import dataclass
from dataclasses import field
import codecs
import tomllib


# logging: netstream.log or netstream.log + console
# logging.basicConfig(handlers=[logging.FileHandler(os.path.join('netstream.log'), 'w', 'utf-8')], level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d.%m.%y %H:%M:%S')
logging.basicConfig(handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join('netstream.log'), 'w', 'utf-8')], level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d.%m.%y %H:%M:%S')


class Netstream():
    def __init__(self):
        self.data = dict()
        self.total = 0
        self.received = 0
        self.status = 'init'
        self.started = default_timer()
        try:
            with open('netstream.toml', 'rb') as f:
                config = tomllib.load(f)
            self.proxy = config['connection']['proxy']
            self.timeout = config['connection']['timeout']
            self.attemps = config['connection']['attemps']
            self.status = 'ready'
        except * (FileNotFoundError, KeyError) as e:
            e.add_note('Configuration file not correct! Please try again.')
            logging.error(e.__notes__[0])
            self.status = 'config error'


    def finish(self):
        time_total = f'{default_timer() - self.started:1.2f}s'
        logging.info(f'finished at {time_total}')


    async def get_page(self, client, target):
        async with client.get(target) as response:
            if response.status != 200:
                return ''
            return await response.read()


    async def get_data(self, target):
        attemp = 0
        loop = asyncio.get_running_loop()
        while (attemp < self.attemps):
            attemp += 1
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = ProxyConnector.from_url(self.proxy)
            headers = {'User-Agent': UserAgent().chrome}
            async with aiohttp.ClientSession(loop=loop, headers=headers, connector=connector, timeout=timeout) as client:
                logging.debug(f'receiving page data: {target} ({attemp}/{self.attemps})')
                try:
                    data = await self.get_page(client, target)
                    if data:
                        self.data[target] = data.decode('utf-8')
                        logging.debug(f'!received page data: {target} ({attemp}/{self.attemps})')
                        self.received += 1
                        break
                    else:
                        self.data[target] = ''
                except:
##                    logging.debug(traceback.format_exc())
                    ...


    async def start(self, targets):
        logging.info(f'started')
        await asyncio.gather(*(self.get_data(target) for target in targets))


    def run(self, targets):
        if self.status != 'ready':
            logging.warning(f'Netstream not ready')
        else:
            self.total = len(targets)
            asyncio.run(self.start(targets))
            self.finish()
        return self.data


def main():
    urls = [fr'https://ya.ru', fr'http://jsonip.com']
    ns = Netstream()
    data = ns.run(targets=urls)
    complete = f'{100*ns.received/ns.total:.0f}' if ns.total else 0
    logging.info(f'result {complete}% (errors {ns.total-ns.received}) ')
    logging.debug(f'{data}')


if __name__ == "__main__":
    main()
