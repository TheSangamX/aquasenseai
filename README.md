# 💧 AquaSense AI - Smart Reservoir Monitoring & Prediction System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)

An AI-powered dashboard for reservoir monitoring, analytics, and predictive insights.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Folder Structure](#folder-structure)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Data](#data)
7. [Technology Stack](#technology-stack)
8. [Contributing](#contributing)
9. [License](#license)
10. [Team](#team)
11. [Hackathon Presentation](#hackathon-presentation)

---

## 🌟 Project Overview

AquaSense AI is a comprehensive reservoir management system featuring:
- Real-time monitoring
- Advanced analytics
- AI predictions
- Risk assessment
- Professional visualizations

---

## ✨ Features

### 🏠 Home Dashboard
- Real-time reservoir status
- Interactive map visualization
- Key metrics and KPIs
- Reservoir comparison charts

### 📊 Analytics
- Historical trends
- Statistical summaries
- Distribution analysis
- Correlation studies

### 🤖 ML Predictions
- Linear Regression model
- Random Forest model
- Performance comparison
- Future level predictions
- Model evaluation metrics

### 🧠 Intelligent Analytics
- Reservoir Health Score
- Flood Risk Indicator
- Water Scarcity Indicator
- AI-generated insights
- Automatic recommendations

### ⚠️ Risk Assessment
- Flood/drought risk classification
- Risk heatmaps
- Alert notifications
- Actionable recommendations

### 📄 Reports
- Custom report generation
- Export to CSV/Excel
- Summary statistics
- Quick downloads

---

## 📁 Folder Structure

```
AquaSense-AI/
├── app.py                          # Main application entry
├── requirements.txt                # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   └── config.toml            # Theme & App Configuration
├── pages/                        # Streamlit multi-page app
│   ├── 1_🏠_Home.py
│   ├── 2_📊_Analytics.py
│   ├── 3_🤖_Predictions.py
│   ├── 4_⚠️_Risk_Assessment.py
│   ├── 5_📄_Reports.py
│   ├── 6_🧠_Intelligent_Analytics.py
│   └── 7_🤖_ML_Predictions.py
├── utils/                       # Utility functions
│   ├── __init__.py
│   ├── data_loader.py
│   ├── eda.py
│   ├── visualization.py
│   ├── prediction.py
│   ├── risk_assessment.py
│   └── helpers.py
├── notebooks/                  # Exploratory Data Analysis
│   ├── eda_plots/
│   └── complete_eda.py
│   ├── inspect_data.py
│   └── try_read_csv.py
└── assets/                     # Static assets
```

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (optional)

### Step 1: Clone or download
```bash
git clone <repository-url>
cd AquaSense-AI
```

### Step 2: Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Start the app
```bash
streamlit run app.py
```

The application will open in browser at http://localhost:8501

---

## 📊 Data

The dataset includes:
- Reservoir names
- Basin and subbasin info
- Date, month, year
- Latitude/longitude
- Full reservoir level
- Live capacity
- Storage levels

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Visualizations | Plotly |
| Data Manipulation | Pandas / NumPy |
| ML Models | Scikit-learn |
| Time Series | Pandas DateTime |

---

## 🎯 Features Breakdown

1. **Home Dashboard**: Quick overview of all reservoirs
2. **Analytics Page**: Detailed analysis
3. **Predictions**: AI predictions
4. **Risk Assessment**: Flood/drought risk
5. **Reports**: Generate reports
6. **Intelligent Analytics**: AI insights
7. **ML Predictions**: ML models

---

## 🚀 Deployment

### Local Deployment
```bash
streamlit run app.py
```

### Cloud Deployment (Streamlit Community Cloud)
1. Push to GitHub
2. Go to share.streamlit.io
3. Connect your repository
4. Select branch
5. Deploy!

### Docker Deployment
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

---

## 📋 Hackathon Presentation Outline

### Slide 1: Title
- AquaSense AI
- Team Name
- Hackathon Name
- Date

### Slide 2: Problem
- Current water management issues
- Climate change impact

### Slide 3: Solution
- What we built
- Key features

### Slides 4-6: Demo
- Dashboard walkthrough

### Slides 7-8: Tech
- Architecture
- Stack

### Slide 9: Impact
- How it helps
- Stakeholders

### Slides 10-11: Future
- Roadmap
- Next steps

### Slide 12: Thank You & Q&A

---

## 🤝 Contributing

Contributions welcome! Please feel free to open issues or submit pull requests.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🎉 Acknowledgments
Built for hackathons and open-source!
