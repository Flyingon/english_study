#-*- coding: utf-8 -*-

import asyncio
import aiopg

dsn = "dbname=english user=root_yzy password=Yzy^105178 host=postgres-iuaw1qed.sql.tencentcdb.com port=9969"

table_account_sql = """
    CREATE TABLE users (
      username varchar(64),
      account varchar(64) PRIMARY KEY,
      password varchar(64) NOT NULL,
      email varchar(64),
      active integer DEFAULT 1,
      create_time timestamp DEFAULT current_timestamp
);
"""

async def go():
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(table_account_sql)
                ret = []
                async for row in cur:
                    ret.append(row)
                return ret

async def format():
    data = await go()
    print("Result: ", data)


loop = asyncio.get_event_loop()
loop.run_until_complete(format())
