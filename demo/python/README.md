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

### wave function collapse
Generate random maps with the _Wave Function Collapse_ algorithm.

```shell
python wave_function_collapse.py
```

- _space_ to run another generation

```nushell
let ns = seq 1 20
const NB_MEASUREMENTS = 10

let res_no_entropy = $ns | each { |n|
    python wave_function_collapse.py ...[
        -W $n
        -H $n
        -s -1
        -I
        --use-information-entropy
        -A
        --nb-measurements $NB_MEASUREMENTS
    ]
        | lines
        | parse "retries: {r}, t: {t}"
}

let res_entropy = $ns | each { |n|
    python wave_function_collapse.py ...[
        -W $n
        -H $n
        -s -1
        -I
        -A
        --nb-measurements $NB_MEASUREMENTS
    ]
        | lines
        | parse "retries: {r}, t: {t}"
}
```
```nushell
const NB_NS_IN_SEC = 1e9

[
    {
        name: "\\#options",
        points: ($res_no_entropy | zip $ns | each {{
            x: $in.1,
            y: ($in.0.r | into int | math avg),
            e: ($in.0.r | into int | math stddev),
        }}),
    },
    {
        name: "entropy",
        points: ($res_entropy | zip $ns | each {{
            x: $in.1,
            y: ($in.0.r | into int | math avg),
            e: ($in.0.r | into int | math stddev),
        }}),
    },
] | to json | gplt plot $in ...[
    --use-tex
    --x-label "$n$"
    --y-label "\\#retries"
    --title "number of WFC retries on a map of size $n \\times n$"
    --font ({ size: 30, family: serif, sans-serif: Helvetica } | to json)
    --fullscreen
]

[
    {
        name: "\\#options",
        points: ($res_no_entropy | zip $ns | each {{
            x: $in.1,
            y: ($in.0.t | into int | math avg | $in / $NB_NS_IN_SEC),
            e: ($in.0.t | into float | math stddev | $in / $NB_NS_IN_SEC),
        }}),
    },
    {
        name: "entropy",
        points: ($res_entropy | zip $ns | each {{
            x: $in.1,
            y: ($in.0.t | into int | math avg | $in / $NB_NS_IN_SEC),
            e: ($in.0.t | into float | math stddev | $in / $NB_NS_IN_SEC),
        }}),
    },
] | to json | gplt plot $in ...[
    --use-tex
    --x-label "$n$"
    --y-label "$t$ (in s)"
    --title "time for WFC to generate a map of size $n \\times n$"
    --font ({ size: 30, family: serif, sans-serif: Helvetica } | to json)
    --fullscreen
]
```

### perlin noise
```nushell
const SEED = 123

const NOISE = {
    terrain: [
        [amplitude, octaves];

        [1.000,     1],
        [0.500,     6],
        [0.250,     12],
    ],
    forest: [
        [amplitude, octaves];

        [1.000,     1],
        [0.500,     3],
        [0.250,     12],
    ]
}

const LAND_TYPES = { "ROCK": 0.1, "GRASS": 0.0, "WATER": "-inf" }

python perlin.py ...[
    -W 40
    -H 20
    -s 32
    -f 60
    --seed $SEED
    --terrain-noise ($NOISE.terrain | to json)
    --biome-noise ($NOISE.forest | to json)
    --land-types ($LAND_TYPES | to json)
]
```
