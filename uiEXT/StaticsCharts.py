import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew

def skwness(col_name, df):
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    skewness = skew(df[col_name])
    print(f"Skewness of {col_name}: {skewness:.4f}")
    sns.histplot(df[col_name], kde=True, ax=ax)
    ax.set_title(f'{col_name} Distribution')
    ax.set_xlabel(col_name)
    ax.set_ylabel('Frequency')
    return fig

def boxBlot(col_name, df):
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    sns.boxplot(y=df[col_name], ax=ax)
    ax.set_title(f'Boxplot of {col_name}')
    return fig

def col_desc(col_name, df):
    description = df.describe()[[col_name]]
    return description

def col_corrBlot(col_name, df):
    # Get only numeric columns - include all numeric types
    numeric_cols = df.select_dtypes(include=['int16', 'int32', 'int64', 
                                           'float16', 'float32', 'float64']).columns
    
    # Check if the target column is numeric
    if not col_name in numeric_cols:
        fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
        ax.text(0.5, 0.5, 'Correlation plot not available\nfor non-numeric columns',
                ha='center', va='center', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig
    
    # Calculate correlation only for numeric columns
    correlation_matrix = df[numeric_cols].corr()
    target_corr = correlation_matrix[[col_name]].drop(col_name)

    if len(target_corr) == 0:
        fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
        ax.text(0.5, 0.5, 'No other numeric columns\nto calculate correlations',
                ha='center', va='center', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # Calculate figure height based on number of columns
        num_cols = len(target_corr)
        fig_height = max(6, 0.4 * num_cols)  # Allow figure to grow taller
        
        # Create figure with calculated height
        fig, ax = plt.subplots(figsize=(6, fig_height), constrained_layout=True)
        
        # Sort and plot
        target_corr_sorted = target_corr.sort_values(col_name, ascending=True)
        
        # Create color map based on correlation values
        colors = ['red' if x < 0 else 'blue' for x in target_corr_sorted[col_name]]
        
        # Plot bars
        bars = target_corr_sorted.plot(kind='barh', ax=ax, color=colors,
                                     title=f'Correlation with {col_name}')
        
        # Add value labels on the bars
        for i, v in enumerate(target_corr_sorted[col_name]):
            ax.text(v + (0.01 if v >= 0 else -0.01), 
                   i,
                   f'{v:.3f}',
                   va='center',
                   ha='left' if v >= 0 else 'right',
                   fontsize=9)
        
        # Adjust layout
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('Correlation Coefficient')
        
        # Set reasonable x-axis limits
        max_abs_corr = max(abs(target_corr_sorted[col_name].max()), 
                          abs(target_corr_sorted[col_name].min()))
        ax.set_xlim(-max(0.1, max_abs_corr * 1.2), max(0.1, max_abs_corr * 1.2))
        
        # Set consistent font sizes
        ax.tick_params(axis='y', labelsize=9)
        ax.tick_params(axis='x', labelsize=9)
        ax.set_title(ax.get_title(), fontsize=10, pad=10)
    
    return fig