"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""
import time
from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])
        self.goals = []
        self.boxes = []
        self.walls=[]
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for i in range(0,self.N):
            for j in range(0,self.M):
                if(self.grid[i][j]=='B'):
                    self.boxes.append((i)*10+(j))
                if(self.grid[i][j]=='G'):
                    self.goals.append((i)*10+(j))
                if(self.grid[i][j]=='P'):
                    self.player_start=(i)*10+(j)
                if(self.grid[i][j]=='#'):
                    self.walls.append((i)*10+(j))
        self.num_boxes = len(self.boxes)

    # ---------------- Variable Encoding ----------------
    def var_player(self, y, x, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        if y<0 or y>=self.N or x<0 or x>=self.M:
            return 800 #this is always 
        else:
            return t*1000+1*100+y*10+x
           

    def var_box(self,b, y, x, t):
        """
        Variable ID for box  at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        if y<0 or y>=self.N or x<0 or x>=self.M:
            return 800
        else:
            return t*1000+(1+b)*100+y*10+x
        
    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
    # assigning initial conditions of boxes and players
        self.cnf.append([-800])
        v=1
        for i in range(0,self.N):
            for j in range(0,self.M):
                if i*10+j in self.boxes:
                    self.cnf.append([i*10+j+(1+v)*100])
                    self.boxes.remove(i*10+j)
                    v=v+1
                if (i*10+j)==self.player_start:
                    self.cnf.append([100+i*10+j])
                else:
                    self.cnf.append([-100-i*10-j])

        # 2. Player movement
        #movement of the player it depends only on the player position for now does not depends on box or any walls
        #its like if P(i,j) is true then in next step P(i+1,j) or P(i-1,j) or P(i,j+1) or P(i,j-1) or P(i,j) will be true
        for t in range(0,self.T):           
            for i in range(0,self.N):
                for j in range(0,self.M):
                    self.cnf.append([self.var_player(i,j,t+1),self.var_player(i+1,j,t+1),self.var_player(i-1,j,t+1),self.var_player(i,j+1,t+1),self.var_player(i,j-1,t+1),-self.var_player(i,j,t)])  
            # assigning logic for wall and player can't be at same place at a time
        # 3. Box movement 
        for t in range(0,self.T):           
            for i in range(0,self.N):
                for j in range(0,self.M):
                    for b in range(1,self.num_boxes+1) :
                        self.cnf.append([self.var_box(b,i,j,t+1),self.var_box(b,i+1,j,t+1),self.var_box(b,i-1,j,t+1),self.var_box(b,i,j+1,t+1),self.var_box(b,i,j-1,t+1),-self.var_box(b,i,j,t)])
        # pushing logic
        for t in range(0,self.T):
            for i in range(0,self.N):
                for j in range(0,self.M):
                    for b in range(1,self.num_boxes+1):
                        B=[]
                        B.append([self.var_box(b,i+1,j,t+1),self.var_player(i-1,j,t)])
                        B.append([self.var_box(b,i-1,j,t+1),self.var_player(i+1,j,t)])
                        B.append([self.var_box(b,i,j+1,t+1),self.var_player(i,j-1,t)])
                        B.append([self.var_box(b,i,j-1,t+1),self.var_player(i,j+1,t)])
                        for l in B:
                            self.cnf.append([-l[0],-self.var_box(b,i,j,t),l[1]])
                            self.cnf.append([-l[0],-self.var_box(b,i,j,t),self.var_player(i,j,t+1)])
        # 4. Non-overlap constraints
        #player,box,wall overlapp constraints
        for t in range(0,self.T):
            for i in range(0,self.N):
                for j in range(0,self.M):
                    for b in range(1,self.num_boxes+1):
                        self.cnf.append([-self.var_player(i,j,t+1),-self.var_box(b,i,j,t+1)])
                        if (10*i+j in self.walls):
                            self.cnf.append([-self.var_box(b,i,j,t+1)])
                            self.cnf.append([-self.var_player(i,j,t+1)])

        for b in range(0,self.num_boxes+1):
            for t in range (0,self.T+1):              #no two cells can have player and same box simultaneously
                for i in range(0,(self.N-1)*10+self.M):
                    for j in range(i+1,(self.N-1)*10+self.M):
                        if (i%10>self.M-1 or j%10>self.M-1) :
                            continue
                        self.cnf.append([-t*1000-(1+b)*100-i,-t*1000-(1+b)*100-j])
                        
        for t in range (0,self.T):              #no two cells can have diffrent boxes simultaneously
            for i in range(0,self.N):
                for j in range(0,self.M):
                    for x in range(1,self.num_boxes+1):
                        for y in range(x+1,self.num_boxes+1):
                            self.cnf.append([-self.var_box(x,i,j,t+1),-self.var_box(y,i,j,t+1)])
        
        # 5. Goal conditions
        for x in self.goals:
                c=[]
                for b in range(1,self.num_boxes+1):
                    c.append(self.T*1000+(1+b)*100+x)
                self.cnf.append(c)
        return self.cnf
        


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T
    player=[]
    boxes=[]
    goals=encoder.goals
    #finding positions of player and box at each t
    for x in model:
        if abs(x)%1000-100>=0 and abs(x)%1000-100<100 and x>0:
            player.append(x)
        for i in range(1,encoder.num_boxes+1) :
            if abs(x)%1000-(1+i)*100>=0 and abs(x)%1000-(1+i)*100<100 and x>0:
                boxes.append(x)   
    #finding when the boxes are filled (in goals)
    n=len(goals)
    for x in range(0,T+1):
        alpha=0
        for i in range(0,len(boxes)):
            if boxes[i]-boxes[i]%1000==x*1000:
                if boxes[i]%100  in goals:
                    alpha=alpha+1
        if alpha==n:
            ans=x
            break 
    #Map player positions at each timestep to movement directions
    ANS=[]
    for i in range(0,ans):
        diff=player[i]%100-player[i+1]%100
        if (diff==10):
            ANS.append("U")
        elif (diff==-10 ):
            ANS.append("D")
        elif (diff==1):
            ANS.append("L")
        elif(diff==-1):
            ANS.append("R")
    return ANS

def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()
    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1
        model = solver.get_model()
        if not model:
            return -1
        return decode(model, encoder)