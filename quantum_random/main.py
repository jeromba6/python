#!/bin/env python3

import json
from unittest import result
import requests
import math

# print(math.log(125,5))
# exit()

def qrandom(data_type: str = 'hex16',array_length: int = 1, block_size: int = 1) -> dict:
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

def qrandom_int(max_val: int = 10, array_length: int = 1 ) -> list :
    max_array_length = 1024
    max_blocks = 1024
    
    fits=int(math.log(2**max_blocks,max_val))-1
    entries_to_get = array_lenght // fits + 1
    nr_passes = entries_to_get // max_blocks + 1
    results_int = []
    for _ in range(nr_passes):
        array_length_to_get = min(max_array_length, (array_lenght - len(results_int)) // fits + 1)
        results = qrandom(array_length=array_length_to_get,block_size=max_blocks)
        print(array_length_to_get, end=' ')
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
    print()
    return results_int

# print (qrandom('uint8'))
# print (qrandom('uint16'))
# print (qrandom())
max_val = 6
array_lenght = 600_000
int_list = qrandom_int(max_val = max_val, array_length = array_lenght)
frequency = {}
for index in range(max_val):
    frequency[index] = 0
for index in int_list:
    frequency[index] += 1
print(f'Average: {array_lenght // max_val}')
print (frequency)

