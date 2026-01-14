import math
from .helpers import vprint


RANGES = [(int(math.pow(2, i)), int(math.pow(2, i + 1))) for i in range(8)]

def range_info(diff):
    for l, u in RANGES:
        if l <= diff < u:
            bits_to_hide = int(math.log2(u - l + 1))
            return (l, u, bits_to_hide)
    return None

def embed_pair(p1, p2, bits, verbose):

    diff = abs(p1 - p2)
    info = range_info(diff)
    
    if not info:
        vprint(verbose, "Error: No valid range found for difference: {}".format(diff))
        return None

    l, u, bits_to_hide = info
    
    data = bits[:bits_to_hide]
    if not data:
        vprint(verbose, "Error: Not enough bits to hide")
        return None

    

def pvd_encrypt(input_image, message, key, verbose):
    '''
    Encrypts the message using PVD steganography.
    '''
    print(range_info(12))

pvd_encrypt(None, None, None, None)