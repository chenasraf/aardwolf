# SpellRotation Aardwolf Plugin

This plugin lets you switch between various spells to use with SnD or your other aliases.

A typical rotation set might look like:

- `main` - The main spell
- `aoe` - An AOE spell
- `phys` - A physical spell for enemies resistent to elemental damage

## Installation

1. Download [SpellRotation.xml](SpellRotation.xml), place it somewhere it wouldn't move (e.g. the
   plugins directory in your MUSHClient installation)
1. Open Plugin Manager (Ctrl+Shift+P)
1. Add `SpellRotation.xml` via the plugin manager

## Usage

1. To **set a rotation**, use `ks set <rotation name> <commands` e.g,
   ```
   ks set main cast balefire`
   ks set aoe cast 'fire breath';;cast 'balefire'
   ```
1. To **see a rotation command list**, use `ks get <rotation name>`
1. Attacking is done by using `kp` without a taregt, or `kp <target>`.
1. You can switch to a rotation by using `ks switch <rotation name>`. To switch mid-battle, you can
use `kp <rotation name>`, which will switch rotation and also attack the active target at the same
time. e.g. `kp aoe`
<!-- 1. `kkp` is a utility alias that will execute the main rotation on the current target set by SnD,
   and fill the Command Input on the main window with the main attack command, so you can keep
   pressing <kbd>Enter</kbd> to attack, without accidentally attacking a different target of the
same name if it dies while you spam the command. -->

### Aliases/Commands

Use `ks help` to see this list at any time in the game.

```
SpellRotation
--------------------------------------------------------------
kp [target]           Execute current rotation
kp [name]             Switch to rotation [name] and execute
ks get <name>         Get rotation
ks <name> <cmds>      Set rotation
ks switch <name>      Switch to rotation
ks list               List all rotations and their commands
```
