Metadata-Version: 1.0
Name: ConwayCPU
Version: 0.0
Summary: The Game of Life, living on your CPU
Homepage: http://pypi.python.org/pypi/ConwayCPU/
Author: Rupert Deese
Author-email: hartdeese@mac.com
License: MIT
Description: ======
        ConwayCPU
        ======
        
        ConwayCPU is an implementation of Conway's game of Life that
        lives in a console window. The rules of the game have been changed
        slightly to allow for the influence of your computer's CPU usage.
        ConwayCPU's life is more virile (look for the yellow cells!)
        when your CPU is busy--and returns to its normal self when your 
        computer is idle.

        This project is a half-baked idea of mine that I hope you enjoy, but
        I want to credit Eric Rose and Giampaolo Rodola for their packages,
        which made this much easier to create.
        
        .. _psutil library: https://pypi.python.org/pypi/psutil
        .. _original conway package: https://pypi.python.org/pypi/conway/1.1
        .. _Blessings terminal library: http://pypi.python.org/pypi/blessings/
        
        
        Features
        ========
        
        * Runs a fullscreen Game of Life world in your console.
        * Makes Life more interesting by "loosening the rules" probabilistically
        according to how active the CPU is. Yellow colored cells in the game are
        the ones created by CPU activity.
        * The life environment is split into as many vertical sections as your
        machine has cores, with each core's activity only affecting the Life in
        its section.
        
        
        Getting it running
        ==================
        
        ::
        
            pip install conwayCPU
            conwayCPU.py
        
        Sit back and enjoy Life.

            If your computer is really powerful and you don't often come near
            max CPU usage, you can pass the script an argument between 0 and 1
            for the program to treat as "max cpu usage".
        
        Kudos
        =====
        
        A very simple extension of the pip package 'conway'. Credit to Eric Rose
        for the original package.
        
        
        Version History
        ===============
        
        0.0 Initial Release