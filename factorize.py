import time
from multiprocessing import Pool, cpu_count, Process, Semaphore


a_ = [1, 2, 4, 8, 16, 32, 64, 128]
b_ = [1, 3, 5, 15, 17, 51, 85, 255]
c_ = [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
d_ = [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106,
      1521580, 2130212, 2662765, 5325530, 10651060]


def divided_numbers(number: int) -> list:
    ls = list(filter(lambda x: number % x == 0, range(1, number + 1)))
    return ls


def sem_worker(sem: Semaphore, number: int):
    with sem:
        divided_numbers(number)


def callback(result):
    print([x == y for x, y in zip([a_, b_, c_, d_], result)])


def factorize(*number):
    # synchro
    s_time_start = time.time()
    result_synchro = [divided_numbers(val) for val in number]
    s_time_stop = time.time() - s_time_start
    print(f'Synchro time: {s_time_stop:.4f} seconds')
    print([x == y for x, y in zip([a_, b_, c_, d_], result_synchro)])

    # Processing
    print('-' * 50)
    print(f"Count cpu: {cpu_count()}")
    p_time_start = time.time()
    with Pool(cpu_count()) as p:
        p.map_async(
            divided_numbers,
            number,
            callback=callback
        )
        p.close()
        p.join()
    p_time_stop = time.time() - p_time_start
    print(f'Pool time: {p_time_stop:.4f} seconds')

    # Processing_2
    print('-' * 50)
    p_time_start = time.time()
    with Pool(cpu_count()) as p:
        for val in number:
            p.apply_async(divided_numbers, args=(val,))
        p.close()
        p.join()
    p_time_stop = time.time() - p_time_start
    print(f'Pool 2 time: {p_time_stop:.4f} seconds')

    # Processing_3
    print('-' * 50)
    prs = []
    p_time_start = time.time()
    for val in number:
        prs.append(Process(target=divided_numbers, args=(val,)))
        prs[-1].start()
    [val.join() for val in prs]
    p_time_stop = time.time() - p_time_start
    print(f'Process time: {p_time_stop:.4f} seconds')

    # Semaphore
    print('-' * 50)
    semaphore = Semaphore(cpu_count())
    prs = []
    p_time_start = time.time()
    for val in number:
        prs.append(Process(name=f'{number.index(val)}', target=sem_worker, args=(semaphore, val)))
        prs[-1].start()
    [p.join() for p in prs]
    p_time_stop = time.time() - p_time_start
    print(f'Semaphore time: {p_time_stop:.4f} seconds')

    return tuple(result_synchro)


if __name__ == '__main__':
    #
    a, b, c, d = factorize(128, 255, 99999, 10651060)

    assert a == a_
    assert b == b_
    assert c == c_
    assert d == d_
