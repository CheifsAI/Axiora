import matplotlib.pyplot as plt

# Data for the charts
categories = ['A', 'B', 'C', 'D']
values = [3, 7, 8, 5]

time = [1, 2, 3, 4, 5]
temperature = [30, 32, 34, 33, 31]

# Create the figure and axes for two charts
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Chart 1: Bar Chart
axes[0].bar(categories, values, color='skyblue')
axes[0].set_title("Bar Chart")
axes[0].set_xlabel("Categories")
axes[0].set_ylabel("Values")

# Chart 2: Line Chart
axes[1].plot(time, temperature, marker='o', color='red', linestyle='--')
axes[1].set_title("Line Chart")
axes[1].set_xlabel("Time")
axes[1].set_ylabel("Temperature")

# Adjust layout and display the charts
plt.tight_layout()
plt.show()
