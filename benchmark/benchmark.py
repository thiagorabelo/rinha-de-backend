import json
import requests
import statistics
import tqdm

from django.conf import settings
from django.db import connections
from itertools import count
from functools import partial
from time import perf_counter
from urllib.parse import quote


class PostBenchmark:

    def __init__(self, url, json_file):
        self._endpoint = None
        self.url = url
        self.json_file = json_file

    def _retrieve_data(self, limit=None):
        with open(self.json_file, "rt") as json_file:
            counter = range(limit) if limit else count()
            result = [
                line for _, line in zip(counter, json_file)
            ]
            return result

    def _prepare_data(self, line):
        return json.loads(line)

    @property
    def endpoint(self):
        if not self._endpoint:
            self._endpoint = f"{self.url}/pessoas"
        return self._endpoint

    def invoke_request(self, endpoint, data):
        return requests.post(endpoint, json=data)

    def response_data_saver(self, _file, response):
        try:
            print(response.headers["Location"], file=_file)
        except KeyError:
            pass

    def run(self, executor, limit=None, result_id_file=None):
        items = (
            (self.endpoint, self._prepare_data(d))
            for d in self._retrieve_data(limit=limit)
        )
        if result_id_file:
            with open(result_id_file, "wt") as output:
                return executor(self.invoke_request, items, partial(self.response_data_saver, output))
        return executor(self.invoke_request, items)


class FindByTermBenchmark:

    def __init__(self, url, resource_path):
        self.url = url
        self.resource_path = resource_path

    def endpoint(self, term):
        return f"{self.url}/pessoas?t={quote(term)}"

    def _retrieve_data(self, limit=None):
        with open(self.resource_path, "rt") as term_file:
            counter = range(limit) if limit else count()
            result = [
                d for _, d in zip(counter, term_file)
            ]
            return result

    def invoke_request(self, endpoint, _):
        return requests.get(endpoint)

    def run(self, executor, limit=None):
        items = (
            (self.endpoint(term[0]), None)
            for term in self._retrieve_data(limit=limit)
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
    def run(self, executor, limit=None):
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

    def __init__(self, url):
        self.url = url

    def _run(self, request_maker, **kwargs):
        mean, variance, stdev = request_maker.run(
            self._executor,
            **kwargs
        )

        print(f"Mean: {mean} seconds")
        print(f"Variance: {variance}")
        print(f"StdEv: {stdev}")

    def post(self, json_path, limit=None, result_id_file=None):
        if not(limit is None) and limit < 2:
            raise ValueError("Limit must be at least 2")
        poster = PostBenchmark(self.url, json_path)
        self._run(poster, limit=limit, result_id_file=result_id_file)

    def find_by_term(self, term_resources_file, limit=None):
        if not(limit is None) and limit < 2:
            raise ValueError("Limit must be at least 2")
        getter = FindByTermBenchmark(self.url, term_resources_file)
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


def _get_conn():
    conf = settings.DATABASES["default"]
    user = conf["USER"]
    password = conf["PASSWORD"]
    host = conf["HOST"]
    port = conf["PORT"]
    name = conf["NAME"]
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def sql_find_by_tsvector(path, limit=None, close_con=False):
    lines = None
    with open(path, "rt") as term_file:
            counter = range(limit) if limit else count()
            lines = [
                d for _, d in zip(counter, term_file)
            ]

    sql = """
        SELECT "pessoas_pessoa"."apelido", "pessoas_pessoa"."nome", "pessoas_pessoa"."stack",
        ("pessoas_pessoa"."nascimento")::varchar AS "nascimento" FROM "pessoas_pessoa" WHERE
        "pessoas_pessoa"."search_field" @@ (to_tsquery( %(terms)s )) LIMIT 50
    """.strip()

    times = []

    for idx, line in enumerate(lines):
        terms = " & ".join(line.split())

        # print(">>> " + sql % {"terms": terms})

        connection = None
        begin = perf_counter()
        try:
            connection = connections["default"]
            with connection.cursor() as cursor:
                cursor.execute(sql, {"terms": terms})
                data = cursor.fetchall()
        finally:
            if close_con:
                connection.close()
        end = perf_counter()

        print(f"{idx}: {len(data)=}")

        times.append(end - begin)

    mean = statistics.mean(times)
    variance = statistics.variance(times)
    stdev = statistics.stdev(times)

    print(f"Mean: {mean} seconds")
    print(f"Variance: {variance}")
    print(f"StdEv: {stdev}")


def sql_find_by_text(path, limit=None, close_con=False):
    lines = None
    with open(path, "rt") as term_file:
            counter = range(limit) if limit else count()
            lines = [
                d for _, d in zip(counter, term_file)
            ]

    sql = """
        SELECT "pessoas_pessoa"."apelido", "pessoas_pessoa"."nome", "pessoas_pessoa"."stack",
        ("pessoas_pessoa"."nascimento")::varchar AS "nascimento" FROM "pessoas_pessoa" WHERE
    """.strip()

    times = []

    for idx, line in enumerate(lines):
        clause = """"pessoas_pessoa"."search_row" like '%%' || lower( %s ) || '%%' """
        terms = line.split()
        clauses = [clause for _ in terms]
        sql_ = sql + " " + " and ".join(clauses) + " LIMIT 50"

        # print(">>> " + sql_ + " :: " + str(terms))
        # print(">>> " + (sql_ % terms))

        connection = None
        begin = perf_counter()
        try:
            connection = connections["default"]
            with connection.cursor() as cursor:
                cursor.execute(sql_, terms)
                data = cursor.fetchall()
        finally:
            if close_con:
                connection.close()
        end = perf_counter()

        print(f"{idx}: {len(data)=}")

        times.append(end - begin)

    mean = statistics.mean(times)
    variance = statistics.variance(times)
    stdev = statistics.stdev(times)

    print(f"Mean: {mean} seconds")
    print(f"Variance: {variance}")
    print(f"StdEv: {stdev}")
