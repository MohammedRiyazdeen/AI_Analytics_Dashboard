"""
📦 load_data.py — CSV to SQLite Loader
=======================================
This script reads the Zomato CSV, cleans it, and loads it into a SQLite database.

WHY DO WE NEED THIS?
---------------------
- CSV files are flat files — you can't run SQL queries on them
- SQLite is a lightweight database that lives as a single .db file
- Once data is in SQLite, we can:
  1. Run SQL queries (SELECT, WHERE, GROUP BY, etc.)
  2. Let the AI convert English questions → SQL queries
  3. Filter and aggregate data fast

HOW IT WORKS (Step by Step):
-----------------------------
Step 1: Read the CSV file using pandas (a Python data library)
Step 2: Clean the data (fix column names, remove bad rows, fix data types)
Step 3: Extract extra info (like area/location from the URL)
Step 4: Save everything into a SQLite database file (dashboard.db)
Step 5: Print sample data so we can verify it worked
"""

import pandas as pd
from sqlalchemy import create_engine
import re
import os


def extract_area_from_url(url):
    """
    🔍 Extract the area/locality name from the Zomato URL.
    
    Example:
        Input:  "https://www.zomato.com/hyderabad/kfc-abids/order"
        Output: "abids"
    
    WHY? The CSV doesn't have a separate "area" column, but the URL contains
    the locality name! We extract it to create a useful filter for the dashboard.
    """
    try:
        # Split URL by '/' and get the restaurant part (e.g., "kfc-abids")
        parts = url.split("/")
        # The restaurant slug is usually the 4th part (index 4)
        if len(parts) >= 5:
            slug = parts[4]  # e.g., "kfc-abids"
            # The area is usually the LAST part after the last hyphen
            # But restaurant names can have hyphens too, so we take the last segment
            segments = slug.split("-")
            if len(segments) >= 2:
                return segments[-1]  # e.g., "abids"
        return "unknown"
    except Exception:
        return "unknown"


def extract_city_from_url(url):
    """
    🏙️ Extract the city name from the Zomato URL.
    
    Example:
        Input:  "https://www.zomato.com/hyderabad/kfc-abids/order"
        Output: "hyderabad"
    """
    try:
        parts = url.split("/")
        if len(parts) >= 4:
            return parts[3]  # e.g., "hyderabad"
        return "unknown"
    except Exception:
        return "unknown"


