import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from aiopath import AsyncPath
from exchange import exchange
from datetime import datetime

LOGFILE = 'logs.txt.'


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def send_currency_exchange(self, message, ):
        if message == 'exchange':
            rate = await exchange()
            await self.send_to_clients(f"{'Currency exchange'}: {rate}")
            logging.info(f'Currency exchange for today')
            log = f'{datetime.now()} user called currency exchange \n'
            await logging_check(log)
        if message.startswith('exchange') and message != 'exchange':
            days = message[-1]
            rate = await exchange(days)
            await self.send_to_clients(f"{'Currency exchange'}: {rate}")
            logging.info(f'Exchange rate for {days} day')
            log = f'{datetime.now()}  user called currency exchange\n'
            await logging_check(log)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            await self.send_to_clients(f"{ws.name}: {message}")
            if message.startswith('exchange'):
                await self.send_currency_exchange(message)


async def logging_check(log):
    log_file = AsyncPath(LOGFILE)
    if await log_file.exists():
        with open(LOGFILE, 'a') as file:
            file.write(f'{log}\n')
    else:
        await log_file.touch()


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
