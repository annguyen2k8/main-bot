import asyncio
from discord.ext.ipc.client import Client
from config import *

ipc_client = Client(secret_key='WUT')

async def main():
    resp = await ipc_client.request("test")
    print(str(resp))

if __name__ == '__main__':
    asyncio.run(main())