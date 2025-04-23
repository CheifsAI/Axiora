import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew

def skwness(col_name, df):
    skewness = skew(df[col_name])
    print(f"Skewness of {col_name}: {skewness:.4f}")
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

def col_desc(col_name,df):
    describtion = df.describe()[[col_name]]
    return describtion