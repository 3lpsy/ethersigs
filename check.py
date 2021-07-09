#!/usr/bin/env python3
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys
import json

def check_hash(hash_):
    arg = hash_
    real = ""
    if "=" in hash_:
        arg = hash_.split(" ")[0]
        real = hash_.split(" ")[2]
    url = "https://www.4byte.directory/api/v1/signatures/?hex_signature=" + arg
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        return (hash_, int(data["count"]), real)
    return (hash_, -1, real)


def result(data):
    count = data[1]
    hash_ = data[0]
    real = data[2]
    if count == 0:
        print("New:", hash_, count, real)

# infile in hashesmap
def run(infile):
    hashmapstrs = [h.strip() for h in Path(infile).read_text().split("\n")]
    with ThreadPoolExecutor() as ex:
        futures = []
        for hash_ in hashmapstrs:
            future = ex.submit(check_hash, hash_)
            futures.append(future)
        for future in as_completed(futures):
            try:
                res = future.result()
                result(res)
            except requests.ConnectionError:
                print("Connect erro...")

run(sys.argv[1])

