import asyncio
from datetime import datetime

from sqlalchemy import (
    Column, LargeBinary, String, DateTime, BigInteger
)
from sqlalchemy.orm import declarative_base, declarative_mixin
from sqlalchemy.ext.asyncio import create_async_engine

from config import SQLALCHEMY_DATABASE_URI

Base = declarative_base()


@declarative_mixin
class BaseModelMixin:
    id = Column(BigInteger, primary_key=True)
    create_date = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow)
    update_date = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Users(Base, BaseModelMixin):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    mail = Column(String, unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)

    def __repr__(self):
        return (
            f'id: {self.id} name: {self.name} login: {self.login} '
            f'phone: {self.phone}, e-mail: {self.mail}'
        )


async def create_scheme():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URI)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(create_scheme())
