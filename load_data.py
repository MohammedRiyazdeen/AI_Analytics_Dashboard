"""
load_data.py - CSV to SQLite Loader
Reads the Zomato CSV, cleans the data, and loads it into a SQLite database.
"""

import pandas as pd
from sqlalchemy import create_engine
import re
import os


def extract_area_from_url(url):
    """Extract the area/locality name from the Zomato URL."""
    try:
        parts = url.split("/")
        if len(parts) >= 5:
            slug = parts[4]
            segments = slug.split("-")
            if len(segments) >= 2:
                return segments[-1]
        return "unknown"
    except Exception:
        return "unknown"


def extract_city_from_url(url):
    """Extract the city name from the Zomato URL."""
    try:
        parts = url.split("/")
        if len(parts) >= 4:
            return parts[3]
        return "unknown"
    except Exception:
        return "unknown"


def clean_and_load_data():
    """Read CSV, clean the data, and load into SQLite database."""
    
    csv_file = "zomata.csv"
    
    if not os.path.exists(csv_file):
        print(f"Error: '{csv_file}' not found in {os.getcwd()}")
        return
    
    # Step 1: Read CSV
    print("Step 1: Reading CSV file...")
    df = pd.read_csv(csv_file)
    print(f"  Loaded {len(df)} rows and {len(df.columns)} columns")
    print(f"  Original columns: {list(df.columns)}")
    
    # Step 2: Fix column names (lowercase, underscores)
    print("\nStep 2: Fixing column names...")
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "_", regex=True)
    )
    print(f"  New columns: {list(df.columns)}")
    
    # Step 3: Clean data types
    print("\nStep 3: Cleaning data...")
    df["ratings"] = pd.to_numeric(df["ratings"], errors="coerce")
    df["price_for_one"] = pd.to_numeric(df["price_for_one"], errors="coerce")
    
    null_ratings = df["ratings"].isna().sum()
    null_prices = df["price_for_one"].isna().sum()
    print(f"  Found {null_ratings} restaurants with no rating")
    print(f"  Found {null_prices} restaurants with no price")
    
    before = len(df)
    df = df.dropna(subset=["names"])
    after = len(df)
    print(f"  Dropped {before - after} rows with missing names")
    
    df["ratings"] = df["ratings"].fillna(0)
    df["price_for_one"] = df["price_for_one"].fillna(0)
    
    # Step 4: Extract city and area from URLs
    print("\nStep 4: Extracting city & area from URLs...")
    df["city"] = df["links"].apply(extract_city_from_url)
    df["area"] = df["links"].apply(extract_area_from_url)
    print(f"  Cities found: {df['city'].nunique()}")
    print(f"  Areas found: {df['area'].nunique()}")
    
    # Step 5: Create price categories
    print("\nStep 5: Creating price categories...")
    def categorize_price(price):
        if price <= 100:
            return "Budget (<=Rs.100)"
        elif price <= 200:
            return "Affordable (Rs.101-200)"
        elif price <= 350:
            return "Mid-Range (Rs.201-350)"
        else:
            return "Premium (Rs.350+)"
    
    df["price_category"] = df["price_for_one"].apply(categorize_price)
    print(f"  Price categories: {df['price_category'].value_counts().to_dict()}")
    
    # Step 6: Load into SQLite
    print("\nStep 6: Loading into SQLite database...")
    db_path = "dashboard.db"
    engine = create_engine(f"sqlite:///{db_path}")
    df.to_sql("restaurants", engine, if_exists="replace", index=False)
    
    saved_df = pd.read_sql("SELECT COUNT(*) as count FROM restaurants", engine)
    print(f"  Saved {saved_df['count'][0]} restaurants to '{db_path}'")
    
    # Print summary
    print("\n" + "=" * 60)
    print("  DATA LOADED SUCCESSFULLY")
    print("=" * 60)
    
    print(f"\n  Columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"    {i}. {col}")
    
    print(f"\n  First 5 rows:")
    print(df[["names", "ratings", "cuisine", "price_for_one", "city", "area", "price_category"]].head().to_string(index=False))
    
    print(f"\n  Stats:")
    print(f"    Total Restaurants: {len(df)}")
    print(f"    Avg Rating: {df[df['ratings'] > 0]['ratings'].mean():.1f}")
    print(f"    Avg Price: Rs.{df['price_for_one'].mean():.0f}")
    print(f"    Unique Cuisines: {df['cuisine'].nunique()}")
    
    print(f"\n  Database file: {os.path.abspath(db_path)}")
    print(f"  File size: {os.path.getsize(db_path) / 1024:.1f} KB")
    

if __name__ == "__main__":
    clean_and_load_data()
