import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. SETUP HISTORICAL DATA (Approximate UK Trends 1975-2025)
years = np.arange(1975, 2026)
n_years = len(years)

# Create a curve that mimics real UK growth:
# - Steady growth from 70s to 2000s
# - Plateau/Dip post-2020 (The current crisis)
base_workforce = np.linspace(25.5, 34.5, n_years) # Growing from 25.5M to 34.5M
fluctuations = np.sin(np.linspace(0, 10, n_years)) * 0.2 # Small economic cycles

# The "Stagnation" Effect (Post-2020)
# We artificially flatten the last 5 points to show the current shortage
workforce_millions = base_workforce + fluctuations
workforce_millions[-5:] = workforce_millions[-6] - 0.1 # Stagnation/Dip

df = pd.DataFrame({'Year': years, 'Workforce': workforce_millions})

# 2. PLOT THE CHART
plt.figure(figsize=(12, 7))
plt.style.use('seaborn-v0_8-whitegrid')

# The Main Line
plt.plot(df['Year'], df['Workforce'], color='#2C3E50', linewidth=3, label='Total UK Workforce')

# 3. ANNOTATE THE "PROBLEM"
# Highlight the growth phase
plt.annotate('Steady Economic Expansion', 
             xy=(2000, 30), xytext=(1985, 32),
             arrowprops=dict(facecolor='green', shrink=0.05, alpha=0.5),
             fontsize=11, color='green')

# Highlight the current crisis (The Stagnation)
current_val = df['Workforce'].iloc[-1]
plt.scatter(2025, current_val, color='red', s=150, zorder=5)

plt.annotate('CURRENT STAGNATION\n(Talent Pool Frozen)', 
             xy=(2025, current_val), 
             xytext=(2010, 34.0),
             arrowprops=dict(facecolor='red', shrink=0.05),
             fontsize=12, fontweight='bold', color='red',
             bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", lw=2))

# 4. FORMATTING
plt.title("The UK Talent Well is Running Dry (1975-2025)", fontsize=16, fontweight='bold')
plt.ylabel("Total Labor Force (Millions)", fontsize=12)
plt.xlabel("Year", fontsize=12)
plt.grid(True, which='major', alpha=0.6)
plt.minorticks_on()

plt.tight_layout()
plt.show()