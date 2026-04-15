# 🚀 Quick Start Guide - Segment Head Dashboard

## Launch the Application

```bash
cd /labs/user-b2473f16/lab1
streamlit run streamlit_app.py
```

## Demo Credentials

### Segment Head (Recommended for Testing)
- **Username:** `rachel`
- **Password:** `password123`

### Other Roles
- **Account Manager:** john.wicks / password123
- **Factory Head:** abhinav / password123

---

## 🎯 Segment Head Dashboard Features

Once logged in as the Segment Head, you'll find a powerful 3-tab dashboard:

### **Tab 1: 📊 Product Trends**
- **Multi-select Bearing Designations:** Choose one or more bearing types
  - 6205-2RS
  - 6206-ZZ
  - 6207-RS
- **Multi-select Customers:** Filter by customer
  - Mahindra Tractors
  - Sonalika
  - TAFE
- **Visualizations:**
  - Line charts showing trends over 6 months
  - Monthly volume heatmap by designation
  - Key metrics (Average, Peak, Min/Max volumes)
  - Growth percentage trends

### **Tab 2: 📈 Designation Analysis**
- **Deep Dive Analytics** for specific bearing designations
- **Monthly Statistics Table** with:
  - Total Volume
  - Average per Customer
  - Min/Max values
  - Customer Count
- **Growth Metrics:**
  - Overall growth trend %
  - Average monthly volume
  - Peak month volume
- **Per-Customer Breakdown** for the selected product
- **Visual Charts** (bar charts and trends)

### **Tab 3: 💡 Market Intelligence**
- **AI-Powered Insights** using OpenRouter API
- **Customer Performance Summary:**
  - Total Volume
  - Average Monthly Volume
  - Peak Volume
  - Months Tracked
- **Live Market Intelligence Cards** with:
  - Market insights and headlines
  - Growth percentage impact
  - Source attribution
  - Date created
- **Generate New Insights** with one click

---

## 📊 Sample Data Included

- **54 Sales Records** across 3 customers
- **6 Months of History:** October 2025 → March 2026
- **3 Bearing Designations:** 6205-2RS, 6206-ZZ, 6207-RS
- **3 Customers:** Mahindra, Sonalika, TAFE
- Shows realistic growth trends across all products

---

## ✨ Key Capabilities

✅ **Trend Analysis:** See volume trends per bearing type over multiple months
✅ **Team Filtering:** Multi-select customers to compare performance
✅ **Volume Metrics:** Monthly volume breakdown and heatmap views
✅ **Market Intelligence:** AI-powered insights about market conditions
✅ **Growth Tracking:** Automatic calculation of growth percentages
✅ **Export Ready:** Download data in CSV format
✅ **Professional UI:** Gradient designs, intuitive layouts
✅ **Zero Errors:** Thoroughly tested and validated

---

## 🔌 API Integration

The application uses **OpenRouter API** for real-time market intelligence generation:
- Model: Meta Llama 2 7B Chat
- Generates realistic growth insights
- Saves insights to database for future reference

---

## 💾 Database

SQLite database (`sop_platform.db`) includes:
- **users:** 3 demo accounts with different roles
- **customers:** 3 sample companies with regions and industries
- **sales_history:** 54 transactions with dates and volumes
- **forecast_lines:** Generated forecasts (empty initially)
- **market_intelligence:** AI-generated insights (created on demand)

---

## 🐛 Error Handling

The application includes:
- ✅ Input validation
- ✅ Error handling for API calls
- ✅ Database connection management
- ✅ Graceful fallbacks for missing data
- ✅ Session state management

---

## 📱 Browser Compatibility

Works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Tablet browsers
- Mobile browsers (Streamlit responsive design)

---

## 🎨 UI/UX Features

- **Gradient Backgrounds:** Purple, teal, and orange color schemes
- **Interactive Tabs:** Easy navigation between analytics views
- **Responsive Columns:** Adapts to screen size
- **Color-Coded Metrics:** Quick visual recognition
- **Charts & Visualizations:** Streamlit native charts
- **Custom HTML Styling:** Enhanced card designs
- **Emojis:** Visual indicators for quick understanding

---

## 📈 Next Steps

1. **Login** with rachel/password123
2. **Explore** the Product Trends tab to see all designations
3. **Filter** by specific customers for focused analysis
4. **Generate** market intelligence for any customer
5. **Analyze** growth trends and monthly patterns
6. **Download** data in CSV format for reports

---

**No React Components! Pure Streamlit! 🎉**
All state management handled natively by Streamlit's session state system.
