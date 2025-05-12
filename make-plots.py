from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import pathlib


plot_path = pathlib.Path("./plots")
if not plot_path.exists():
    plot_path.mkdir(parents=True)


# Get datetime prefix
datetime_prefix = datetime.now().strftime("%m-%d_%H-%M-%S") + "-"


df = pd.read_csv('./stats/total-counts.csv')


# Plot with total counts
plt.figure(figsize=(12, 8))
plt.plot(df['Day'], df['Susceptible'], label="Podatni", color='blue')
plt.plot(df['Day'], df['Infected'], label="Zarażeni", color='red')
plt.plot(df['Day'], df['Recovered'], label="Wyzdrowiali", color='green')

plt.title("Wykres symulacji epidemii")
plt.xlabel("Dzień")
xticks = []
xticks.extend(range(0, df['Day'].max() + 1, df['Day'].max() // 20))
xticks[-1] = (df['Day'].max())
plt.xticks(xticks)
plt.ylabel("Liczba osób")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'./plots/{datetime_prefix}total-counts.png', dpi=300)
plt.close()


# Plot with percentages
df['Total'] = df['Susceptible'] + df['Infected'] + df['Recovered']
df['Susceptible_P'] = df['Susceptible'] / df['Total'] * 100
df['Infected_P'] = df['Infected'] / df['Total'] * 100
df['Recovered_P'] = df['Recovered'] / df['Total'] * 100

plt.figure(figsize=(12, 8))
plt.plot(df['Day'], df['Susceptible_P'], label="Podatni", color='blue')
plt.plot(df['Day'], df['Infected_P'], label="Zarażeni", color='red')
plt.plot(df['Day'], df['Recovered_P'], label="Wyzdrowiali", color='green')

plt.title("Wykres symulacji epidemii (wartości procentowe)")
plt.xlabel("Dzień")
plt.xticks(xticks)
plt.ylabel("Udział w populacji [%]")
plt.yticks(range(0, 101, 10))
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'./plots/{datetime_prefix}total-percentages.png', dpi=300)
plt.close()


# Plot with vaccination
plt.figure(figsize=(12, 8))
plt.plot(df['Day'], df['Vaccined'], label="Zaszczepieni", color='orange')

plt.title("Wykres codziennych szczepień")
plt.xlabel("Dzień")
plt.xticks(xticks)
plt.ylabel("Liczba zaszczepionych osób")
plt.yticks(range(0, df['Vaccined'].max() + 1, 1))

plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'./plots/{datetime_prefix}vaccinations.png', dpi=300)
plt.close()


# Plot with total differences
plt.figure(figsize=(12, 8))
df['Total'] = df['Susceptible'] + df['Infected'] + df['Recovered']
df['Delta'] = df['Total'].diff()

plt.plot(df['Day'], df['Delta'], label="Zmiana liczebności populacji", color='black')

plt.title("Wykres zmiany liczebności populacji")
plt.xlabel("Dzień")
plt.xticks(xticks)
plt.ylabel("Różnica w liczbie osób")
plt.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(f'./plots/{datetime_prefix}total-delta.png', dpi=300)
plt.close()


# Plot with total sum
df['Total'] = df['Susceptible'] + df['Infected'] + df['Recovered']

plt.figure(figsize=(12, 8))
plt.plot(df['Day'], df['Total'], label="Liczebność", color='Purple')


plt.title("Wykres całkowitej liczebności populacji")
plt.xlabel("Dzień")
plt.xticks(xticks)
plt.ylabel("Liczba osób")
plt.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(f'./plots/{datetime_prefix}total-sum.png', dpi=300)
plt.close()


# Plot with count difference
df['Susceptible_D'] = df['Susceptible'].diff()
df['Infected_D'] = df['Infected'].diff()
df['Recovered_D'] = df['Recovered'].diff()

plt.figure(figsize=(12, 8))
plt.plot(df['Day'], df['Susceptible_D'], label="Podatni", color='blue')
plt.plot(df['Day'], df['Infected_D'], label="Zarażeni", color='red')
plt.plot(df['Day'], df['Recovered_D'], label="Wyzdrowiali", color='green')

plt.title("Wykres symulacji epidemii (zmiany liczby osób)")
plt.xlabel("Dzień")
plt.xticks(xticks)
plt.ylabel("Zmiana liczby osób")
plt.legend()
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(f'./plots/{datetime_prefix}total-counts-delta.png', dpi=300)
plt.close()