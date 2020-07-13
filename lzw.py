from functools import partial
import math

"""
    WIP - study material

    attempting to implement LZW to understand how it works
"""

# to do: improve compression rate

def compress(uncompressed): # take a bytearray, output an integer list
    max_size = 4096
    dictionary = {chr(i): i for i in range(256)} # self explanatory

    w = chr(uncompressed[0]) # first chara
    result = []
    for i in range(1, len(uncompressed)): # start reading
        c = chr(uncompressed[i]) # current chara
        wc = w + c # check for previous chain + current chara
        if wc in dictionary: # already in dict, we'll check for the next chara
            w = wc
        else:
            result.append(dictionary[w]) # add to output the previous chain
            if len(dictionary) < max_size:
                dictionary[wc] = len(dictionary) # add full chain to dict if not full
            w = c # previous chain set to current chara
    if len(w) > 0:
        result.append(dictionary[w]) # append the rest
    return result

def compress_file(i):
    with open(i, "rb") as fi:
        return compress(fi.read())

def compress_file_to(i, o):
    with open(i, "rb") as fi:
        with open(o, "wb") as fo:
            bit_size = 9
            max_size = 512
            size_limit = 12
            dictionary = {chr(i): i for i in range(max_size)}

            buf = "" # buffer to handle our output and its weird width
            w = None
            for uncompressed in iter(partial(fi.read, 1024), b''):
                for c in uncompressed:
                    if w is None:
                        w = chr(c)
                        continue
                    wc = w + chr(c)
                    if wc in dictionary:
                        w = wc
                    else:
                        buf = buf + "{0:b}".format(dictionary[w]).zfill(bit_size)
                        if len(buf) > 64:
                            fo.write(int(buf[0:64], 2).to_bytes(8, 'big'))
                            buf = buf[64:]
                        if len(dictionary) < max_size:
                            dictionary[wc] = len(dictionary)
                            if len(dictionary) == max_size:
                                if bit_size < size_limit:
                                    bit_size += 1
                                    max_size += max_size
                                else:
                                    bit_size = 9
                                    max_size = 512
                                    dictionary = {str([i]): i for i in range(max_size)}
                        w = chr(c)
            if len(w) > 0:
                buf = buf + "{0:b}".format(dictionary[w]).zfill(bit_size) # add the leftover
                while len(buf) % 8 != 0:
                    buf += "0" # padding
                l = ((len(buf) - 1) // 8) + 1
                fo.write(int(buf, 2).to_bytes(l, 'big')) # and write

def decompress(compressed): # take an integer list (first element being the bit size), output a bytearray
    max_size = 4096
    dictionary = [chr(i) for i in range(256)]

    result = bytearray()
    entry = ""
    w = ""
    for c in compressed:
        if c < len(dictionary):
            entry = dictionary[c]
        elif c == len(dictionary):
            entry = w + w[0]
        else:
            raise ValueError('Bad compressed c: %s' % c)
        for e in entry: result.append(ord(e))
        if len(w) > 0 and len(dictionary) < max_size:
            dictionary.append(w + entry[0])
        w = entry
    return result

def decompress_to_file(o, compressed):
    with open(o, "wb") as fo:
        return fo.write(decompress(compressed))

def decompress_file_to(i, o):
    with open(i, "rb") as fi:
        with open(o, "wb") as fo:
            bit_size = 9
            max_size = 512
            size_limit = 12
            dictionary = {i: chr(i) for i in range(max_size)}

            result = bytearray()
            entry = ""
            w = ""

            buf = ""
            for chunk in iter(partial(fi.read, 64), b''):
                buf = buf + "{0:b}".format(int.from_bytes(chunk, 'big')).zfill(len(chunk)*8) # add to our buffer
                while len(buf) >= bit_size:
                    c = int(buf[:bit_size], 2)
                    buf = buf[bit_size:]
                    if c in dictionary:
                        entry = dictionary[c]
                    elif c == len(dictionary):
                        entry = w + w[0]
                    else:
                        raise ValueError('Bad compressed c: %s' % c)
                    for e in entry: result.append(ord(e))
                    if len(w) > 0 and len(dictionary) < max_size:
                        dictionary[len(dictionary)] = w + chr(entry[0])
                        if len(dictionary) == max_size:
                            if bit_size < size_limit:
                                bit_size += 1
                                max_size += max_size
                            else:
                                bit_size = 9
                                max_size = 512
                                dictionary = {i: [i] for i in range(max_size)}
                    w = entry
                fo.write(result)
                result = bytearray()

if __name__ == "__main__":
    with open("in.txt", "w") as f:
        f.write("Hello world !!\nThis is a test to study LZW algorithm!\nabcdefghijklmnopqrstuvwxyz\n123456789\n987654321\n0000")
    print("Compressing...")
    compress_file_to("in.odt", "compressed")
    print("Decompressing...")
    decompress_file_to("compressed", "out.odt")
    print("Done")

    #print(decompress(compress("hello world!!".encode('ascii'))))