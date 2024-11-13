from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression


class Base:

    # Generate id automatically
    id = Column(Integer, primary_key=True, index=True)
    is_deleted = Column(
        Boolean, default=False, server_default=expression.false()
    )
    __mapper_args__ = {"eager_defaults": True}


Base = declarative_base(cls=Base)
