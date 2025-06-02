from typing import Union

import pygame
import random
import sys
import enum
import csv
import pathlib



# --- Constants ---

# Pygame 
WIDTH, HEIGHT = 1200, 1000 # window size
DOT_SIZE = 7 # of agents
WINDOW_TITLE = "Simulation of disease spread in a population"

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)  
RED = (255, 0, 0)    
BLUE = (0, 0, 255)   
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)



# --- Parameters --- (user modifiable)

# Simulation
FPS = 60 
NUM_AGENTS = 200  
MAX_DAYS = 300 
GATHER_STATS = True
SHOW_VIEW = True

# Agents parameters
NO_MOVE_PROBABILITY = 0.3
MAX_SPEED = 10 # of agents (max distance per day)
DAY_IN_WEEK_MODIFIER = [0.2, 0.5, 0.8, 0.4, 0.3, 1, 0.9] # of max speed through the week
VACCINED_PERCENTAGE = 0.01 # of modifing agents status every day
MASKED_PERCENTAGE = 0.02 # of agents every day
FEARFUL_PERCENTAGE = 0.2 # of new agents after creating
ANTI_VACCINE_PERCENTAGE = 0.1 # of new agents after creating
MIN_DAYS_TO_LIVE = 100 # normal live
NORMAL_DEATH_PROBABILITY = 0.01 # after min_days_to_live
REPRODUCTION_PROBABILITY = 0.0005 # every day
REPRODUCTION_RADIUS = 30

# Disease
INFECTION_RADIUS = 50  
INFECTION_PROBABILITY = 0.2 
INFECTED_ON_START = 0.2 
MIN_INFECTED_DAYS = 30
CURE_PROBABILITY = 0.01 # after min_infected_days
IMMUNITY_DAYS = 90 
DISEASE_DEATH_PROBABILITY = 0.02 # every day



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
        self.anti_vaccine = False
        self.fearful = False
        self.days_old = 0

    def get_info_list(self) -> list[str]:
        return [
            f"Coords: ({self.x:.2f}, {self.y:.2f})",
            f"Status: {self.status.name}",
            f"Days old: {self.days_old}",
            f"Infected days: {self.infected_days}",
            f"Immune days: {self.immune_days}",
            f"Anti vaccine: {self.anti_vaccine}",
            f"Fearful: {self.fearful}"
        ]

    def move(self):
        if random.random() < NO_MOVE_PROBABILITY: return

        if self.fearful: speed = MAX_SPEED / 2
        else: speed = MAX_SPEED

        self.velocity = [random.uniform(-speed, speed), random.uniform(-speed, speed)]
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


    def draw(self, screen, selected=False):
        if self.status == Status.Susceptible: color = GREEN
        elif self.status == Status.Infected: color = RED
        else: color = BLUE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), DOT_SIZE)
        if selected:
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), DOT_SIZE + 3, 2)


    def simulate_day(self, others, vaccined_today):
        # Check if its time to die
        self.days_old += 1
        if self.days_old >= MIN_DAYS_TO_LIVE:
            if random.random() < NORMAL_DEATH_PROBABILITY: return "DEAD"

        # Check if agent is vaccinated
        if self.anti_vaccine == False and self.status == Status.Susceptible:
            if random.random() < VACCINED_PERCENTAGE:
                self.status = Status.Recovered
                self.immune_days = 0
                vaccined_today[0] += 1

        # Check if agent has still immunity
        elif self.status == Status.Recovered:
            self.immune_days += 1
            if self.immune_days >= IMMUNITY_DAYS: self.status = Status.Susceptible

        if self.status == Status.Infected:
            # Check if agent is dead due to disease
            if random.random() < DISEASE_DEATH_PROBABILITY:
                return "DEAD"
            
            # Try to infect others
            for other in others:
                if other.status == Status.Susceptible:
                    if (
                        (random.random() < MASKED_PERCENTAGE and self.distance_squared(other) < (INFECTION_RADIUS / 2) ** 2) 
                        or self.distance_squared(other) < INFECTION_RADIUS ** 2
                    ):
                        if random.random() < INFECTION_PROBABILITY:
                            other.status = Status.Infected
                            other.infected_days = 0

            # Check if agent is cured
            self.infected_days += 1
            if self.infected_days >= MIN_INFECTED_DAYS:
                if random.random() < CURE_PROBABILITY:
                    self.status = Status.Recovered
                    self.immune_days = 0

        # Try to reproduce
        for other in others:
            if self.distance_squared(other) < REPRODUCTION_RADIUS ** 2 and random.random() < REPRODUCTION_PROBABILITY:
                x = (self.x + other.x) / 2
                y = (self.y + other.y) / 2
                new_agent = Agent(x, y, Status.Susceptible)
                if random.random() < ANTI_VACCINE_PERCENTAGE: new_agent.anti_vaccine = True
                if random.random() < FEARFUL_PERCENTAGE: new_agent.fearful = True
                return new_agent



