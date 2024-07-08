## running the examples
- create a Python virtual environment and activate it
- install the dependencies
```shell
pip install -r requirements.txt
```

all the examples use a very simple library i've written, `tileset.py`, which provides a few types and functions.

### neighbours
Shows tiles and their possible neighbours.

```shell
python neighbours.py
```
- _space_ and _shift + space_ will cycle through all the tiles
- north, west, east and south neighbours will be shown next to the tile
- _k_ and _shift + k_ will cycle the north neighbours
- _l_ and _shift + l_ will cycle the east neighbours
- _j_ and _shift + j_ will cycle the south neighbours
- _h_ and _shift + h_ will cycle the west neighbours

> **Note**
>
> i haven't seen any issues

### animations
Shows all tile animation in one window.

```shell
python animation.py
```

### characters
Show the animations of all the characters, one by one.

```shell
python characters.py
```
- _space_ and _shift + space_ will cycle through the characters

> **Important**
>
> - the _slime_ is missing
