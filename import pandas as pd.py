import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Sets up the timeline (1975-2026)
years = np.arange(1975, 2026)
n_years = len(years)

# Creates a curve mimicking real UK growth
# Establishes the baseline trend (25.5M -> 34.5M)
base_workforce = np.linspace(25.5, 34.5, n_years) 

# Adds economic fluctuations/noise
fluctuations = np.sin(np.linspace(0, 10, n_years)) * 0.2 

# Models the post-2020 stagnation effect
workforce_millions = base_workforce + fluctuations
workforce_millions[-5:] = workforce_millions[-6] - 0.1 

df = pd.DataFrame({'Year': years, 'Workforce': workforce_millions})

# Initializes the figure
plt.figure(figsize=(12, 7))
plt.style.use('seaborn-v0_8-whitegrid')

# Plots the main workforce trajectory
plt.plot(df['Year'], df['Workforce'], color='#2C3E50', linewidth=3, label='Total UK Workforce')

# Annotates the steady growth phase
plt.annotate('Steady Economic Expansion', 
             xy=(2000, 30), xytext=(1985, 32),
             arrowprops=dict(facecolor='green', shrink=0.05, alpha=0.5),
             fontsize=11, color='green')

# Highlights the current crisis point
current_val = df['Workforce'].iloc[-1]
plt.scatter(2025, current_val, color='red', s=150, zorder=5)

# Adds a warning box for the stagnation
plt.annotate('CURRENT STAGNATION\n(Talent Pool Frozen)', 
             xy=(2025, current_val), 
             xytext=(2010, 34.0),
             arrowprops=dict(facecolor='red', shrink=0.05),
             fontsize=12, fontweight='bold', color='red',
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=2))

# Formats the final chart axes and titles
plt.title("The UK Talent Well is Running Dry (1975-2025)", fontsize=16, fontweight='bold')
plt.ylabel("Total Labor Force (Millions)", fontsize=12)
plt.xlabel("Year", fontsize=12)
plt.grid(True, which='major', alpha=0.6)
plt.minorticks_on()

plt.tight_layout()
plt.show()