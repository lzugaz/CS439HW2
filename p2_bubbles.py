import pandas as pd
import matplotlib.pyplot as plt
import argparse

def create_bubble_chart(df):
    x_attr = "GDP_per_capita"
    y_attr = "military_expenditures"
    size_attr = "population"
    color_attr = "life_expectancy"

    x = df[x_attr]
    y = df[y_attr]
    
    min_val = df[size_attr].min()
    max_val = df[size_attr].max()
    value_range = max_val - min_val 

    min_size = 10 
    max_size = 2000
    size_range = max_size - min_size 
    
    K = size_range / value_range 
    sizes = min_size + K * (df[size_attr] - min_val)
    colors = df[color_attr]

    plt.figure(figsize=(12, 8))
    
    scatter = plt.scatter(x, y, s=sizes, c=colors, cmap='viridis', alpha=0.6, edgecolors="w", linewidth=0.5)

    cbar = plt.colorbar(scatter)
    cbar.set_label(color_attr)

    legend_sizes = [1e5, 1e7, 1e9] 
    legend_bubbles = [min_size + K * (s - min_val) for s in legend_sizes]
    
    for size, legend_bubble in zip(legend_sizes, legend_bubbles):
        plt.scatter([], [], s=legend_bubble, c='gray', alpha=0.6, edgecolors="w", label=f'{size:.1e}')
    
    plt.legend(scatterpoints=1, frameon=False, labelspacing=1, title='Population')

    plt.xlabel(x_attr)
    plt.ylabel(y_attr)
    plt.title(f'Bubble chart representation of {x_attr}, {y_attr}, {size_attr}, {color_attr}')
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a bubble chart from a CSV dataset.')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV filename')  # Only input is required now
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    
    create_bubble_chart(df)
