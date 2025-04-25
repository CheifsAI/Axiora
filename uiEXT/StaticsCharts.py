import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew

def skwness(col_name, df):
    fig, ax = plt.subplots(figsize=(6, 4))
    skewness = skew(df[col_name])
    print(f"Skewness of {col_name}: {skewness:.4f}")
    sns.histplot(df[col_name], kde=True, ax=ax)
    ax.set_title(f'{col_name} Distribution')
    ax.set_xlabel(col_name)
    ax.set_ylabel('Frequency')
    plt.tight_layout()
    return fig

def boxBlot(col_name, df):
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(y=df[col_name], ax=ax)
    ax.set_title(f'Boxplot of {col_name}')
    plt.tight_layout()
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
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'Correlation plot not available\nfor non-numeric columns',
                ha='center', va='center', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.tight_layout()
        return fig
    
    # Calculate correlation only for numeric columns
    correlation_matrix = df[numeric_cols].corr()
    target_corr = correlation_matrix[[col_name]].drop(col_name)

    if len(target_corr) == 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No other numeric columns\nto calculate correlations',
                ha='center', va='center', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        # Calculate figure height based on number of columns
        num_cols = len(target_corr)
        fig_height = max(4, min(8, 0.4 * num_cols))  # Reduced height per column
        
        # Create figure with calculated height
        fig, ax = plt.subplots(figsize=(8, fig_height))
        
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
                   fontsize=9)  # Slightly smaller font
        
        # Adjust layout
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('Correlation Coefficient')
        
        # Set reasonable x-axis limits
        max_abs_corr = max(abs(target_corr_sorted[col_name].max()), 
                          abs(target_corr_sorted[col_name].min()))
        ax.set_xlim(-max(0.1, max_abs_corr * 1.2), max(0.1, max_abs_corr * 1.2))
        
        # Adjust margins and spacing
        plt.subplots_adjust(left=0.25, right=0.95, top=0.95, bottom=0.1)
        
        # Reduce font size of y-axis labels if there are many columns
        if num_cols > 10:
            ax.tick_params(axis='y', labelsize=8)
    
    return fig