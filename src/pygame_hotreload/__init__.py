# SPDX-FileCopyrightText: 2023-present luxluth <delphin.blehoussi93@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
pygame-hotreload
================
An hot reload enhancer for pygame developement
"""

from typing import Union, Tuple, Callable, Any

from rich import print as rprint
from .crypto import getMd5
import pygame
import sys


def set_caption(title: str):
    """
    Change the game window title.
    
    Parameters
    ----------
    title : str
        The title string

    Returns
    -------
    None
    """
    pygame.display.set_caption(title)

def get_font_size(
        screen_width: Union[int, float], 
        screen_height: Union[int, float], 
        scale_factor=0.05
    ):
    """
    Get a font size depending on the screen width an height.

    Parameters
    ----------
    screen_width : int | float
        The screen width
    screen_height : int | float
        The screen height
    scale_factor : float, optional
        The scale factor of the font to display
    
    Returns
    -------
    int -- The adapted fontsize
    """
    return int(min(screen_width, screen_height) * scale_factor)

def show_error_message(
        message: str, 
        screen: pygame.Surface,
        screen_width: Union[int, float], 
        screen_height: Union[int, float], 
        height=0.08, 
        banner_color: Union[str, Tuple[int, int, int]]=(255, 0, 0),
        message_color: Union[str, Tuple[int, int, int]]=(0, 0, 0),
    ):
    """
    Show an error message on the top of the game window

    Parameters
    ----------
    message : str
        The error message to display
    screen : pygame.Surface
        The pygame Surface to display on
    screen_width : int | float
        The Surface width
    screen_height : int | float 
        The Surface height
    height : float
        Banner Height (Default `0.08`, that is `8%` of the screen)
    banner_color : str | tuple[int, int, int]
        Banner background color (Default `red`)
    message_color : str | tuple[int, int, int]
        Banner text color (Default `black`)
    
    Returns
    -------
    None
    """
    fontsize = get_font_size(screen_width, screen_height)
    font = pygame.font.SysFont(None, fontsize)
    banner_height = int(screen_height * height)
    banner_color = banner_color

    pygame.draw.rect(screen, banner_color, (0, 0, screen_width, banner_height))

    text = font.render(message, True, message_color)
    text_rect = text.get_rect(center=(screen_width // 2, banner_height // 2))
    screen.blit(text, text_rect)

    pygame.display.flip()


def exec_script(hr: "HotReload", script: str, script_path: str, initscript: bool):
    """Execute the game script"""
    global screen
    global clock
    screen = hr.screen
    clock = hr.clock
    try:
        if initscript:
            exec(compile(script, script_path, "exec"))
            exec("init()")
        else:
            exec(compile(script, script_path, "exec"))
            exec("loop()")
        hr.script_err = False
    except Exception as e:
        hr.script_err_msg = f"Error executing game script: {e}"
        rprint("[red bold]\[pygame-hotreload][/] " + hr.script_err_msg)
        hr.script_err = True

def load_game_script(hr: "HotReload", script_path: str, init=False):
    """Load the Game script"""
    rprint(f"[green bold]\[pygame-hotreload][/] load script-'{script_path}'")
    scriptMd5 = getMd5(script_path)
    script = ""
    try:
        with open(script_path, "r") as f:
            script = f.read()
            exec_script(hr, script, script_path, init)
    except Exception as e:
        hr.script_err_msg = f"Error loading game script: {e}"
        rprint("[red bold]\[pygame-hotreload][/] " + hr.script_err_msg)
        hr.script_err = True
    return scriptMd5, script


class HotReload():
    """
    HotReload
    =========
    The HotReload class

    Parameters
    ----------
    main_file : str
        The main file path
    screen : pygame.Surface
        The pygame Surface to display on
    clock : pygame.time.Clock
        The pygame Clock
    clock_tick : int, optional
        The clock tick (Default `60`)
    gen_script_name : str, optional
        The generated script name (Default `loop.py`)
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
            self,
            main_file: str,
            screen: pygame.Surface,
            clock: pygame.time.Clock,
            clock_tick=60,
            gen_script_name: str="loop.py",
        ):
        self.main_file = main_file
        self.script_generated = False
        self.script_err = False
        self.script_err_msg = ""
        self.gen_script_name = gen_script_name
        self.clock = clock
        self.clock_tick = clock_tick
        self.screen = screen
        self.md5 = ""
        self.main_file_md5 = ""
        self.init_srcipt = ""
        self.loop_script = ""

        self._init()

    def get_imports(self):
        """Get the imports of the main script"""
        imports = []
        with open(self.main_file, "r") as f:
            lines = f.readlines()
            start = False
            for line in lines:
                if "imports-start-hotreload" in line:
                    start = True
                    continue
                if "imports-end-hotreload" in line:
                    start = False
                    break
                if start:
                    imports.append(line)
        return imports
    
    def get_globals(self):
        """Get the globals of the main script"""
        globals_ = []
        with open(self.main_file, "r") as f:
            lines = f.readlines()
            start = False
            for line in lines:
                if "globals-start-hotreload" in line:
                    start = True
                    continue
                if "globals-end-hotreload" in line:
                    start = False
                    break
                if start:
                    globals_.append(line)
        return globals_

    def get_loop(self):
        """Get the loop function of the main script"""
        loop = []
        with open(self.main_file, "r") as f:
            lines = f.readlines()
            start = False
            for line in lines:
                if "loop-start-hotreload" in line:
                    start = True
                    continue
                if "loop-end-hotreload" in line:
                    start = False
                    break
                if start:
                    loop.append(line)
        if len(loop) == 0:
            return ""
        loop = "".join(loop)
        # remove the definition from the first line
        loop = "def loop():\n" + "\n".join(loop.split("\n")[1:])
        return loop
    
    def get_init(self):
        """Get the init function of the main script"""
        init = []
        with open(self.main_file, "r") as f:
            lines = f.readlines()
            start = False
            for line in lines:
                if "init-start-hotreload" in line:
                    start = True
                    continue
                if "init-end-hotreload" in line:
                    start = False
                    break
                if start:
                    init.append(line)
        if len(init) == 0:
            return ""
        init = "".join(init)
        # remove the definition from the first line
        init = "def init():\n" + "\n".join(init.split("\n")[1:])
        return init
    
    def _init(self):
        """Initialize the HotReload"""
        self.init_srcipt = self.get_init()
        self.loop_script = self.get_loop()
        if len(self.init_srcipt) == 0:
            rprint("[red bold]\[pygame-hotreload][/] No init function found")
            sys.exit(1)
        if len(self.loop_script) == 0:
            rprint("[red bold]\[pygame-hotreload][/] No loop function found")
            sys.exit(1)
    

    def genarate_game_file(self):
        """Generate the game script file"""
        rprint("[green bold]\[pygame-hotreload][/] Generate Game Script")
        with open(self.gen_script_name, "w") as f:
            # add imports
            for imp in self.get_imports():
                f.write(imp)
            # add globals
            for glob in self.get_globals():
                f.write(glob)
            f.write(self.init_srcipt)
            f.write(self.loop_script)
        self.script_generated = True

    def run(self):
        """Run the HotReload"""
        self.genarate_game_file()
        self.md5, self.loop_script = load_game_script(self, self.gen_script_name, True)
        self.main_file_md5 = getMd5(self.main_file)
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                if self.script_err:
                    show_error_message(
                        self.script_err_msg, 
                        self.screen, 
                        self.screen.get_width(), 
                        self.screen.get_height()
                    )
                else:
                    exec_script(self, self.loop_script, self.gen_script_name, False)
                
                if self.main_file_md5 != getMd5(self.main_file):
                    self.screen.fill("black")
                    prev_loop = self.loop_script
                    self.loop_script = self.get_loop()
                    self.main_file_md5 = getMd5(self.main_file)
                    self.script_generated = False
                    self.script_err = False
                    self.script_err_msg = ""
                    if prev_loop != self.loop_script:
                        self.genarate_game_file()
                        self.md5, self.loop_script = load_game_script(self, self.gen_script_name, False)
                        rprint("[green bold]\[pygame-hotreload][/] Game Script Reloaded")
                    else:
                        rprint("[red bold]\[pygame-hotreload][/] Game Script Modified but loop function not modified")

                
                pygame.display.flip()
                self.clock.tick(self.clock_tick)
        except Exception as e:
            rprint(f"[red bold]\[pygame-hotreload][/] Error running the game loop: {e}")
            pygame.quit()
            sys.exit()