def clean_and_load_data():
    """
    🧹 Main function that reads, cleans, and loads data into SQLite.
    
    WHAT EACH STEP DOES:
    --------------------
    """
    
    # ─── STEP 1: Read the CSV ─────────────────────────────────────
    # pandas.read_csv() reads a CSV file and creates a "DataFrame" 
    # (think of it as a spreadsheet/table in Python)
    
    csv_file = "zomata.csv"  # Your file name
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: '{csv_file}' not found!")
        print(f"   Make sure the CSV file is in: {os.getcwd()}")
        return
    
    print("📂 Step 1: Reading CSV file...")
    df = pd.read_csv(csv_file)
    print(f"   ✅ Loaded {len(df)} rows and {len(df.columns)} columns")
    print(f"   Original columns: {list(df.columns)}")
    
    
    # ─── STEP 2: Fix Column Names ─────────────────────────────────
    # Why? Column names like "price for one" have spaces — that causes
    # problems in SQL queries. We replace spaces with underscores and
    # make everything lowercase.
    # "price for one" → "price_for_one"
    
    print("\n🔧 Step 2: Fixing column names...")
    df.columns = (
        df.columns
        .str.strip()              # Remove leading/trailing spaces
        .str.lower()              # Make lowercase
        .str.replace(" ", "_")    # Replace spaces with underscores
        .str.replace(r"[^\w]", "_", regex=True)  # Remove special chars
    )
    print(f"   ✅ New columns: {list(df.columns)}")
    
    
    # ─── STEP 3: Clean the Data ───────────────────────────────────
    # - Some ratings are "New" or "-" (not numbers) → we fix those
    # - Some rows might have missing values → we handle them
    
    print("\n🧹 Step 3: Cleaning data...")
    
    # Convert ratings to numbers. "New" and "-" become NaN (Not a Number)
    df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
    # errors="coerce" means: if a value can't be converted, make it NaN
    
    # Convert price to numbers (in case there are any non-numeric values)
    df["price_for_one"] = pd.to_numeric(df["price_for_one"], errors="coerce")
    
    # Count how many bad values we found
    null_ratings = df["ratings"].isna().sum()
    null_prices = df["price_for_one"].isna().sum()
    print(f"   Found {null_ratings} restaurants with no rating (New/-)")
    print(f"   Found {null_prices} restaurants with no price")
    
    # Drop rows where BOTH rating AND price are missing
    before = len(df)
    df = df.dropna(subset=["names"])  # At minimum, must have a name
    after = len(df)
    print(f"   Dropped {before - after} rows with missing names")
    
    # Fill missing ratings with 0 (we'll mark them as "Unrated" in dashboard)
    df["ratings"] = df["ratings"].fillna(0)
    df["price_for_one"] = df["price_for_one"].fillna(0)
    
    
    # ─── STEP 4: Extract Extra Info ───────────────────────────────
    # We extract city and area from the URL to create useful filters
    
    print("\n🌍 Step 4: Extracting city & area from URLs...")
    df["city"] = df["links"].apply(extract_city_from_url)
    df["area"] = df["links"].apply(extract_area_from_url)
    print(f"   ✅ Cities found: {df['city'].nunique()}")
    print(f"   ✅ Areas found: {df['area'].nunique()}")
    
    
    # ─── STEP 5: Create a Price Category Column ──────────────────
    # This groups prices into categories for easier filtering
    
    print("\n💰 Step 5: Creating price categories...")
    def categorize_price(price):
        if price <= 100:
            return "Budget (≤₹100)"
        elif price <= 200:
            return "Affordable (₹101-200)"
        elif price <= 350:
            return "Mid-Range (₹201-350)"
        else:
            return "Premium (₹350+)"
    
    df["price_category"] = df["price_for_one"].apply(categorize_price)
    print(f"   ✅ Price categories: {df['price_category'].value_counts().to_dict()}")
    
    
    # ─── STEP 6: Load into SQLite ─────────────────────────────────
    # SQLAlchemy's create_engine() creates a connection to the database.
    # "sqlite:///dashboard.db" means: create/connect to a file called dashboard.db
    # df.to_sql() takes the DataFrame and writes it as a SQL table.
    
    print("\n💾 Step 6: Loading into SQLite database...")
    db_path = "dashboard.db"
    engine = create_engine(f"sqlite:///{db_path}")
    
    # if_exists="replace" → if table already exists, overwrite it
    # index=False → don't save the pandas index as a column
    df.to_sql("restaurants", engine, if_exists="replace", index=False)
    
    # Verify the data was saved
    saved_df = pd.read_sql("SELECT COUNT(*) as count FROM restaurants", engine)
    print(f"   ✅ Saved {saved_df['count'][0]} restaurants to '{db_path}'")
    
    
    # ─── STEP 7: Print Results ────────────────────────────────────
    print("\n" + "=" * 60)
    print("📊 DATA LOADED SUCCESSFULLY!")
    print("=" * 60)
    
    print(f"\n📋 Final Column Names (SAVE THESE — needed for AI queries):")
    print("-" * 40)
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col}")
    
    print(f"\n📝 First 5 Rows:")
    print("-" * 40)
    # Show first 5 rows without the links column (too long to display)
    print(df[["names", "ratings", "cuisine", "price_for_one", "city", "area", "price_category"]].head().to_string(index=False))
    
    print(f"\n📈 Quick Stats:")
    print("-" * 40)
    print(f"   Total Restaurants: {len(df)}")
    print(f"   Avg Rating: {df[df['ratings'] > 0]['ratings'].mean():.1f}")
    print(f"   Avg Price for One: ₹{df['price_for_one'].mean():.0f}")
    print(f"   Unique Cuisines: {df['cuisine'].nunique()}")
    print(f"   Top Areas: {', '.join(df['area'].value_counts().head(5).index.tolist())}")
    
    print(f"\n✅ Database file created: {os.path.abspath(db_path)}")
    print(f"   File size: {os.path.getsize(db_path) / 1024:.1f} KB")
    

if __name__ == "__main__":
    clean_and_load_data()
