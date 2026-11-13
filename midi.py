#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Print a list of midi pitches or search for one."""

import math
import re
import unicodedata
from argparse import ArgumentParser
from functools import reduce
from itertools import starmap


SEMIS = [
    ['C'],
    ['C#', 'D\u266d'],
    ['D'],
    ['D#', 'E\u266d'],
    ['E'],
    ['F'],
    ['F#', 'G\u266d'],
    ['G'],
    ['G#', 'A\u266d'],
    ['A'],
    ['A#', 'B\u266d'],
    ['B']
]

GERMAN = [
    ['C'],
    ['Cis', 'Des'],
    ['D'],
    ['Dis', 'Es'],
    ['E'],
    ['F'],
    ['Fis', 'Ges'],
    ['G'],
    ['Gis', 'As'],
    ['A'],
    ['Ais', 'B'],
    ['H']
]

SOLFEGE = [
    ['Do'],
    ['Do#', 'R\u00e9\u266d'],
    ['R\u00e9'],
    ['R\u00e9#', 'Mi\u266d'],
    ['Mi'],
    ['Fa'],
    ['Fa#', 'Sol\u266d'],
    ['Sol'],
    ['Sol#', 'La\u266d'],
    ['La'],
    ['La#', 'Si\u266d'],
    ['Si']
]

SUB = ['\u2080', '\u2081', '\u2082', '\u2083', '\u2084',
       '\u2085', '\u2086', '\u2087', '\u2088', '\u2089']

SUP = ['\u2070', '\u00b9', '\u00b2', '\u00b3', '\u2074',
       '\u2075', '\u2076', '\u2077', '\u2078', '\u2079']

CONCERT = 440.


def short_info(m):
    name, *_ = spn(m)
    f = freq(m)
    if m < 36:
        return f"{m:4d} {name:>4s} {f:>5.2f}  "
    if m < 84:
        return f"{m:4d} {name:>3s} {f:>5.1f}  "
    if m < 108:
        return f"{m:4d} {name:>3s} {f:>4.0f}  "
    return f"{m:4d} {name:>3s} {f:>5.0f}"


def freq(m):
    return CONCERT * 2. ** ((m - 69) / 12.)


def midi(f):
    m_ = 12 * math.log2(f / CONCERT) + 69
    m = int(round(m_))
    if m < 0 or m >= 128:
        raise ValueError
    cents = int(round(100 * (m_ - m)))
    return m, cents


def spn(m):
    octave, semi = divmod(m - 12, 12)
    return map(lambda x: f"{x}{octave}", SEMIS[semi])


def ger(m):
    if m >= 48:
        octave, semi = divmod(m - 48, 12)
        primes = octave * "'" if octave <= 3 else SUP[octave]
        return map(lambda x: x.lower() + primes, GERMAN[semi])
    if m >= 36:
        semi = m % 12
        return GERMAN[semi]

    return ""


def solfege(m):
    # SPN octaves (middle C is Do4), not the Franco-Belgian Do3
    octave, semi = divmod(m - 12, 12)
    return [f"{x}{octave}" for x in SOLFEGE[semi]]


def fold(s):
    # case- and accent-insensitive, so "re3" finds "Ré3"
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


def catch(*exceptions, cont=lambda x: []):
    def decorator(fn):
        def fn_(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exceptions as e:
                return cont(e)
        return fn_
    return decorator


def parse_f(s: str):
    s = s.upper()
    if s.endswith("HZ"):
        s = s[:-2]
    if s.endswith("K"):
        return 1000 * float(s[:-1])
    return float(s)


def parse_m(s: str):
    m = int(s)
    if 0 <= m < 128:
        return m
    raise ValueError


def matches(key, names):
    return reduce(lambda a, n: a or key in n, names, False)


@catch(ValueError)
def find_frequency(key):
    f = parse_f(key)
    m, c = midi(f)
    return [(f"Frequency {key}:", m, c, f, spn(m), ger(m))]


@catch(ValueError)
def find_midi(key):
    m = parse_m(key)
    return [(f"Midi pitch {key}:", m, 0, freq(m), spn(m), ger(m))]


def find_name(key):
    # a "b" after a letter is a flat: "Bb4", "Eb", "mib4"; no note name has one
    key = re.sub(r"(?<=[^\W\d_])b", "\u266d", key)
    for m in range(128):
        names = list(spn(m))
        if matches(key, names):
            yield (f"SPN name {key}:", m, 0, freq(m), names, ger(m))
    for m in range(128):
        germans = list(ger(m))
        if matches(key, germans):
            yield (f"German name {key}:", m, 0, freq(m), spn(m), germans)
    k = fold(key)
    for m in range(128):
        names = [fold(n) for n in solfege(m)]
        if k in names or k in [n.rstrip("-0123456789") for n in names]:
            yield (f"Solf\u00e8ge name {key}:", m, 0, freq(m), spn(m), ger(m))


def find(key):
    def find_(finder):
        results = finder(key)
        return "\n".join(starmap(summarize, results))
    return find_


def summarize(header, m, cents, f, name, german):
    m_ = f"MIDI pitch: {m}"
    if cents:
        m_ += f" + {cents} cents"
    return "\n  ".join((
        header, m_,
        f"Frequency: {f:.1f} Hz",
        f"Scientific pitch notation: {' / '.join(name)}",
        f"German pitch name: {' / '.join(german)}",
        f"Solf\u00e8ge pitch name: {' / '.join(solfege(m))}",
    ))


def print_long(key):
    print("\n".join(filter(bool, map(find(key), [
        find_frequency,
        find_midi,
        find_name,
    ]))))


def print_table():
    print("MIDI  SPN  FREQ  MIDI SPN  FREQ  MIDI SPN  FREQ  "
          "MIDI SPN FREQ  MIDI SPN  FREQ")
    columns = 24
    for c in range(12, columns + 12):
        col = (short_info(m) for m in range(c, 128, columns))
        print("".join(col))


def get_args():
    parser = ArgumentParser(
        description=__doc__
    )
    parser.add_argument("terms", nargs="*", help="Search terms")
    parser.add_argument("-c", "--concert", default=440., type=float,
                        help="Concert pitch (default 440Hz)")
    return vars(parser.parse_args())


def main(terms, concert):
    global CONCERT
    CONCERT = concert
    if terms:
        for arg in terms:
            print_long(arg)
    else:
        print_table()


def cli():
    main(**get_args())


if __name__ == "__main__":
    cli()
