__all__ = ["init_pg_db"]

import aiopg

pg_dsn = None
pool = None

async def init_pg_db(host, port, user, password, db_name):
    global pool, pg_dsn
    pg_dsn = "dbname={4} user={2} password={3} host={0} port={1}".format(host, port, user, password, db_name)
    pool = await aiopg.create_pool(pg_dsn)

async def sql_excute(sql):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                await cur.execute(sql)
            except Exception as e:
                return str(e)
            try:
                ret = []
                async for row in cur:
                    ret.append(row)
            except Exception as e:
                if str(e) == "no results to fetch":
                    ret = 0
                else:
                    ret = str(e)
            return ret
