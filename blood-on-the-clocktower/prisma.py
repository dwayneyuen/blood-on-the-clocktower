import asyncio
from prisma import Prisma


prisma_client = Prisma()
loop = asyncio.get_event_loop()
loop.run_until_complete(prisma_client.connect())
