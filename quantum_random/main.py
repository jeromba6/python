#!/bin/env python3

import json
from re import A
from unittest import result
import requests
import math
import random
import copy

# print(math.log(125,5))
# exit()

def qrandom_get(data_type: str = 'hex16',array_length: int = 1, block_size: int = 1) -> dict:
    """
    Data type, the data type must be ‘uint8’ (returns integers between 0–255), ‘uint16’ (returns integers between 0–65535) or ‘hex16’ (returns hexadecimal characters between 00–ff).
    Array length, the length of the array to return. Must be between 1–1024.
    Block size, only needed for ‘hex16’ data type. Sets the length of each block. Must be between 1–1024.

    Ouput will be an dict

    Documentation:
    https://qrng.anu.edu.au/contact/api-documentation/
    """
    data_types = ('uint8','uint16','hex16')
    if not data_type in data_types:
        raise Exception(f'data_type should contain 1 of ({",".join(data_types)}) currently it contains: {data_type}')
    if not isinstance(array_length,int) or array_length < 1 or array_length > 1024:
        raise Exception(f'Variable array_length should contain an integer with following conditions > 0 and < 1025')
    if data_type == 'hex16':
        if not isinstance(block_size,int) or block_size < 1 or block_size > 1024:
            raise Exception(f'Variable block_size should contain an integer with following conditions > 0 and < 1025')
    else:
        block_size=1
    url = f'https://qrng.anu.edu.au/API/jsonI.php?type={data_type}&length={array_length}&size={block_size}'
    res = requests.get(url=url)
    if res.status_code != 200:
        raise Exception(f'Backend did not response as expected with status_code 200 but with: {res.status_code}')
    res_json = json.loads(res.text)
    if res_json['success']:
        return(res_json)
    raise Exception(f'Response from backend failed with following json"{res_json}"')

def qrandomint_list(max_val: int = 10, array_length: int = 1 ) -> list :
    max_array_length = 1024
    max_blocks = 1024
    
    fits=int(math.log(2**max_blocks,max_val))-1
    entries_to_get = array_length // fits + 1
    nr_passes = entries_to_get // max_blocks + 1
    results_int = []
    for _ in range(nr_passes):
        array_length_to_get = min(max_array_length, (array_length - len(results_int)) // fits + 1)
        results = qrandom_get(array_length=array_length_to_get,block_size=max_blocks)
        for result_hex in results['data']:
            rand_base = int(result_hex,16) // max_val
            for _ in range(fits):
                results_int.append(rand_base % max_val)
                rand_base = rand_base // max_val
                if len(results_int) == array_length:
                    break
            else:
                continue
            break
        else:
            continue
        break
    return results_int

def qrandom_list(array_length: int = 1 ) -> list :
    max_val = 10 ** 20
    max_array_length = 1024
    max_blocks = 1024
    
    fits=int(math.log(2**max_blocks,max_val))-1
    entries_to_get = array_length // fits + 1
    nr_passes = entries_to_get // max_blocks + 1
    results_rand = []
    for _ in range(nr_passes):
        array_length_to_get = min(max_array_length, (array_length - len(results_rand)) // fits + 1)
        results = qrandom_get(array_length=array_length_to_get,block_size=max_blocks)
        for result_hex in results['data']:
            rand_base = int(result_hex,16) // max_val
            for _ in range(fits):
                results_rand.append((rand_base % max_val)/max_val)
                rand_base = rand_base // max_val
                if len(results_rand) == array_length:
                    break
            else:
                continue
            break
        else:
            continue
        break
    return results_rand

def qrandom() -> float:
    return qrandom_list(array_length=1)[0]

def qrandint(a: int,b: int) -> int:
    return a + qrandomint_list(b - a + 1)[0]

def qgetrandbits_list(k: int, array_length: int = 1) -> list:
    return qrandomint_list(2 ** k, array_length = array_length)

def qgetrandbits(k: int) -> int:
    return qgetrandbits_list(k, array_length = 1)[0]

def qchoice_list(seq: list, array_length: int = 1):
    result = []
    for item in qrandomint_list(len(seq),array_length=array_length):
        result.append(seq[item])
    return result

def qchoice(seq: list):
    return qchoice_list(seq = seq, array_length = 1)[0]

def qchoices(seq: list, weights: list = None, k: int = 1) -> list:
    if weights is None:
        weights = [1] * len(seq)
    weighted_seq = []
    for item in range(len(seq)):
        weighted_seq.extend([seq[item]]*weights[item])
    return qchoice_list(weighted_seq, k)

def qshuffle(seq: list) -> list:
    seq_work = copy.deepcopy(seq)
    items = qrandom_list(array_length=len(seq))
    for item in range(len(seq)):
        pick = int(items[item]*len(seq_work))
        seq[item] = seq_work.pop(pick)

def qsample(seq: list, k: int=1 ) -> list:
    seq_work = copy.deepcopy(seq)
    items = qrandom_list(array_length = k)
    result = []
    for item in items:
        pick = int(item*len(seq_work))
        result.append(seq_work.pop(pick))  
    return result
        
def quniform_list(start: float, end: float, array_length: int = 1) -> list:
    items = qrandom_list(array_length = array_length)
    result = []
    for item in items:
        result.append(start + (end - start) * item)
    return result

def quniform(start: float, end: float) -> float:
    return quniform_list(start = start, end = end, array_length = 1)[0]

# print (qrandom_get('uint8'))
# print (qrandom_get('uint16'))
# print (qrandom_get())
# max_val = 1_0
# array_lenght = 1000
# int_list = qrandom_int_list(max_val = max_val, array_length = array_lenght)
# frequency = {}
# for index in range(max_val):
#     frequency[index] = 0
# for index in int_list:
#     frequency[index] += 1
# print(f'Average: {array_lenght // max_val}')
# print (frequency)

# r = random.random()
# print(r, len(str(r)))

# r = qrandom()
# print(r, len(str(r)))

# r = random.randint(0,3)
# print(r)

# r = qrandint(0,3)
# print(r)

r = [1,2,3,4,5,6,7,8,9]
random.shuffle(r)
print(r)

rs = quniform(1.5,7g)
print(r)
print(rs)