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

def col_corr(col_name,df):
    correlation_matrix = df.corr()
    target_corr = correlation_matrix[[col_name]].drop(col_name)

    # Sort and plot
    target_corr_sorted = target_corr.sort_values(col_name)
    target_corr_sorted.plot(kind='barh', title='Correlation with {col_name}')
    plt.show()