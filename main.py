import aiohttp
import asyncio
from pprint import pprint


async def main():

    async with aiohttp.ClientSession() as session:
        async with session.get('https://dummyjson.com/users?limit=20&skip=0') as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            response = await response.json()

            out = [{'name': item['firstName'] + ' ' + item['lastName'],
                    'phone': item['phone'],
                    'email': item['email'],
                    'login': item['username'],
                    'password': item['password']
                    } for item in response['users']]
            # for items in response['users']:
            # pprint(items)
            pprint(len(out))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
