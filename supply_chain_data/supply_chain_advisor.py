import pandas as pd
import tkinter as tk
from tkinter import scrolledtext
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Load the data
data = pd.read_csv('/content/drive/MyDrive/supply_chain_data.csv')

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

if __name__ == "__main__":
    recommendations = analyze_supply_chain()
    print("=" * 80)
    print("Supply Chain Recommendations")
    print("=" * 80)
    print(recommendations)
# output
"""================================================================================
Supply Chain Recommendations
================================================================================
⚠️ Inventory Alert: 14 products with critically low stock levels (<10). Consider replenishing:
- haircare (SKU: SKU2, Current Stock: 1)
- skincare (SKU: SKU4, Current Stock: 5)
- cosmetics (SKU: SKU8, Current Stock: 5)
- skincare (SKU: SKU15, Current Stock: 9)
- skincare (SKU: SKU16, Current Stock: 2)
- haircare (SKU: SKU24, Current Stock: 4)
- skincare (SKU: SKU31, Current Stock: 6)
- cosmetics (SKU: SKU33, Current Stock: 4)
- skincare (SKU: SKU34, Current Stock: 1)
- skincare (SKU: SKU47, Current Stock: 4)
- haircare (SKU: SKU57, Current Stock: 5)
- haircare (SKU: SKU68, Current Stock: 0)
- haircare (SKU: SKU78, Current Stock: 5)
- haircare (SKU: SKU87, Current Stock: 5)

🔧 Quality Issue: 32 products with high defect rates (>3%). Review these suppliers:
- skincare (SKU: SKU1, Supplier: Supplier 3, Defect Rate: 4.854068026%)
- haircare (SKU: SKU2, Supplier: Supplier 1, Defect Rate: 4.580592619%)
- skincare (SKU: SKU3, Supplier: Supplier 5, Defect Rate: 4.746648621%)
- skincare (SKU: SKU4, Supplier: Supplier 1, Defect Rate: 3.145579523%)
- skincare (SKU: SKU9, Supplier: Supplier 2, Defect Rate: 3.844614479%)
- skincare (SKU: SKU19, Supplier: Supplier 4, Defect Rate: 3.646450865%)
- skincare (SKU: SKU20, Supplier: Supplier 1, Defect Rate: 4.231416574%)
- haircare (SKU: SKU24, Supplier: Supplier 2, Defect Rate: 3.691310293%)
- haircare (SKU: SKU25, Supplier: Supplier 4, Defect Rate: 3.797231217%)
- cosmetics (SKU: SKU29, Supplier: Supplier 1, Defect Rate: 3.878098937%)
- cosmetics (SKU: SKU33, Supplier: Supplier 5, Defect Rate: 3.541046012%)
- skincare (SKU: SKU36, Supplier: Supplier 2, Defect Rate: 3.805533379%)
- skincare (SKU: SKU40, Supplier: Supplier 1, Defect Rate: 4.213269431%)
- skincare (SKU: SKU42, Supplier: Supplier 5, Defect Rate: 4.939255289%)
- haircare (SKU: SKU45, Supplier: Supplier 2, Defect Rate: 3.219604612%)
- haircare (SKU: SKU46, Supplier: Supplier 3, Defect Rate: 3.648610593%)
- cosmetics (SKU: SKU50, Supplier: Supplier 2, Defect Rate: 4.754800805%)
- haircare (SKU: SKU55, Supplier: Supplier 2, Defect Rate: 4.548919659%)
- haircare (SKU: SKU61, Supplier: Supplier 4, Defect Rate: 4.367470538%)
- skincare (SKU: SKU63, Supplier: Supplier 3, Defect Rate: 3.63284329%)
- skincare (SKU: SKU65, Supplier: Supplier 5, Defect Rate: 4.911095955%)
- skincare (SKU: SKU66, Supplier: Supplier 5, Defect Rate: 3.448063288%)
- cosmetics (SKU: SKU72, Supplier: Supplier 1, Defect Rate: 3.213329607%)
- cosmetics (SKU: SKU73, Supplier: Supplier 4, Defect Rate: 4.620546065%)
- haircare (SKU: SKU77, Supplier: Supplier 1, Defect Rate: 3.055141818%)
- haircare (SKU: SKU78, Supplier: Supplier 5, Defect Rate: 4.096881332%)
- skincare (SKU: SKU82, Supplier: Supplier 2, Defect Rate: 4.137877049%)
- haircare (SKU: SKU84, Supplier: Supplier 5, Defect Rate: 4.843456577%)
- haircare (SKU: SKU87, Supplier: Supplier 3, Defect Rate: 3.693737788%)
- haircare (SKU: SKU93, Supplier: Supplier 4, Defect Rate: 4.165781795%)
- cosmetics (SKU: SKU96, Supplier: Supplier 3, Defect Rate: 3.872047681%)
- haircare (SKU: SKU97, Supplier: Supplier 4, Defect Rate: 3.376237835%)

🐢 Slow Movers: 5 products with low sales (<50 units). Consider promotions or discontinuation:
- haircare (SKU: SKU2, Units Sold: 8)
- haircare (SKU: SKU45, Units Sold: 24)
- haircare (SKU: SKU48, Units Sold: 29)
- haircare (SKU: SKU70, Units Sold: 32)
- cosmetics (SKU: SKU85, Units Sold: 25)

🏭 Supplier Performance Issues:
               Defect rates  Supplier  Lead times  Manufacturing costs
Supplier name                                                         
Supplier 5         2.665408             14.722222            44.768243
Supplier 3         2.465786             14.333333            43.634121
Supplier 2         2.362750             16.227273            41.622514
Supplier 4         2.337397             17.000000            62.709727

🚨 Anomaly Detection: Found unusual patterns in these products that need investigation:
- skincare (SKU: SKU1)
- haircare (SKU: SKU2)
- cosmetics (SKU: SKU38)
- haircare (SKU: SKU78)
- cosmetics (SKU: SKU89)"""
