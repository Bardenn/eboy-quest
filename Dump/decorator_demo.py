import time

def timeit(f):
    def g():
        start = time.time()
        res = f()
        end = time.time()
        duration = end-start
        return res, duration
    return g

@timeit
def complex_math():
    time.sleep(2)
    return 5

print(complex_math())