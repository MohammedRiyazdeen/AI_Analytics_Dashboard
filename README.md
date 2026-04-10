# 📊 AI Data Analytics Dashboard

A fully interactive data analytics dashboard built with **Python** and **Streamlit** that lets you explore and analyze restaurant data from Hyderabad using dynamic charts, real-time filters, and powerful SQL queries displayed right on the screen.

---

## ✨ Features

- 🎛️ **Interactive Sidebar Filters** — Filter by area, cuisine type, price range, and rating
- 📊 **4 Dynamic Plotly Charts** — Bar charts, pie charts, and scatter plots that respond to filters in real time
- 📈 **4 KPI Metric Cards** — Total restaurants, average rating, top cuisine, and top area at a glance
- 🔬 **5 SQL Queries with Results** — Real SQL queries shown in code blocks with live results (proves SQL skills on screen)
- 📋 **Sortable Data Table** — Browse, sort and explore the full filtered dataset
- 📥 **CSV Download** — Download the currently filtered dataset as a CSV file
- 📂 **Data Overview** — Expandable raw data preview with row/column counts
- 🎨 **Professional Theming** — Clean, polished UI with custom Streamlit theme
- 🔄 **One-Click Reset** — Reset all filters instantly

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python** | Core programming language |
| **Pandas** | Data cleaning, manipulation and analysis |
| **Streamlit** | Web dashboard framework |
| **SQLite** | Lightweight database for structured queries |
| **SQLAlchemy** | Database connection and query execution |
| **Plotly** | Interactive data visualizations |

---

## 📁 Dataset

This project uses the **Zomato Hyderabad Restaurants** dataset containing **658 restaurants** with information about restaurant names, ratings, cuisines, prices, and locations.

🔗 **Source:** [Zomato Dataset on Kaggle](https://www.kaggle.com/datasets)

### Columns:
- `names` — Restaurant name
- `ratings` — Rating (0–5 scale)
- `cuisine` — Comma-separated cuisine types
- `price_for_one` — Average price per person (₹)
- `area` — Locality in Hyderabad
- `price_category` — Budget / Mid-Range / Premium / Fine Dining

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10 or higher installed on your machine

### Step-by-step

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AI_Analytics_Dashboard.git
cd AI_Analytics_Dashboard

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Load the data into SQLite database
python load_data.py

# 6. Run the dashboard
python -m streamlit run app.py
```

The dashboard will open automatically at **http://localhost:8501** 🎉

---

## 📸 Screenshots

> 📌 **Add your dashboard screenshots here!**
>
> Take a screenshot of your running dashboard and replace this section.
> A README with real screenshots looks 10x more professional on GitHub.

<!-- Example: -->
<!-- ![Dashboard Overview](screenshots/dashboard.png) -->
<!-- ![SQL Queries](screenshots/sql_queries.png) -->

---

## 📂 Project Structure

```
AI_Analytics_Dashboard/
├── app.py              # Main Streamlit dashboard
├── load_data.py        # Data pipeline: CSV → SQLite
├── explore.py          # SQL exploration queries
├── ai_service.py       # AI text-to-SQL service
├── zomata.csv          # Raw dataset
├── dashboard.db        # SQLite database (auto-generated)
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
├── .gitignore          # Git ignore rules
├── .streamlit/
│   └── config.toml     # Streamlit theme configuration
└── venv/               # Virtual environment (not tracked)
```

---

## 👨‍💻 Built By

**Riyaz** — Data Analytics & Python Developer

---

## 📝 License

This project is open source and available for educational purposes.