# --- Other functions ---

def gather_stats(agents):
    susceptible = 0
    infected = 0
    recovered = 0

    for x in agents:
        if x.status == Status.Susceptible: susceptible += 1
        elif x.status == Status.Infected: infected += 1
        else: recovered += 1

    return susceptible, infected, recovered


def draw_start_screen(window):
    font = pygame.font.SysFont(None, 30)
    big_font = pygame.font.SysFont(None, 60)

    input_fields = {
        "FPS": str(FPS),
        "Agents count": str(NUM_AGENTS),
        "Maximum simulation duration in days": str(MAX_DAYS),
        "Gather stats data": str(GATHER_STATS),
        "Show simulation view": str(SHOW_VIEW),
        
        "Probability of agent staying in one place": str(NO_MOVE_PROBABILITY),
        "Maximum distance per day": str(MAX_SPEED),
        "Percentage of population vaccined every day": str(VACCINED_PERCENTAGE),
        "Percentage of population masked every day": str(MASKED_PERCENTAGE),
        "Percentage of population being fearful": str(FEARFUL_PERCENTAGE),
        "Percentage of population being anti vaccine": str(ANTI_VACCINE_PERCENTAGE),
        "Minimum normal life duration": str(MIN_DAYS_TO_LIVE),
        "Probability of natural death": str(NORMAL_DEATH_PROBABILITY),
        "Probability of reproduction ": str(REPRODUCTION_PROBABILITY),
        "Reproduction radius": str(REPRODUCTION_RADIUS),
        "Modifiers of maximum distance per day during week": str(DAY_IN_WEEK_MODIFIER)[1 : -1],
        
        "Infection radius": str(INFECTION_RADIUS),
        "Infection probability": str(INFECTION_PROBABILITY),
        "Percentage of population infected on start": str(INFECTED_ON_START),
        "Minimum infection duration": str(MIN_INFECTED_DAYS),
        "Curing probability after minimum days": str(CURE_PROBABILITY),
        "Immunity duration after curied": str(IMMUNITY_DAYS),
        "Probability of death due to infection": str(DISEASE_DEATH_PROBABILITY),
    }

    value_fields = {}
    active_field = None

    action_buttons_width = 300
    action_buttons_height = 50
    start_button = pygame.Rect(WIDTH // 2 - action_buttons_width // 2, HEIGHT - 155, action_buttons_width, action_buttons_height)
    exit_button = pygame.Rect(WIDTH // 2 - action_buttons_width // 2, HEIGHT - 99, action_buttons_width, action_buttons_height)

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
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        y_offset = 80
        value_fields.clear()

        max_label_width = 0
        for key, value in input_fields.items():
            label = font.render(key, True, BLACK)
            max_label_width = max(max_label_width, label.get_width())

        max_label_width += 20

        for key, value in input_fields.items():
            label = font.render(key, True, BLACK)
            window.blit(label, (WIDTH // 2 - max_label_width, y_offset))

            field = pygame.Rect(WIDTH // 2, y_offset, max_label_width, 30)
            value_fields[key] = field
            pygame.draw.rect(window, LIGHT_GRAY, field, 0)
            pygame.draw.rect(window, BLACK, field, 2)

            show_cursor = key == active_field and (pygame.time.get_ticks() // 500) % 2 == 0
            display_text = value + ('|' if show_cursor else '')
            text = font.render(display_text, True, BLACK)
            window.blit(text, (field.x + 5, field.y + 5))

            y_offset += 32

        pygame.draw.rect(window, BLACK, start_button)
        pygame.draw.rect(window, BLACK, exit_button)

        start_text = font.render("Start Simulation", True, WHITE)
        exit_text = font.render("Exit", True, WHITE)

        window.blit(start_text, (start_button.x + (action_buttons_width - start_text.get_width()) // 2, 
            start_button.y + (action_buttons_height - start_text.get_height()) // 2))
        window.blit(exit_text, (exit_button.x + (action_buttons_width - exit_text.get_width()) // 2, 
            exit_button.y + (action_buttons_height - exit_text.get_height()) // 2))

        pygame.display.flip()


def set_params(params):
    global FPS, NUM_AGENTS, MAX_DAYS
    global NO_MOVE_PROBABILITY, MAX_SPEED, VACCINED_PERCENTAGE, MASKED_PERCENTAGE
    global FEARFUL_PERCENTAGE, ANTI_VACCINE_PERCENTAGE, MIN_DAYS_TO_LIVE
    global NORMAL_DEATH_PROBABILITY, REPRODUCTION_PROBABILITY, REPRODUCTION_RADIUS
    global INFECTION_RADIUS, INFECTION_PROBABILITY, INFECTED_ON_START
    global MIN_INFECTED_DAYS, CURE_PROBABILITY, IMMUNITY_DAYS, DISEASE_DEATH_PROBABILITY
    global GATHER_STATS, DAY_IN_WEEK_MODIFIER, SHOW_VIEW

    FPS = int(params["FPS"])
    NUM_AGENTS = int(params["Agents count"])
    MAX_DAYS = int(params["Maximum simulation duration in days"])
    GATHER_STATS = params["Gather stats data"].lower() == "true"
    SHOW_VIEW = params["Show simulation view"].lower() == "true"
    
    NO_MOVE_PROBABILITY = float(params["Probability of agent staying in one place"])
    MAX_SPEED = int(params["Maximum distance per day"])
    VACCINED_PERCENTAGE = float(params["Percentage of population vaccined every day"])
    MASKED_PERCENTAGE = float(params["Percentage of population masked every day"])
    FEARFUL_PERCENTAGE = float(params["Percentage of population being fearful"])
    ANTI_VACCINE_PERCENTAGE = float(params["Percentage of population being anti vaccine"])
    MIN_DAYS_TO_LIVE = int(params["Minimum normal life duration"])
    NORMAL_DEATH_PROBABILITY = float(params["Probability of natural death"])
    REPRODUCTION_PROBABILITY = float(params["Probability of reproduction "])
    REPRODUCTION_RADIUS = int(params["Reproduction radius"])
    DAY_IN_WEEK_MODIFIER = [float(x) for x in params["Modifiers of maximum distance per day during week"].split(",")]
    
    INFECTION_RADIUS = int(params["Infection radius"])
    INFECTION_PROBABILITY = float(params["Infection probability"])
    INFECTED_ON_START = float(params["Percentage of population infected on start"])
    MIN_INFECTED_DAYS = int(params["Minimum infection duration"])
    CURE_PROBABILITY = float(params["Curing probability after minimum days"])
    IMMUNITY_DAYS = int(params["Immunity duration after curied"])
    DISEASE_DEATH_PROBABILITY = float(params["Probability of death due to infection"])


def get_hovered_agent(agents):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for agent in agents:
        dx = agent.x - mouse_x
        dy = agent.y - mouse_y
        if dx**2 + dy**2 <= DOT_SIZE**2:
            return agent
    return None


def draw_tooltip(window, agent, set_coords: Union[tuple, None] = None, auto_position: bool = True):
    if set_coords is None:
        tooltip_x, tooltip_y = pygame.mouse.get_pos()
        x, y = tooltip_x + 10, tooltip_y + 10
    else:
        x, y = set_coords

    font = pygame.font.SysFont(None, 20)
    padding = 5
    line_height = 20

    info_lines = agent.get_info_list()

    tooltip_width = max(font.size(line)[0] for line in info_lines) + 2 * padding
    tooltip_height = line_height * len(info_lines) + 2 * padding

    if auto_position:
        if x + tooltip_width > WIDTH:
            x = WIDTH - tooltip_width
        if y + tooltip_height > HEIGHT:
            y = HEIGHT - tooltip_height

    tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
    pygame.draw.rect(window, LIGHT_GRAY, tooltip_rect)
    pygame.draw.rect(window, BLACK, tooltip_rect, 2)

    for i, line in enumerate(info_lines):
        text = font.render(line, True, BLACK)
        window.blit(text, (x + 5, y + 5 + i * 20))


# --- Main ---

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)

params = draw_start_screen(window)
set_params(params)

if GATHER_STATS:
    stats_path = pathlib.Path("./stats")
    if not stats_path.exists():
        stats_path.mkdir(parents=True)

agents = []
for _ in range(0, NUM_AGENTS):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    agent = Agent(x, y, Status.Susceptible)
    if random.random() < INFECTED_ON_START: agent.status = Status.Infected
    if random.random() < ANTI_VACCINE_PERCENTAGE: agent.anti_vaccine = True
    if random.random() < FEARFUL_PERCENTAGE: agent.fearful = True
    agents.append(agent)

clock = pygame.time.Clock()
running = True
day = 0
stats = []
start_max_speed = MAX_SPEED
selected_agent = None
paused = False

if GATHER_STATS:    # 0th day
    s = list(gather_stats(agents))
    s.append(0)     # Vaccined
    stats.append(s)

while running:
    day_in_week = day % 7
    MAX_SPEED = start_max_speed * DAY_IN_WEEK_MODIFIER[day_in_week]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False        
        elif SHOW_VIEW and event.type == pygame.MOUSEBUTTONDOWN:
            selected_agent = get_hovered_agent(agents)
        elif SHOW_VIEW and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused

    if SHOW_VIEW: window.fill(WHITE)

    if SHOW_VIEW and paused:
        for agent in agents:
            agent.draw(window, selected=(agent == selected_agent))
        
        hovered_agent = get_hovered_agent(agents)
        if hovered_agent:
            draw_tooltip(window, hovered_agent)
        
    else:

        vaccined_today = [0]
        for agent in agents:
            agent.move()
            result = agent.simulate_day(agents, vaccined_today)
            if result == "DEAD":
                agents.remove(agent)
            elif result is not None: # reproduction happened
                agents.append(result)
                if (SHOW_VIEW): agent.draw(window, selected=(agent == selected_agent))
                if (SHOW_VIEW): result.draw(window)
            else:
                if (SHOW_VIEW): agent.draw(window, selected=(agent == selected_agent))

        s = list(gather_stats(agents))
        s.append(vaccined_today[0])
        if GATHER_STATS: stats.append(s)
        
        day += 1
        if day >= MAX_DAYS: running = False

    if (SHOW_VIEW):
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()

if GATHER_STATS:
    with open('./stats/total-counts.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Day', 'Susceptible', 'Infected', 'Recovered', 'Vaccined'])
        for i, stat in enumerate(stats):
            writer.writerow([i] + list(stat))

print("Simulation finished succesfully.")

sys.exit()
