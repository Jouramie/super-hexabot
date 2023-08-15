import time


performances = {}


def timeit(method=None, name: str = None, print_each_call: bool = False):
    def timeit_decorator(method):
        def timed(*args, **kw):
            nonlocal name
            ts = time.perf_counter_ns()
            result = method(*args, **kw)
            te = time.perf_counter_ns()

            if name is None:
                name = kw.get("log_name", method.__name__.upper())

            delta = (te - ts) / 1e6
            if print_each_call:
                print("%r  %2.2f ms" % (name, delta))

            performances[name] = performances.get(name, 0) + delta
            return result

        return timed

    if method is not None:
        return timeit_decorator(method)

    return timeit_decorator
