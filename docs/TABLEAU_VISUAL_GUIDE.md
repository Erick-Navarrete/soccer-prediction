# Tableau Visual Creation Guide for Soccer Predictions (4/29/2026)

## 📊 Your Data is Ready!

**Data Location:** `D:\Project_App\soccer-prediction\outputs\tableau_data\`

**Available Files:**
- `match_predictions.csv` - Today's 10 match predictions with full details
- `team_performance_trends.csv` - Team statistics and rankings
- `model_performance.csv` - Overall model accuracy metrics
- `confidence_intervals.csv` - Prediction confidence analysis

---

## 🎯 Step-by-Step Guide to Create Tableau Visuals

### **Step 1: Open Tableau Desktop & Connect to Data**

1. **Launch Tableau Desktop**
2. **Connect to Data Source:**
   - Click "Connect" → "Text File"
   - Navigate to: `D:\Project_App\soccer-prediction\outputs\tableau_data\`
   - Select `match_predictions.csv`
   - Click "Open"

3. **Verify Connection:**
   - You should see 10 rows of data (today's matches)
   - Date field should show "2026-04-29"
   - All 20 Premier League teams should be present

---

### **Step 2: Create Your First Visualization - Match Overview**

**Create a Match Summary Table:**

1. **Drag "date" to Columns** → Convert to "DAY(date)" for better display
2. **Drag "home_team" to Rows**
3. **Drag "away_team" to Rows** (right next to home_team)
4. **Drag "prediction_text" to "Text" in Marks card**
5. **Drag "confidence_level" to "Color" in Marks card**

**Result:** A color-coded table showing all today's matches with predictions!

---

### **Step 3: Create Probability Bar Chart**

**Visualize Win Probabilities:**

1. **Create New Worksheet** (right-click → New Worksheet)
2. **Drag "home_team" to Columns**
3. **Drag "home_win_pct" to Rows** (this creates a bar chart)
4. **Drag "away_team" to "Color"** (shows opponent)
5. **Drag "prediction_text" to "Label"** (shows predicted result)

**Enhancement:** Add reference lines:
- Right-click on axis → "Add Reference Line"
- Set at 50% to show even probability

---

### **Step 4: Create Team Performance Dashboard**

**Connect to Team Performance Data:**

1. **Add New Data Source:**
   - Data → New Data Source → Text File
   - Select `team_performance_trends.csv`

2. **Create Team Rankings:**
   - Drag "team" to Rows
   - Drag "overall_strength" to Columns
   - Sort descending (strongest teams first)
   - Drag "recent_form" to "Tooltip"

---

### **Step 5: Build Interactive Dashboard**

**Create Your Main Dashboard:**

1. **Create New Dashboard** (right-click → New Dashboard)
2. **Set Size:** 1280 x 720 pixels
3. **Add Your Worksheets:**
   - Drag "Match Overview" to top-left
   - Drag "Probability Bar Chart" to top-right
   - Drag "Team Rankings" to bottom

4. **Add Filters:**
   - Drag "confidence_level" from Data pane to dashboard
   - Select "High" to see only confident predictions

---

### **Step 6: Create Model Performance Visualization**

**Show Model Accuracy:**

1. **Connect to `model_performance.csv`**
2. **Create Big Number Display:**
   - Drag "accuracy_percent" to "Text"
   - Format as percentage with 1 decimal
   - Add title: "Today's Model Accuracy"

3. **Create Confidence Breakdown:**
   - Drag "confidence_level" to Columns
   - Drag "prediction_correct" to Rows (change to COUNT)
   - Change mark type to "Bar"
   - Add labels to show counts

---

## 🎨 Advanced Visualizations

### **Heat Map: Team vs Team Matrix**

1. **Drag "home_team" to Columns**
2. **Drag "away_team" to Rows**
3. **Drag "prediction_correct" to "Color"
4. **Change mark type to "Square"**
5. **Add "prediction_text" to "Label"**

### **Scatter Plot: Probability Analysis**

1. **Drag "home_win_pct" to Columns**
2. **Drag "away_win_pct" to Rows**
3. **Drag "prediction_text" to "Color"**
4. **Drag "home_team" to "Label"**
5. **Add trend line if desired**

### **Gauge Chart: Confidence Levels**

1. **Create calculated field:** `IF [confidence_level] = 'High' THEN 1 ELSEIF [confidence_level] = 'Medium' THEN 0.5 ELSE 0 END`
2. **Use this field to create a gauge showing prediction confidence distribution**

---

## 🔧 Pro Tips for Your Soccer Dashboard

### **1. Use Color Effectively**
- **Green:** Home Win predictions
- **Red:** Away Win predictions
- **Yellow:** Draw predictions
- **Opacity:** Based on confidence level

### **2. Add Interactivity**
- **Filters:** Date, League, Confidence Level
- **Actions:** Click on a team to filter all views
- **Tooltips:** Add detailed probability breakdowns

### **3. Create Calculated Fields**
```tableau
// High Confidence Home Wins
IF [confidence_level] = 'High' AND [prediction] = 2 THEN 'High Conf Home Win'
ELSE 'Other'
END

// Upset Alert (Low confidence favorite)
IF [confidence_level] = 'Low' AND [home_win_pct] > 60 THEN 'Potential Upset'
ELSE 'Standard'
END
```

### **4. Format for Professional Look**
- **Fonts:** Use Tableau Sans or Arial
- **Colors:** Professional palette (blues, greens, grays)
- **Gridlines:** Minimal or removed
- **Titles:** Clear and descriptive

---

## 📱 Today's Data Highlights (4/29/2026)

**Key Matches to Watch:**
- **Arsenal vs Chelsea** (44.9% Home Win, Low confidence)
- **Man City vs Liverpool** (43.8% Home Win, Low confidence)
- **Brighton vs Aston Villa** (65.0% Home Win, Medium confidence)

**Model Performance:**
- **Overall Accuracy:** 70.0%
- **Total Predictions:** 10 matches
- **High Confidence:** 0 matches
- **Medium Confidence:** 5 matches
- **Low Confidence:** 5 matches

**Top Teams by Overall Strength:**
1. Brighton (64.97% home strength)
2. Bournemouth (67.03% home strength)
3. Newcastle (51.65% home strength)

---

## 🚀 Next Steps

1. **Open Tableau Desktop** and connect to your new data
2. **Build the visualizations** following the steps above
3. **Customize colors and formatting** to match your preferences
4. **Add filters and interactivity** for better user experience
5. **Save your workbook** as `Soccer_Predictions_2026-04-29.twb`

---

## 💡 Troubleshooting

**Issue:** Data not showing correctly
- **Solution:** Verify date format in Tableau (should be 2026-04-29)

**Issue:** Percentages showing as decimals
- **Solution:** Right-click field → Format → Percentage → 1 decimal

**Issue:** Colors not displaying
- **Solution:** Check Color palette in Marks card → Edit Colors

**Issue:** Want to update data tomorrow
- **Solution:** Run `python generate_todays_data.py` again for fresh predictions

---

## 📞 Need Help?

Your data is ready and waiting in Tableau! Start with the simple visualizations and work your way up to the advanced ones. The key is to experiment with different chart types and find what tells the best story for your soccer predictions.

**Happy Visualizing! ⚽**