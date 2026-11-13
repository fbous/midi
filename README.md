# midi

The MIDI version of Unix' `ascii`

Try either (in shell)
```bash
midi
```
or 
```bash
midi 440 C4 fis
```

Use `-c` to set a different concert pitch, e.g. `midi -c 443 A4`.

## Install

```bash
pipx install midi-ascii
```

Or just run the single file: `python3 midi.py`.

### Requirements
python 3.6 or higher


## Status

This is just a first draft so far
and some features, I envisioned,
are still missing
or do not work perfectly yet.
Upgrade from time to time with `pipx upgrade midi-ascii`.

## License

GPL-3.0-or-later — see [LICENSE](LICENSE).
