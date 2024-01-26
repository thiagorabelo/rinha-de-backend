import asyncio
import psycopg
import requests
import statistics
import tqdm

from psycopg.rows import dict_row
from time import perf_counter

psycopg.connect
class RunBenchmark:

    select_query = """
    select id, apelido, nome, nascimento, stack from pessoas_pessoa
    """.strip()

    def __init__(self, url, **connection_params):
        connection_params["row_factory"] = dict_row
        self.connection = psycopg.connect(**connection_params)
        self.url = url

    def _retrieve_data(self, limit=None):
        with self.connection.cursor() as cursor:
            query = self.select_query
            if limit:
                query += " limit %(limit)s"
            cursor.execute(query, {"limit": limit})
            return cursor.fetchall()

    def _prepare_data(self, row):
        return {
            "id": str(row["id"]),
            "apelido": row["apelido"],
            "nome": row["nome"],
            "nascimento": str(row["nascimento"]),
            "stack": row["stack"]
        }

    def _post_endpoint(self):
        return f"{self.url}/pessoas"

    def post(self, limit=None):
        if limit < 2:
            raise ValueError("Limit must be at least 2")

        url = self._post_endpoint()

        items = (
            (url, self._prepare_data(d))
            for d in self._retrieve_data(limit=limit)
        )

        mean, variance, stdev = self._run(
            lambda endpoint, data: requests.post(endpoint, json=data),
            items
        )

        print(f"Mean: {mean} seconds")
        print(f"Variance: {variance}")
        print(f"StdEv: {stdev}")

    def _run(self, runner, items):
        times = []

        for endpoint, data in tqdm.tqdm(list(items)):  # disable=True):
            begin = perf_counter()
            # print(f"{endpoint},  {data}")
            response = runner(endpoint, data=data)

            end = perf_counter()

            times.append(end - begin)

        return (
            statistics.mean(times),
            statistics.variance(times),
            statistics.stdev(times),
        )


def main():
    pass

def async_tests():
    async def teste(t=5, s=0.5):
        c = 0
        while c < t:
            await asyncio.sleep(s)
            print(f"Dormi por {s}s")
            c += 1


    async def main():
        print("Olá da main coro")
        loop = asyncio.get_event_loop()
        loop.create_task(teste())
        for i in range(20):
            await asyncio.sleep(1)
            print("Main dormiu 1s")


    asyncio.run(main())
