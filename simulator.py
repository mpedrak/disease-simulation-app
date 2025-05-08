import pygame
import random
import sys
import enum
import csv


# --- Parameters ---

# Pygame 
WIDTH, HEIGHT = 1000, 800 # window size
DOT_SIZE = 7 # of agents
WINDOW_TITLE = "Simulation of disease spread in a population"

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)  
RED = (255, 0, 0)    
BLUE = (0, 0, 255)   

# Simulation
FPS = 60 
NUM_AGENTS = 200  
MAX_SPEED = 3 # of agents
MAX_DAYS = 100 
GATHER_STATS = True

# Disease
INFECTION_RADIUS = 50  
INFECTION_PROBABILITY = 0.2 
INFECTED_ON_START = 0.2 
MIN_INFECTED_DAYS = 30
CURE_PROBABILITY = 0.01 # after min_infected_days
IMMUNITY_DAYS = 90 



# --- Agent ---

class Status(enum.Enum):
    Susceptible = 1
    Infected = 2
    Recovered = 3


class Agent:
    def __init__(self, x, y, status):
        self.x = x
        self.y = y
        self.status = status
        self.velocity = [random.uniform(-MAX_SPEED, MAX_SPEED), random.uniform(-MAX_SPEED, MAX_SPEED)]
        self.infected_days = 0
        self.immune_days = 0


    def move(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        if self.x <= 0 or self.x >= WIDTH: 
            self.velocity[0] = -self.velocity[0]
            if self.x < 0: self.x = 0
            elif self.x > WIDTH: self.x = WIDTH

        if self.y <= 0 or self.y >= HEIGHT: 
            self.velocity[1] = -self.velocity[1]
            if self.y < 0: self.y = 0
            elif self.y > HEIGHT: self.y = HEIGHT


    def distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


    def draw(self, screen):
        if self.status == Status.Susceptible: color = GREEN
        elif self.status == Status.Infected: color = RED
        else: color = BLUE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), DOT_SIZE)


    def simulate_day(self, others):
        if self.status == Status.Recovered:
            self.immune_days += 1
            if self.immune_days >= IMMUNITY_DAYS: self.status = Status.Susceptible

        if self.status == Status.Infected:
            for other in others:
                if other.status == Status.Susceptible and self.distance(other) < INFECTION_RADIUS:
                    if random.random() < INFECTION_PROBABILITY:
                        other.status = Status.Infected
                        other.infected_days = 0

            self.infected_days += 1
            if self.infected_days >= MIN_INFECTED_DAYS:
                if random.random() < CURE_PROBABILITY:
                    self.status = Status.Recovered
                    self.immune_days = 0

def gather_stats(agents):
    susceptible = 0
    infected = 0
    recovered = 0

    for other in agents:
        if other.status == Status.Susceptible: susceptible += 1
        elif other.status == Status.Infected: infected += 1
        else: recovered += 1

    return susceptible, infected, recovered


# --- Code ---

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

agents = []
for _ in range(0, NUM_AGENTS):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    if random.random() < INFECTED_ON_START: agents.append(Agent(x, y, Status.Infected))
    else: agents.append(Agent(x, y, Status.Susceptible))
   
clock = pygame.time.Clock()
running = True
day = 1
stats = []

while running:
    day += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    window.fill(WHITE)

    for agent in agents:
        agent.move()
        agent.simulate_day(agents)
        agent.draw(window)

    pygame.display.flip()
    clock.tick(FPS)

    if GATHER_STATS: stats.append(gather_stats(agents))

    if day > MAX_DAYS: running = False

pygame.quit()

if GATHER_STATS:
    with open('./stats.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Day', 'Susceptible', 'Infected', 'Recovered'])
        for i, stat in enumerate(stats):
            writer.writerow([i + 1] + list(stat))

sys.exit()
