"""数据库：引擎、会话、WAL 模式、建表。"""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, Session

from app import models  # noqa: F401  注册全部模型
from app.config import Settings


def build_engine(database_url: str) -> Engine:
    """创建 SQLite 引擎，开启 WAL 与并发读。"""
    connect_args: dict = {"check_same_thread": False}
    if database_url.startswith("sqlite"):
        connect_args.setdefault("timeout", 30)
        # 内存库需共享连接（StaticPool），否则多线程/多连接各自独立库
        if ":memory:" in database_url:
            from sqlalchemy.pool import StaticPool

            return create_engine(
                database_url,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
    return create_engine(database_url, connect_args=connect_args)


def init_db(engine: Engine) -> None:
    """建表并启用 WAL。"""
    SQLModel.metadata.create_all(engine)
    if str(engine.url).startswith("sqlite"):
        with engine.connect() as conn:
            conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
            conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
            conn.commit()


def session_factory(engine: Engine):
    """生成 session 工厂。"""

    def _factory() -> Session:
        return Session(engine)

    return _factory
