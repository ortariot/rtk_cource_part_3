import aiohttp
import asyncio
from pprint import pprint

from sqlalchemy.ext.asyncio import create_async_engine

from data_store_tools import DataStoreTools
from config import SQLALCHEMY_DATABASE_URI


async def get_dummy_users(limit, total, wait_time):
    timeout = aiohttp.ClientTimeout(total=wait_time)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        cnt = 0
        tasks = []

        while cnt < total:
            if total - cnt > limit:
                tasks.append(asyncio.create_task(session.get(
                    f'https://dummyjson.com/users?limit={limit}&skip={cnt}')
                ))
            else:
                tasks.append(asyncio.create_task(session.get(
                    f'https://dummyjson.com/users?limit={total-cnt}&skip={cnt}')
                ))
            cnt += limit

        responses = await asyncio.gather(*tasks)
        out = []
        for item in responses:
            data = await item.json()
            result = [{'name': item['firstName'] + ' ' + item['lastName'],
                       'phone': item['phone'],
                       'email': item['email'],
                       'login': item['username'],
                       'password': item['password']
                       } for item in data['users']]
            out.extend(result)
        return out


async def insert_users_to_data_store(tools, users):
    for user in users:
        check_user = await tools.chek_user(user['login'])
        if check_user:
            await tools.crate_user(
                user['name'],
                user['phone'],
                user['mail'],
                user['login'],
                user['password']
            )
        else:
            await tools.crate_user(
                user['name'],
                user['phone'],
                user['mail'],
                user['login'],
                user['password']
            )


if __name__ == '__main__':
    users = asyncio.run(get_dummy_users(5, 20, 1))
    tools = DataStoreTools(SQLALCHEMY_DATABASE_URI)
    pprint(users)
    asyncio.run(insert_users_to_data_store(tools, users))
