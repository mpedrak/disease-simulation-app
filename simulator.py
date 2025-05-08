import pygame
import random
import sys
import enum
import csv
import time


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
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)

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


    def distance_squared(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


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
                if other.status == Status.Susceptible and self.distance_squared(other) < INFECTION_RADIUS ** 2:
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


def draw_start_screen(window):
    font = pygame.font.SysFont(None, 30)
    big_font = pygame.font.SysFont(None, 60)

    input_fields = {
        "FPS": "60",
        "NUM_AGENTS": "200",
        "MAX_SPEED": "3",
        "MAX_DAYS": "100",
        "INFECTION_RADIUS": "50",
        "INFECTION_PROBABILITY": "0.2",
        "INFECTED_ON_START": "0.2",
        "MIN_INFECTED_DAYS": "30",
        "CURE_PROBABILITY": "0.01",
        "IMMUNITY_DAYS": "90",
    }

    value_fields = {}
    active_field = None

    action_buttons_width = 300
    action_buttons_height = 50
    start_button = pygame.Rect(WIDTH // 2 - action_buttons_width // 2, HEIGHT - 210, action_buttons_width, action_buttons_height)
    exit_button = pygame.Rect(WIDTH // 2 - action_buttons_width // 2, HEIGHT - 150, action_buttons_width, action_buttons_height)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                active_field = None
                for key, rect in value_fields.items():
                    if rect.collidepoint(event.pos):
                        active_field = key
                        break

                if start_button.collidepoint(event.pos):
                    return {key: value for key, value in input_fields.items()}
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.KEYDOWN and active_field is not None:
                if event.key == pygame.K_BACKSPACE:
                    input_fields[active_field] = input_fields[active_field][:-1]
                elif event.key == pygame.K_RETURN:
                    active_field = None
                else:
                    input_fields[active_field] += event.unicode

        window.fill(WHITE)
        title = big_font.render(WINDOW_TITLE, True, BLACK)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        y_offset = 120
        value_fields.clear()

        max_label_width = 0
        for key, value in input_fields.items():
            label = font.render(key.replace("_", " ").capitalize(), True, BLACK)
            max_label_width = max(max_label_width, label.get_width())

        max_label_width += 20

        for key, value in input_fields.items():
            label = font.render(key.replace("_", " ").capitalize(), True, BLACK)
            window.blit(label, (WIDTH // 2 - max_label_width, y_offset))

            field = pygame.Rect(WIDTH // 2, y_offset, max_label_width, 30)
            value_fields[key] = field
            pygame.draw.rect(window, LIGHT_GRAY, field, 0)
            pygame.draw.rect(window, BLACK, field, 2)

            show_cursor = key == active_field and (pygame.time.get_ticks() // 500) % 2 == 0
            display_text = value + ('|' if show_cursor else '')
            text = font.render(display_text, True, BLACK)
            window.blit(text, (field.x + 5, field.y + 5))

            y_offset += 40

        pygame.draw.rect(window, BLACK, start_button)
        pygame.draw.rect(window, BLACK, exit_button)

        start_text = font.render("Start Simulation", True, WHITE)
        exit_text = font.render("Exit", True, WHITE)

        window.blit(start_text, (start_button.x + (action_buttons_width - start_text.get_width()) // 2, 
            start_button.y + (action_buttons_height - start_text.get_height()) // 2))
        window.blit(exit_text, (exit_button.x + (action_buttons_width - exit_text.get_width()) // 2, 
            exit_button.y + (action_buttons_height - exit_text.get_height()) // 2))

        pygame.display.flip()


# --- Code ---

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

params = draw_start_screen(window)

FPS = int(params["FPS"])
NUM_AGENTS = int(params["NUM_AGENTS"])
MAX_SPEED = int(params["MAX_SPEED"])
MAX_DAYS = int(params["MAX_DAYS"])
INFECTION_RADIUS = int(params["INFECTION_RADIUS"])
INFECTION_PROBABILITY = float(params["INFECTION_PROBABILITY"])
INFECTED_ON_START = float(params["INFECTED_ON_START"])
MIN_INFECTED_DAYS = int(params["MIN_INFECTED_DAYS"])
CURE_PROBABILITY = float(params["CURE_PROBABILITY"])
IMMUNITY_DAYS = int(params["IMMUNITY_DAYS"])

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
