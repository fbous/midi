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

## Install

Just create a link in a folder within your path
that points to the file `midi.py`.
For me e.g.:
```bash
cd ~/bin
ln -s ../workspace/midi/midi.py midi
```
(I have the source of this project in `~/workspace/midi/`
 and my `.bashrc` has something like
 `export PATH="$PATH":"$HOME"/bin`)
 
### Requirements
python 3.6 or higher


## Status

This is just a first draft so far
and some features, I envisioned,
are still missing
or do not work perfectly yet.
So check for a new version from time to time,
with a `git pull`.
