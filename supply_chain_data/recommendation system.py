import pandas as pd
import tkinter as tk
from tkinter import scrolledtext
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Load the data
data = pd.read_csv('supply_chain_data.csv')

def analyze_supply_chain():
    """Analyze the supply chain data and generate recommendations"""
    
    # Initialize recommendations
    recommendations = []
    
    # 1. Inventory Optimization Analysis
    low_stock = data[data['Stock levels'] < 10]
    if not low_stock.empty:
        rec = f"⚠️ Inventory Alert: {len(low_stock)} products with critically low stock levels (<10). Consider replenishing:\n"
        rec += "\n".join([f"- {row['Product type']} (SKU: {row['SKU']}, Current Stock: {row['Stock levels']})" 
                         for _, row in low_stock.iterrows()])
        recommendations.append(rec)
    
    # 2. High Defect Rate Products
    high_defect = data[data['Defect rates'] > 3]
    if not high_defect.empty:
        rec = f"🔧 Quality Issue: {len(high_defect)} products with high defect rates (>3%). Review these suppliers:\n"
        rec += "\n".join([f"- {row['Product type']} (SKU: {row['SKU']}, Supplier: {row['Supplier name']}, Defect Rate: {row['Defect rates']}%)" 
                         for _, row in high_defect.iterrows()])
        recommendations.append(rec)
    
    # 3. Slow Moving Products
    slow_moving = data[data['Number of products sold'] < 50]
    if not slow_moving.empty:
        rec = f"🐢 Slow Movers: {len(slow_moving)} products with low sales (<50 units). Consider promotions or discontinuation:\n"
        rec += "\n".join([f"- {row['Product type']} (SKU: {row['SKU']}, Units Sold: {row['Number of products sold']})" 
                         for _, row in slow_moving.iterrows()])
        recommendations.append(rec)
    
    # 4. High Cost Transportation
    high_transport = data[data['Shipping costs'] > 500]
    if not high_transport.empty:
        rec = f"🚛 High Shipping Costs: {len(high_transport)} products with shipping costs > $500. Optimize routes/carriers:\n"
        rec += "\n".join([f"- {row['Product type']} (SKU: {row['SKU']}, Carrier: {row['Shipping carriers']}, Cost: ${row['Shipping costs']:.2f})" 
                         for _, row in high_transport.iterrows()])
        recommendations.append(rec)
    
    # 5. Supplier Performance Analysis
    supplier_stats = data.groupby('Supplier name').agg({
        'Defect rates': 'mean',
        'Supplier  Lead times': 'mean',
        'Manufacturing costs': 'mean'
    }).sort_values('Defect rates', ascending=False)
    
    worst_suppliers = supplier_stats[supplier_stats['Defect rates'] > 2]
    if not worst_suppliers.empty:
        rec = "🏭 Supplier Performance Issues:\n"
        rec += worst_suppliers.to_string()
        recommendations.append(rec)
    
    # 6. Anomaly Detection
    numeric_cols = ['Price', 'Availability', 'Number of products sold', 'Revenue generated', 
                   'Stock levels', 'Supplier  Lead times', 'Shipping costs', 'Defect rates']
    anomaly_data = data[numeric_cols].dropna()
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(anomaly_data)
    
    model = IsolationForest(contamination=0.05)
    anomalies = model.fit_predict(scaled_data)
    anomaly_indices = anomalies == -1
    
    if any(anomaly_indices):
        anomaly_products = data.loc[anomaly_indices]
        rec = "🚨 Anomaly Detection: Found unusual patterns in these products that need investigation:\n"
        rec += "\n".join([f"- {row['Product type']} (SKU: {row['SKU']})" 
                         for _, row in anomaly_products.iterrows()])
        recommendations.append(rec)
    
    # If no specific issues found
    if not recommendations:
        return "✅ Supply chain appears healthy. No critical issues detected."
    
    return "\n\n".join(recommendations)

def generate_recommendations():
    """Generate and display recommendations"""
    recommendations = analyze_supply_chain()
    output_area.delete('1.0', tk.END)
    output_area.insert(tk.INSERT, recommendations)

# Create GUI
root = tk.Tk()
root.title("Supply Chain Optimization Advisor")
root.geometry("800x600")

# Title
title_label = tk.Label(root, text="Supply Chain Recommendations", font=("Arial", 16))
title_label.pack(pady=10)

# Button
generate_btn = tk.Button(root, text="Generate Recommendations", command=generate_recommendations, 
                        bg="#4CAF50", fg="white", font=("Arial", 12))
generate_btn.pack(pady=20)

# Output area
output_area = scrolledtext.ScrolledText(root, width=90, height=25, wrap=tk.WORD)
output_area.pack(padx=20, pady=10)

root.mainloop()
