from functools import partial
import math

"""
    WIP - study material

    attempting to implement LZW to understand how it works
"""

def compress(uncompressed): # take a bytearray, output an integer list
    dictionary = {chr(i): i for i in range(256)} # self explanatory

    w = ""
    result = []
    for uc in uncompressed: # start reading
        c = chr(uc) # current chara
        wc = w + c # check for previous chain + current chara
        if wc in dictionary: # already in dict, we'll check for the next chara
            w = wc
        else:
            result.append(dictionary[w]) # add to output the previous chain
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
            dictionary = {chr(i): i for i in range(256)}
            ratio_in = 0
            ratio_out = 0

            buf = "" # buffer to handle our output and its weird width
            w = ""
            for uncompressed in iter(partial(fi.read, 1024), b''):
                for uc in uncompressed:
                    ratio_in += 1
                    c = chr(uc)
                    wc = w + c
                    if wc in dictionary:
                        w = wc
                    else:
                        buf += "{0:b}".format(dictionary[w]).zfill(bit_size) # fill the buffer with our bits

                        if len(buf) > 64: # write 64 by 64 
                            fo.write(int(buf[0:64], 2).to_bytes(8, 'big'))
                            buf = buf[64:] # remove what we wrote
                            ratio_out += 8
                        if len(dictionary) < max_size:
                            dictionary[wc] = len(dictionary)
                            if len(dictionary) == max_size:
                                if bit_size < size_limit:
                                    bit_size += 1
                                    max_size += max_size
                        w = c
            if w != "":
                buf += "{0:b}".format(dictionary[w]).zfill(bit_size) # add the leftover
            if buf != "":
                while len(buf) % 8 != 0:
                    buf += "0" # padding
                l = ((len(buf) - 1) // 8) + 1
                ratio_out += l
                fo.write(int(buf, 2).to_bytes(l, 'big')) # and write
            print(ratio_in, "bytes in,", ratio_out, "bytes out")
            print("Compression Ratio", ratio_out*100/ratio_in, "%")

def decompress(compressed): # take an integer list (first element being the bit size), output a bytearray
    dictionary = {i: chr(i) for i in range(256)}

    result = bytearray()
    entry = ""
    w = ""
    for c in compressed:
        if c in dictionary:
            entry = dictionary[c]
        elif c == len(dictionary):
            entry = w + w[0]
        else:
            raise ValueError('Bad compressed c: %s' % c)
        for e in entry: result.append(ord(e))
        if w != "":
            dictionary[len(dictionary)] = w + entry[0]
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
            dictionary = {i: chr(i) for i in range(256)}

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
                    if w != "" and len(dictionary) < max_size:
                        dictionary[len(dictionary)] = w + entry[0]
                        if len(dictionary) == max_size - 1:
                            if bit_size < size_limit:
                                bit_size += 1
                                max_size += max_size
                    w = entry
                fo.write(result)
                result = bytearray()

if __name__ == "__main__":
    with open("in.txt", "w") as f:
        f.write("Hello world !!\nThis is a test to study LZW algorithm!\nThisisatesttostudyLZWalgorithm\n0101010101\n10101010101\n0000\n")
    print("Compressing...")
    compress_file_to("in.txt", "compressed")
    print("Decompressing...")
    decompress_file_to("compressed", "out.txt")
    print("Done")