from base64 import b64encode, b64decode
from math import sin, pi, log, e, acos, asin, sqrt, cbrt
import random

encoding = 'utf-8'

def ln(x):
    return log(x, e)

def zarccos(x, z):
    return x ** (-z*x) * acos(x)

def cbrtzarcsin(x, z):
    return cbrt(2*x+z-1) * asin(2*x-1) + 0.6

def sqr(x):
    return x ** 2 - sqrt(x) * acos(x) + 1

def sqrt_and_arccos(x):
    return sqrt(x)*acos(x)-1

def cbrtarcsin(x):
    return cbrt(asin(2*x-1))

def cbrtarccos(x):
    return cbrt(acos(2*x-1))

def encode_triplex64(data: str) -> str:
    # 1. Base64
    b64 = b64encode(data.encode(encoding)).decode(encoding)
    unicodes = [ord(c) for c in b64]

    length = len(unicodes)

    # 2. seed (СИНХРОННЫЙ)
    seed = sum(map(int, str(length * 2142888)))
    random.seed(seed)

    # 3. normalisation
    lower = min(unicodes)
    unicodes = [x - lower for x in unicodes]

    # 4. encoding loop
    for pos in range(length):
        uni = unicodes[pos]

        dif2 = (pos * 2) / length
        dif = (pos+1) / length
        radians = (dif2 * 90 * pi) / 180
        uni += int(sin(radians) * 10)

        uni += int(ln((pos + 1) * 10) * 10)

        uni += int(zarccos(dif, length / 20) * 10)

        uni += random.randint(0, 100)

        uni += int(cbrtzarcsin(dif, 0.5)*10)
        uni += int(sqr(dif)*10)

        uni += int(sqrt_and_arccos(dif) * 25)
        uni += int(cbrtarcsin(dif) * 50)
        uni += int(cbrtarccos(dif) * 50)

        unicodes[pos] = uni

    lower2 = min(unicodes)
    unicodes = [uni - lower2 for uni in unicodes]

    encoded = ''.join(chr(x) for x in unicodes)
    return f'{oct(lower)[2:]}:{oct(lower2)[2:]}:{encoded}'


def decode_triplex64(encoded: str) -> str:
    # 1. split
    lower_oct, lower2_oct, data = encoded.split(":")
    lower = int(lower_oct, 8)
    lower2 = int(lower2_oct, 8)

    unicodes = [ord(c) + lower2 for c in data]
    length = len(unicodes)

    # 2. restore seed
    seed = sum(map(int, str(length * 2142888)))
    random.seed(seed)

    # 3. decoding loop
    for pos in range(length):
        dif2 = (pos * 2) / length
        dif = (pos + 1) / length
        radians = (dif2 * 90 * pi) / 180

        uni = unicodes[pos]

        # reverse order
        uni -= int(cbrtarccos(dif) * 50)
        uni -= int(cbrtarcsin(dif) * 50)
        uni -= int(sqrt_and_arccos(dif) * 25)
        uni -= int(sqr(dif) * 10)
        uni -= int(cbrtzarcsin(dif, 0.5) * 10)

        uni -= random.randint(0, 100)

        uni -= int(zarccos(dif, length / 20) * 10)
        uni -= int(ln((pos + 1) * 10) * 10)
        uni -= int(sin(radians) * 10)

        unicodes[pos] = uni

    # 4. restore base64 chars
    unicodes = [x + lower for x in unicodes]
    b64 = ''.join(chr(x) for x in unicodes)

    return b64decode(b64.encode(encoding)).decode(encoding)

