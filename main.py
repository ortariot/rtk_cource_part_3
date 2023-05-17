import aiohttp
import asyncio
from pprint import pprint


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
                    f'https://dummyjson.com/users?limit={limit}&skip={cnt}'
                )
                ))
            else:
                tasks.append(asyncio.create_task(session.get(
                    f'https://dummyjson.com/users?limit={total-cnt}&skip={cnt}'
                )
                ))
            cnt += limit

        responses = await asyncio.gather(*tasks)
        out = []
        for item in responses:
            data = await item.json()
            result = [{'name': item['firstName'] + ' ' + item['lastName'],
                       'phone': item['phone'],
                       'mail': item['email'],
                       'login': item['username'],
                       'password': item['password']
                       } for item in data['users']]
            out.extend(result)
        return out


async def insert_user_to_data_store(tools, user):
    check_user = await tools.chek_user(user['login'])
    if check_user:
        user = await tools.update_user(
            user=check_user,
            name=user['name'],
            phone=user['phone'],
            mail=user['mail'],
            password=user['password']
        )
        res = 'update'
    else:
        user = await tools.crate_user(
            name=user['name'],
            phone=user['phone'],
            mail=user['mail'],
            login=user['login'],
            password=user['password']
        )
        res = 'create'
    return f'user {user.login} is {res}'


async def insert_all_users_to_data_store(tools, users):

    tasks = [asyncio.create_task(
        insert_user_to_data_store(tools, user)
    ) for user in users]

    result = await asyncio.gather(*tasks)
    return [item for item in result]


if __name__ == '__main__':
    get_users = asyncio.run(get_dummy_users(20, 100, 1))
    tools = DataStoreTools(SQLALCHEMY_DATABASE_URI)
    pprint(get_users)
    add_users = asyncio.run(insert_all_users_to_data_store(tools, get_users))
    pprint(add_users)
