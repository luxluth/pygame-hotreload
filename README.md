# pygame-hotreload

[![PyPI - Version](https://img.shields.io/pypi/v/pygame-hotreload.svg)](https://pypi.org/project/pygame-hotreload)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pygame-hotreload.svg)](https://pypi.org/project/pygame-hotreload)

-----

**Table of Contents**

- [pygame-hotreload](#pygame-hotreload)
  - [Installation](#installation)
  - [How it work](#how-it-work)
    - [`imports-start-hotreload`](#imports-start-hotreload)
    - [`globals-start-hotreload`](#globals-start-hotreload)
    - [`init-start-hotreload`](#init-start-hotreload)
    - [`loop-start-hotreload`](#loop-start-hotreload)
  - [Example](#example)
  - [License](#license)

## Installation

```zsh
pip install pygame-hotreload
```

## How it work

The `pygame-hotreload` module is a simple hot-reload module for pygame. It is partialy parse the main python file provided.

It looks for this comment in the main file:

### `imports-start-hotreload`

```python
# imports-start-hotreload
...
# imports-end-hotreload
```
This is where the module will look for the imports that needed for the game loop.

### `globals-start-hotreload`

```python
# globals-start-hotreload
...
# globals-end-hotreload
```
This is where the module will look for the global variables that needed for the game loop.

### `init-start-hotreload`

```python
# init-start-hotreload
...
# init-end-hotreload
```
This is where the module will look for the initialization of the game loop.
There is where you should initialize your global variables.

### `loop-start-hotreload`

```python
# loop-start-hotreload
...
# loop-end-hotreload
```
This is where the module will look for the game loop.

## Example

```python
# game.py

from pygame_hotreload import HotReload, set_caption
# imports-start-hotreload
import pygame
# imports-end-hotreload

# Initialize pygame
pygame.init()

# Set the window caption
set_caption("Hot Reload Example")
clock = pygame.time.Clock()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# globals-start-hotreload
global dt
global player_pos
global player_pos_2
# globals-end-hotreload

# init-start-hotreload
def init():
    global dt
    global player_pos
    global player_pos_2
    dt = 0
    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    player_pos_2 = pygame.Vector2(screen.get_width() // 3, screen.get_height() // 3)
# init-end-hotreload


# loop-start-hotreload
def loop():
    global dt
    global player_pos
    global player_pos_2
    screen.fill("black")
    pygame.draw.rect(screen, "purple", 
                     pygame.Rect(player_pos.x, player_pos.y, 100, 100))
    pygame.draw.rect(screen, "purple", 
                     pygame.Rect(player_pos_2.x, player_pos_2.y, 100, 100), 1)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_z] or keys[pygame.K_UP]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos.y += 300 * dt
    if keys[pygame.K_q] or keys[pygame.K_LEFT]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos.x += 300 * dt

    dt = clock.tick(60) / 1000
# loop-end-hotreload

# Initialize the hot reload
hotreload = HotReload(
    main_file=__file__,
    screen=screen,
    clock=clock,
    clock_tick=60,
    gen_script_name="gen.py",
)

hotreload.run()
```

## License

`pygame-hotreload` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
