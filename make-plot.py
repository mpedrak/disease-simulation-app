import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('stats.csv')


# Plot with total counts
plt.figure(figsize=(12, 8))
plt.plot(df['Day'], df['Susceptible'], label="Podatni", color='blue')
plt.plot(df['Day'], df['Infected'], label="Zarażeni", color='red')
plt.plot(df['Day'], df['Recovered'], label="Wyzdrowiali", color='green')

plt.title("Wykres symulacji epidemii")
plt.xlabel("Dzień")
xticks = [1]
xticks.extend(range(df['Day'].max() // 20, df['Day'].max() + 1, df['Day'].max() // 20))
xticks[-1] = (df['Day'].max())
plt.xticks(xticks)
plt.ylabel("Liczba osób")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('stats-plot.png', dpi=300)
plt.close()


# Plot with percentages
df['Total'] = df['Susceptible'] + df['Infected'] + df['Recovered']
df['Susceptible_%'] = df['Susceptible'] / df['Total'] * 100
df['Infected_%'] = df['Infected'] / df['Total'] * 100
df['Recovered_%'] = df['Recovered'] / df['Total'] * 100

plt.figure(figsize=(12, 8))
plt.plot(df['Day'], df['Susceptible_%'], label="Podatni", color='blue')
plt.plot(df['Day'], df['Infected_%'], label="Zarażeni", color='red')
plt.plot(df['Day'], df['Recovered_%'], label="Wyzdrowiali", color='green')

plt.title("Wykres symulacji epidemii (wartości procentowe)")
plt.xlabel("Dzień")
plt.xticks(xticks)
plt.ylabel("Udział w populacji [%]")
plt.yticks(range(0, 101, 10))
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('stats-percent-plot.png', dpi=300)
plt.close()
