from functools import partial
import math

"""
    WIP - study material

    attempting to implement LZW to understand how it works
"""


def compress(uncompressed, bit_size = 9): # take a bitearray, output an integer list
    if bit_size < 9: raise ValueError('Invalid bit size' % bit_size )
    max_size = int(math.pow(2, bit_size))
    dictionary = {str([i]): i for i in range(256)}

    w = [uncompressed[0]]
    result = []
    for i in range(1, len(uncompressed)):
        c = uncompressed[i]
        wc = w + [c]
        if str(wc) in dictionary:
            w = wc
        else:
            result.append(dictionary[str(w)])
            if len(dictionary) < max_size:
                dictionary[str(wc)] = len(dictionary)
            w = [c]
    if len(w) > 0:
        result.append(dictionary[str(w)])
    result.insert(0, bit_size)
    return result

def compress_file(i, o, bit_size = 9): 
    with open(i, "rb") as fi:
        if bit_size < 9: raise ValueError('Invalid bit size' % bit_size )
        max_size = int(math.pow(2, bit_size))
        dictionary = {str([i]): i for i in range(256)}

        w = None
        result = []
        for uncompressed in iter(partial(fi.read, 1024), b''):
            for c in uncompressed:
                if w is None:
                    w = [c]
                    continue
                wc = w + [c]
                if str(wc) in dictionary:
                    w = wc
                else:
                    result.append(dictionary[str(w)])
                    if len(dictionary) < max_size:
                        dictionary[str(wc)] = len(dictionary)
                    w = [c]
        if len(w) > 0:
            result.append(dictionary[str(w)])

    mul = 1
    while (mul * 8) % bit_size != 0:
        mul += 1

    buf = 0
    buf_pos = 0

    with open(o, "wb") as fo:
        fo.write(bit_size.to_bytes(1, byteorder='big'))
        for e in result:
            buf = (buf << bit_size) + e
            buf_pos += 1
            if buf_pos== mul - 1:
                buf_pos = 0
                fo.write(buf.to_bytes(mul, byteorder='big'))
                buf = 0
        if buf_pos != 0:
            fo.write(buf.to_bytes(1 + (buf_pos * bit_size) // 8, byteorder='big'))

def decompress(compressed): # take an integer list (first element being the bit size), output a bytearray
    bit_size = compressed.pop(0)
    if bit_size < 9: raise ValueError('Invalid bit size' % bit_size )
    max_size = int(math.pow(2, bit_size))
    dictionary = {i: [i] for i in range(256)}

    result = bytearray()
    entry = []
    w = []
    for c in compressed:
        if c in dictionary:
            entry = dictionary[c]
        elif c == len(dictionary):
            entry = w + [w[0]]
        else:
            raise ValueError('Bad compressed k: %s' % c)
        for e in entry: result.append(e)
        if len(w) > 0:
            dictionary[len(dictionary)] = w + [entry[0]]
        w = entry
    return result

def decompress_file(i, o):
    with open(i, "rb") as fi:
        with open(o, "wb") as fo:
            bit_size = int.from_bytes(fi.read(1), 'big')
            if bit_size < 9: raise ValueError('Invalid bit size' % bit_size )
            max_size = int(math.pow(2, bit_size))
            dictionary = {i: [i] for i in range(256)}

            mul = 1
            while (mul * 8) % bit_size != 0:
                mul += 1

            result = bytearray()
            entry = []
            w = []

            for chunk in iter(partial(fi.read, mul), b''): # might not be the most efficient?
                buf = int.from_bytes(chunk, 'big')
                compressed = []
                for i in range(1, len(chunk)):
                    compressed.insert(0, buf % max_size)
                    buf = buf >> bit_size
                for c in compressed:
                    if c in dictionary:
                        entry = dictionary[c]
                    elif c == len(dictionary):
                        entry = w + [w[0]]
                    else:
                        raise ValueError('Bad compressed k: %s' % c)
                    for e in entry: result.append(e)
                    if len(w) > 0:
                        dictionary[len(dictionary)] = w + [entry[0]]
                    w = entry
                fo.write(result)
                result = bytearray()


if __name__ == "__main__":
    with open("in.txt", "w") as f:
        f.write("Hello world !!\nThis is a test to study LZW algorithm!")
    print("Compressing...")
    compress_file("in.txt", "compressed", 9)
    print("Decompressing...")
    decompress_file("compressed", "out.txt")
    print("Done")