from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import bcrypt

from models import Users


from config import SQLALCHEMY_DATABASE_URI


class DataStoreTools():

    def __init__(self, uri: str) -> None:
        self.engine = create_async_engine(uri)

    def async_session_executor(proc):
        async def wrapper(*args, **kwargs):
            self = args[0]
            engine = self.engine
            async_sesion_factory = sessionmaker(
                engine,
                expire_on_commit=False,
                class_=AsyncSession
            )
            async with async_sesion_factory() as session:
                async with session.begin():
                    try:
                        # print('PARAM')
                        # print(args)
                        # print(kwargs)
                        res = await proc(*args, **kwargs, session=session)
                    except NoResultFound as e:
                        print(
                            (f'error: {e}  function: {proc.__name__} '
                             f'args: {args} kwargs: {kwargs}'
                             )
                        )
                        return None
            return res
        return wrapper

    @async_session_executor
    async def crate_user(
        self, name: str, phone: str, mail: str,
        login: str, password: str, session: Session
    ) -> Users:

        user = Users(
            name=name,
            phone=phone,
            mail=mail,
            login=login,
            password=bcrypt.hashpw(
                password.encode(), bcrypt.gensalt()),
        )
        session.add(user)
        return user

    @async_session_executor
    async def update_user(
        self, name: str, phone: str, mail: str,
        password: str, user: Users, session: Session
    ) -> Users:

        user.name = name
        user.phone = phone
        user.mail = mail
        user.password = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        )

        session.add(user)
        return user

    @async_session_executor
    async def chek_user(self, login: str, session: Session = None) -> bool:

        query_user = select(Users).where(Users.login == login)
        query_user_result = await session.execute(query_user)
        user = query_user_result.scalar_one()
        return user
