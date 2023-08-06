import requests

from requests_throttler import HostBasedThrottler


def main():
    hbt = HostBasedThrottler(name='base-throttler', delay=1.5)
    r = requests.Request(method='GET', url='http://www.google.com')
    reqs = [r for i in range(0, 10)]

    with bt:
        throttled_requests = bt.multi_submit(reqs)

    for r in throttled_requests:
        print r.response

    print "Success: {s}, Failures: {f}".format(s=bt.successes, f=bt.failures)


if __name__ == '__main__':
    main()
