
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1️⃣ تحميل البيانات
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")

# إنشاء الشكل والمحاور
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle("Combined Data Analysis")

# 1️⃣ شارت الأعمدة للأهداف المسجلة
if "Home Team Name" in df.columns and "Home Team Goals" in df.columns:
    data = df.groupby("Home Team Name")["Home Team Goals"].sum().sort_values(ascending=False)
    sns.barplot(x=data.index[:10], y=data.values[:10], ax=axes[0, 0], palette="Blues")
    axes[0, 0].set_title("Most Goals Scored as Home Team")
    axes[0, 0].set_xticklabels(data.index[:10], rotation=45)

# 2️⃣ شارت الخط الزمني
if "Year" in df.columns and "Home Team Goals" in df.columns:
    data = df.groupby("Year")["Home Team Goals"].sum()
    sns.lineplot(x=data.index, y=data.values, ax=axes[0, 1], marker="o", color="r")
    axes[0, 1].set_title("Goals Scored Over the Years")

# 3️⃣ شارت الانتشار للعلاقة بين عمودين رقميين
numerical_cols = df.select_dtypes(include=['number']).columns
if len(numerical_cols) >= 2:
    sns.scatterplot(x=df[numerical_cols[0]], y=df[numerical_cols[1]], ax=axes[1, 0], alpha=0.5, color="g")
    axes[1, 0].set_title(f"Correlation between {numerical_cols[0]} and {numerical_cols[1]}")

# 4️⃣ شارت التوزيع
if len(numerical_cols) >= 1:
    sns.histplot(df[numerical_cols[0]], ax=axes[1, 1], bins=20, kde=True, color="purple")
    axes[1, 1].set_title(f"Distribution of {numerical_cols[0]}")

# ضبط التخطيط وحفظ الصورة
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("combined_chart.png")
plt.show()

print("Combined chart generated as PNG: combined_chart.png")