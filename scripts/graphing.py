import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = r"C:\Users\njsca\BGPResearch\SAV\false_positive_results\data.csv"
data = pd.read_csv(file_path)

# Filter data for the required outcome
filtered_data = data[(data['outcome'] == 'TRUE_NEGATIVE')]

# Pivot data to get values and yerr for each scenario label
plot_values = filtered_data.pivot_table(
    index='percent_adopt',
    columns='scenario_label',
    values='value'
)

plot_errors = filtered_data.pivot_table(
    index='percent_adopt',
    columns='scenario_label',
    values='yerr'
)

# Plotting the graph with error bars for each scenario label
plt.figure(figsize=(10, 6))
for scenario_label in plot_values.columns:
    plt.errorbar(
        plot_values.index, plot_values[scenario_label], yerr=plot_errors[scenario_label],
        label=scenario_label, capsize=3, marker='o', linestyle='-'
    )

# Customizing the plot
plt.xlabel("PERCENT ADOPTION")
plt.ylabel("VICTIM SUCCESS")
# plt.title("Value vs Percent Adopt for FALSE_NEGATIVE Outcomes by Scenario Label (with Confidence Intervals)")
plt.legend(title="Scenario Label")
plt.grid(True)
plt.show()
