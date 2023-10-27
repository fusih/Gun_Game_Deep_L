import torch 
import random 
import numpy as np 
import copy
from collections import deque
from model import Linear_QNet, QTrainer
from game import GunGameAI
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 512
LR = 0.001
 

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.999 # discount rate 
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(5, 256, 3)
        self.model.load_state_dict(torch.load('model/best-model-27-10-16-39.pth'))
        self.targetmodel = copy.deepcopy(self.model)

        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma) 

    def get_state(self,game):
        angle = (game.angle + 18 ) / 93
        #gravity = (game.gravity - 3.5) / 7  
        x_pos_player = (game.xp - 30) / 220
        y_pos_player = (game.y1 - 285) / 215
        x_pos_target = (game.xt  - 610) / 240
        y_pos_target = (game.y2 -285) /215

        state = [
            angle,
            #gravity,
            x_pos_player,
            y_pos_player,
            x_pos_target,
            y_pos_target
        ]
        
        return np.array(state, dtype=float)

    def copytarget(self):
        self.targetmodel = copy.deepcopy(self.model)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples 
        else:   
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation 
        #self.epsilon = 200 - self.n_games
        final_move = [0,0,0]
        #if random.randint(0, 270) < self.epsilon:
        #    move = random.randint(0, 2)
        #    final_move[move] = 1
        #else: 
        state0 = torch.tensor(state, dtype=torch.float)
        #prediction = self.model(state0)
        prediction = self.targetmodel(state0)
        move = torch.argmax(prediction).item()
        final_move[move] = 1    
        
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0 
    record = 0
    agent = Agent()
    game = GunGameAI()
    while True:
        #get old state 
        state_old = agent.get_state(game)

        #get move 
        final_move = agent.get_action(state_old)

        #perform move and get new state 
        reward, lost, score = game.play_step(final_move)

        state_new = agent.get_state(game)

        #train short memory
        #agent.train_short_memory(state_old, final_move, reward, state_new, lost)
        agent.remember(state_old, final_move, reward, state_new, lost)
        agent.train_long_memory()

        #remember 
        #agent.remember(state_old, final_move, reward, state_new, lost)

        if lost:
            game.reset()
            agent.n_games +=1 
            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

        if (agent.n_games%3 == 0):
            #train long memory, plot result 
           
            #agent.train_long_memory()
            agent.copytarget()

            


if __name__ == '__main__':
    train()
    