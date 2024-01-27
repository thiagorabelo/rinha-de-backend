import asyncio
import psycopg
import requests
import statistics
import tqdm

from functools import partial
from psycopg.rows import dict_row
from time import perf_counter
from urllib.parse import quote


class PostBenchmark:

    select_query = """
    select id, apelido, nome, nascimento, stack from pessoas
    """.strip()

    def __init__(self, url):
        self._endpoint = None
        self.url = url

    def _retrieve_data(self, cursor, limit=None):
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

    @property
    def endpoint(self):
        if not self._endpoint:
            self._endpoint = f"{self.url}/pessoas"
        return self._endpoint

    def invoke_request(self, endpoint, data):
        return requests.post(endpoint, json=data)

    def response_data_saver(self, _file, response):
        print(response.headers["Location"], file=_file)

    def run(self, executor, connection, limit=None, result_id_file=None):
        with connection.cursor(row_factory=dict_row) as cursor:
            items = (
                (self.endpoint, self._prepare_data(d))
                for d in self._retrieve_data(cursor, limit=limit)
            )
        if result_id_file:
            with open(result_id_file, "wt") as output:
                return executor(self.invoke_request, items, partial(self.response_data_saver, output))
        return executor(self.invoke_request, items)


class FindByTermBenchmark:

    select_query = "select termo from termos"

    def __init__(self, url):
        self.url = url

    def endpoint(self, term):
        return f"{self.url}/pessoas?t={quote(term)}"

    def _retrieve_data(self, cursor, limit=None):
        query = self.select_query
        if limit:
            query += " limit %(limit)s"
        cursor.execute(query, {"limit": limit})
        return cursor.fetchall()

    def invoke_request(self, endpoint, _):
        return requests.get(endpoint)

    def run(self, executor, connection, limit=None):
        with connection.cursor() as cursor:
            items = (
                (self.endpoint(term[0]), None)
                for term in self._retrieve_data(cursor, limit=limit)
            )
        return executor(self.invoke_request, items)


class GetByIdBenckmark:

    def __init__(self, url, file_):
        self.url = url
        self.file = file_

    def endpoint(self, id_):
        return f"{self.url}{id_}"

    def _retrieve_data(self, limit=None):
        with open(self.file, "rt") as file_:
            if limit:
                return [line.strip() for _, line in zip(range(limit), file_)]
            return [line.strip() for line in file_]

    def invoke_request(self, endpoint, _):
        return requests.get(endpoint)

    # TODO: Repetir (para atingir o cache), Randômico, etc?
    def run(self, executor, connection, limit=None):
        items = (
            (self.endpoint(id_), None)
            for id_ in self._retrieve_data(limit=limit)
        )
        # results = []
        # def print_pessoa(response):
        #     p = response.json()
        #     nonlocal results
        #     results.append(f"{p["apelido"]}: {p["nome"]}")
        ret = executor(self.invoke_request, items)  #, print_pessoa)
        # for result in results:
        #     print(result)
        # print("\n", end="\n")
        return ret


class RunBenchmark:

    select_query = """
    select id, apelido, nome, nascimento, stack from pessoas_pessoa
    """.strip()

    def __init__(self, url, **connection_params):
        self.connection = psycopg.connect(**connection_params)
        self.url = url

    def _run(self, request_maker, **kwargs):
        mean, variance, stdev = request_maker.run(
            self._executor,
            self.connection,
            **kwargs
        )

        print(f"Mean: {mean} seconds")
        print(f"Variance: {variance}")
        print(f"StdEv: {stdev}")

    def post(self, limit=None, result_id_file=None):
        if not(limit is None) and limit < 2:
            raise ValueError("Limit must be at least 2")
        poster = PostBenchmark(self.url)
        self._run(poster, limit=limit, result_id_file=result_id_file)

    def find_by_term(self, limit=None):
        if not(limit is None) and limit < 2:
            raise ValueError("Limit must be at least 2")
        getter = FindByTermBenchmark(self.url)
        self._run(getter, limit=limit)

    def get_by_id(self, id_resources_file, limit=None):
        if not(limit is None) and limit < 2:
            raise ValueError("Limit must be at least 2")
        getter = GetByIdBenckmark(self.url, id_resources_file)
        self._run(getter, limit=limit)


    def _executor(self, request_invoker, items, callback=None):
        times = []

        for endpoint, data in tqdm.tqdm(list(items)):  # disable=True):
            # print(f"{endpoint},  {data}")

            begin = perf_counter()
            response = request_invoker(endpoint, data)
            end = perf_counter()

            times.append(end - begin)

            if callback:
                callback(response)

            # print(f">>> {response.status_code=}")
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
