import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew

def skwness(col_name, df):
    # Calculate skewness
    skewness = skew(df[col_name])
    print(f"Skewness of {col_name}: {skewness:.4f}")
    
    # Plot histogram with KDE (to visualize skewness)
    sns.histplot(df[col_name], kde=True)
    plt.title(f'{col_name} Distribution')
    plt.xlabel(col_name)
    plt.ylabel('Frequency')
    plt.savefig(f'{col_name}_skewness.png', dpi=300)
    plt.close()

def boxBlot(col_name, df):
    sns.boxplot(y=df[col_name])
    plt.title(f'Boxplot of {col_name}')
    plt.savefig(f'{col_name}_boxplot.png', dpi=300)
    plt.close()

# Example usage:
# Assuming you have a pandas DataFrame called 'df'
# skwness('your_column_name', df)
# boxBlot('your_column_name', df)