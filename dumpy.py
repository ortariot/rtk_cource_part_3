import aiohttp
from aiohttp.web_exceptions import HTTPException
from aiohttp.client_exceptions import ContentTypeError
import asyncio
from pprint import pprint


from data_store_tools import DataStoreTools
from config import SQLALCHEMY_DATABASE_URI


class DummyData:

    URL = 'https://dummyjson.com/users'

    def __init__(self, tools):
        self.tools = tools

    async def request_dummy_users(
            self, limit: int, skip: int, session
    ) -> aiohttp.ClientSession:

        try:
            response = await session.get(
                self.URL,
                params={'limit': limit, 'skip': skip}
            )
        except HTTPException as e:
            print(
                (
                    f'error {e} in request_dummy_users for url'
                    f' : {self.URL} with limit: {limit}, skip: {skip}'
                )
            )
            response = None
        return response

    async def get_dummy_users(
        self, limit: int, total: int, wait_time: int
    ) -> list[dict[str, str]]:

        cnt = 0
        tasks = []

        timeout = aiohttp.ClientTimeout(total=wait_time)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            while cnt < total:
                if total - cnt > limit:
                    tasks.append(
                        asyncio.create_task(
                            self.request_dummy_users(limit, cnt, session)
                        )
                    )
                else:
                    tasks.append(
                        asyncio.create_task(
                            self.request_dummy_users(
                                total-cnt, cnt, session)
                        )
                    )
                cnt += limit

            responses = await asyncio.gather(*tasks)
            out = []
            for item in responses:
                try:
                    data = await item.json()
                except ContentTypeError as e:
                    print(f'error - {e}')
                    data = {}
                try:
                    data = data['users']
                except KeyError:
                    data = []
                result = [{'name': item['firstName'] + ' ' + item['lastName'],
                           'phone': item['phone'],
                           'mail': item['email'],
                           'login': item['username'],
                           'password': item['password']
                           } for item in data]
                out.extend(result)
        return out

    async def insert_user_to_data_store(self, user: dict) -> str:

        check_user = await self.tools.chek_user(user['login'])
        if check_user:
            user = await self.tools.update_user(
                user=check_user,
                name=user['name'],
                phone=user['phone'],
                mail=user['mail'],
                password=user['password']
            )
            res = 'update'
        else:
            user = await self.tools.crate_user(
                name=user['name'],
                phone=user['phone'],
                mail=user['mail'],
                login=user['login'],
                password=user['password']
            )
            res = 'create'
        return f'user {user.login} is {res}'

    async def insert_all_users_to_data_store(
            self, tools: DataStoreTools, users: list
    ) -> list:

        tasks = [asyncio.create_task(
            self.insert_user_to_data_store(user)
        ) for user in users]

        result = await asyncio.gather(*tasks)
        return [item for item in result]


if __name__ == '__main__':
    tools = DataStoreTools(SQLALCHEMY_DATABASE_URI)
    dumpy = DummyData(tools)
    get_users = asyncio.run(dumpy.get_dummy_users(20, 100, 1))

    pprint(get_users)
    add_users = asyncio.run(
        dumpy.insert_all_users_to_data_store(tools, get_users)
    )
    pprint(add_users)
