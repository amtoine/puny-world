## overworld
> metadata file [here][metadata file]

![tileset](assets/punyworld-overworld-tileset.png)

## characters
#### Archer (green)
![](assets/puny-characters/Archer-Green.png)
---

#### Soldier (yellow)
![](assets/puny-characters/Soldier-Yellow.png)
---

#### Warrior (red)
![](assets/puny-characters/Warrior-Red.png)
---

#### Orc Peon (red)
![](assets/puny-characters/Orc-Peon-Red.png)
---

#### Mage (cyan)
![](assets/puny-characters/Mage-Cyan.png)
---

#### Archer (purple)
![](assets/puny-characters/Archer-Purple.png)
---

#### Human Worker (red)
![](assets/puny-characters/Human-Worker-Red.png)
---

#### Soldier (blue)
![](assets/puny-characters/Soldier-Blue.png)
---

#### Mage (red)
![](assets/puny-characters/Mage-Red.png)
---

#### Human Soldier (cyan)
![](assets/puny-characters/Human-Soldier-Cyan.png)
---

#### Slime
![](assets/puny-characters/Slime.png)
---

#### Human Worker (cyan)
![](assets/puny-characters/Human-Worker-Cyan.png)
---

#### Character Base
![](assets/puny-characters/Character-Base.png)
---

#### Orc Soldier (red)
![](assets/puny-characters/Orc-Soldier-Red.png)
---

#### Warrior (blue)
![](assets/puny-characters/Warrior-Blue.png)
---

#### Orc Grunt
![](assets/puny-characters/Orc-Grunt.png)
---

#### Soldier (red)
![](assets/puny-characters/Soldier-Red.png)
---

#### Orc Soldier (cyan)
![](assets/puny-characters/Orc-Soldier-Cyan.png)
---

#### Orc Peon (cyan)
![](assets/puny-characters/Orc-Peon-Cyan.png)
---

#### Human Soldier (red)
![](assets/puny-characters/Human-Soldier-Red.png)
---

## extract metadata from original
```nushell
let puny = open metadata/punyworld-overworld-tiles.tsx | from xml | {
    image: ($in.content.0.attributes | into int width height),
    animations: (
        $in.content | reject 0 71 | each { {
            id: ($in.attributes.id | into int),
            animation: (
                $in.content.content.0.attributes
                    | rename --column { tileid: "id" }
                    | into int id duration
            ),
        }}
    ),
    wangset: $in.content.71.content,
}
```

and `$puny.animations` has been added to the [metadata file].

[metadata file]: metadata/punyworld-overworld-tiles.nuon
