import numpy as np
import sys
from six import StringIO, b

from gym import utils
from gym.envs.toy_text import discrete

FORWARD = 0
TURNRIGHT = 1
TURNLEFT = 2

"""orientation
    0
  3   1
    2  
"""

MAPS = {
    "4x4": [
        "SPPP",
        "PPPP",
        "PPPP",
        "PPBG"
    ],
    "8x8": [
        "SPPPPPPP",
        "PPPPPPPP",
        "PPPPPPPP",
        "PPPPPPPP",
        "PPPPPBPP",
        "PPPPPPPP",
        "PPPPPPPP",
        "PPPPPPPG"
    ],
    "8x16": [
        "SPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPBPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPP",
        "PPPPPPPPPPPPPPPG"
    ]
}

class gazonEnv(discrete.DiscreteEnv):
    """
   Gazon à tondre
   
   S : starting point, safe
   P : terrain plat
   B: terrain pentu
   X: terrain interdit

    L'episode fini lorsque tout le gazon a été tondu

    """

    metadata = {'render.modes': ['human', 'ansi']}

    def __init__(self, desc=None, map_name="4x4",is_slippery=False, orientation=0):
        if desc is None and map_name is None:
            raise ValueError('Must provide either desc or map_name')
        elif desc is None:
            desc = MAPS[map_name]
        self.desc = desc = np.asarray(desc,dtype='c')
        self.nrow, self.ncol = nrow, ncol = desc.shape
        row, col = np.where(np.array(self.desc == b'S'))[0][0], np.where(np.array(self.desc == b'S'))[1][0]
        
        position = row*ncol + col
        self.state = position, orientation

        self.nA = 3
        self.nO = 4
        self.nS = nrow * ncol * self.nO
        
        self.startstate = self.state

        #isd = np.array(desc == b'S').astype('float64').ravel()
        #isd /= isd.sum()
        
        self.mowed = np.array(desc == b'S').astype(int) + np.array(desc == b'X').astype(int)

        #P = {s : {a : [] for a in range(nA)} for s in range(nS)}

   

    def reset(self):
        self.state  = self.startstate
        self.mowed = np.array(self.desc == b'S').astype(int) + np.array(self.desc == b'X').astype(int)
        
        return self.state
        
    def step(self, action, forward_reward=-1, turn_reward=-1, mowing_reward=2 ):
        reward = 0
        position, orientation = self.state
        if action==0: # forward
            row, col = position//self.nrow, position%self.nrow
            if orientation == 0:
                row = max(row-1,0)  
            elif orientation == 1:
                col = min(col+1,self.ncol-1)
            elif orientation == 2:
                row = min(row+1,self.nrow-1)
            elif orientation == 3:
                col = max(col-1,0)
            position = row*self.ncol + col
            reward += forward_reward

        elif action==1: # right
            orientation = (orientation + 1) % 4
            reward += turn_reward
        elif action==2: # left
            orientation = (orientation - 1) % 4
            reward += turn_reward
        
        next_state = position, orientation
        self.state = next_state
        
        position, orientation = self.state
        row, col = position//self.nrow, position%self.nrow
        if self.mowed[row][col] == 0:
            reward += mowing_reward
            self.mowed[row][col] = 1
            
        done = False
        if np.sum(self.mowed) == self.nrow * self.ncol:
            done = True
        
        return next_state, reward, done

        
        # obtain one-step dynamics for dynamic programming setting
        #self.P = P

        super(gazonEnv, self).__init__(nS, nA, P, isd)

    """def _render(self, mode='human', close=False):
        if close:
            return
        outfile = StringIO() if mode == 'ansi' else sys.stdout

        row, col = self.s // self.ncol, self.s % self.ncol
        desc = self.desc.tolist()
        desc = [[c.decode('utf-8') for c in line] for line in desc]
        desc[row][col] = utils.colorize(desc[row][col], "red", highlight=True)
        if self.lastaction is not None:
            outfile.write("  ({})\n".format(["Left","Down","Right","Up"][self.lastaction]))
        else:
            outfile.write("\n")
        outfile.write("\n".join(''.join(line) for line in desc)+"\n")

        if mode != 'human':
            return outfile"""
