#!/usr/bin/env python3
from Crypto.Hash import keccak
from typing import Tuple
import argparse
from csv import DictReader
from pathlib import Path
import sys
import re 

FUNC_NAME_RE = re.compile(r"([a-zA-Z_]+)\(")
FUNC_ARGS_RE = re.compile(r"[a-zA-Z_]+\(\s*(.+)\s*\)")

_UINT_STEPS = [i for i in range(257) if i % 8 == 0 and i > 0]
UINT_TYPES = ["uint" + str(i) for i in _UINT_STEPS]
INT_TYPES = ["int" + str(i) for i in _UINT_STEPS]
BYTES_TYPES = ["bytes" + str(i) for i in range(33) if i > 0]
FIXED_UNFIXED_TYPES = []
for x in _UINT_STEPS:
    for y in _UINT_STEPS:
        FIXED_UNFIXED_TYPES.append(f"fixed{str(x)}x{str(y)}")
        FIXED_UNFIXED_TYPES.append(f"ufixed{str(x)}x{str(y)}")

# function type not handled yet
ELEM_TYPES = ["address", "bool"] + UINT_TYPES + INT_TYPES + BYTES_TYPES
NON_FIXED_TYPES = ["bytes", "string"] + [x + "[]" for x in ELEM_TYPES]

TYPES = ELEM_TYPES + NON_FIXED_TYPES + FIXED_UNFIXED_TYPES

TYPE_ALIASES = {
        "int": "int256",
        "uint": "uint256",
        "fixed": "fixed126x18",
        "ufixed": "ufixed128X18"
}
# handle fixed array and tuple dynamically

def hash(funcstr):
    k = keccak.new(digest_bits=256)
    k.update(funcstr.encode())
    return "0x" + k.hexdigest()[:8]

def dealias(func_type):
    arr_t = { k:k+"[]" for (k,v) in TYPE_ALIASES.items()}
    arr_t.update(TYPE_ALIASES)
    if func_type in arr_t.keys():
        return arr_t[func_type]
    for t in TYPE_ALIASES.keys():
        if func_type.startswith(t + "["):
            num = func_type.split("[")[1].split("]")[0]
            return TYPE_ALIASES[t] + "[" + num + "]"

    # need tuples
    return func_type

def sigify(funcstr) -> Tuple[bool,str]:
    m = FUNC_NAME_RE.match(funcstr)
    reason_or_sig = ""
    status = False
    if m:
        name = m.group(1)
        m = FUNC_ARGS_RE.match(funcstr)
        if m:
            func_types = []
            _func_args = m.group(1).strip()
            func_args = _func_args.split(",")
            for func_arg in func_args:
                # split on space,
                func_arg_parts = func_arg.strip().split(" ")
                func_type = func_arg_parts[0].lower().strip()
                func_type = dealias(func_type)
                # check if valid type
                if func_type in TYPES:
                    func_types.append(func_type)
                else:
                    x = 1+1
                    #print(f"Bad type {func_type} in {func_arg} | {_func_args} | {funcstr}")
            # doesn't handle nested arrays
            # doesn't handle struct references
            # doesn't handle slice type
            if len(func_args) == len(func_types):
                reason_or_sig = name + "(" + ",".join(func_types).strip(",") + ")"
                status = True
        else:
            reason_or_sig = "Could not extract function args"
    else:
        reason_or_sig = "Could not capture function name"

    return (status, reason_or_sig)


def parse(file_path):
    fd = Path(file_path).open(newline='')
    reader = DictReader(fd)
    for row in reader:
        funcs = [func.strip("\"") for func in row["f0_"].split(';') if func]
        sigs = []
        invalid = []
        for func in funcs:
            status, sig = sigify(func)
            if not status:
                # func is original funcstr and sig is failure reason
                invalid.append((func, sig))
            else:
                sigs.append(sig)
                
        for sig in list(set(sigs)):
            print(f"{hash(sig)} => {sig}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="csv file path")
    args = parser.parse_args()
    if not Path(args.file):
        print(f"[!] Cannot find file: {args.file}")
        sys.exit(1)
    parse(args.file)
