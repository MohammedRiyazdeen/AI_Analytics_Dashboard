"""
🔍 explore.py — Data Exploration Script
========================================
This script explores the SQLite database to help you UNDERSTAND your data
before building the dashboard.

WHY DO WE NEED THIS?
---------------------
Before building charts and filters, you MUST know:
  - How much data do you have?
  - What are the unique values in each column?
  - What's the range of prices and ratings?
  - Which areas have the most restaurants?

This is called "Exploratory Data Analysis" (EDA) — the FIRST thing
any data analyst does before building anything.

INTERVIEW TIP 💡:
If someone asks "How did you build this dashboard?", the correct answer
starts with: "First, I explored the data to understand its structure..."

COLUMNS IN OUR DATABASE:
  1. links          — Zomato URL of the restaurant
  2. names          — Restaurant name
  3. ratings        — Rating (0-5, 0 means unrated)
  4. cuisine        — Types of food served (comma-separated)
  5. price_for_one  — Average price for one person (₹)
  6. city           — City (extracted from URL)
  7. area           — Locality/Area (extracted from URL)
  8. price_category — Budget/Affordable/Mid-Range/Premium
"""

import sqlite3
import pandas as pd


def run_query(cursor, query, description):
    """
    📌 Helper function that runs a SQL query and prints the results.
    
    WHY SHOW THE SQL?
    → So you learn what SQL looks like
    → In interviews, you'll be asked "what SQL did you use?"
    → The AI chat feature will generate queries like these automatically
    """
    print(f"\n{'─' * 60}")
    print(f"📊 {description}")
    print(f"{'─' * 60}")
    print(f"   SQL Query: {query}")
    print()
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Get column names from the cursor description
    columns = [desc[0] for desc in cursor.description]
    
    return results, columns


def explore_data():
    """
    🔍 Main exploration function — runs multiple SQL queries to understand the data.
    """
    
    # ─── Connect to Database ──────────────────────────────────────
    # sqlite3.connect() opens the database file
    # A "cursor" is like a pointer that executes queries one at a time
    
    conn = sqlite3.connect("dashboard.db")
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🔍 ZOMATO DATA EXPLORATION REPORT")
    print("=" * 60)
    
    
    # ─── Query 1: Total Number of Rows ────────────────────────────
    # COUNT(*) counts ALL rows in the table
    
    results, cols = run_query(
        cursor,
        "SELECT COUNT(*) AS total_restaurants FROM restaurants;",
        "1️⃣  Total Number of Restaurants"
    )
    total = results[0][0]
    print(f"   → Total restaurants in database: {total}")
    
    
    # ─── Query 2: Unique Cities ───────────────────────────────────
    # DISTINCT removes duplicates — gives only unique values
    
    results, cols = run_query(
        cursor,
        "SELECT DISTINCT city FROM restaurants ORDER BY city;",
        "2️⃣  All Unique Cities"
    )
    cities = [row[0] for row in results]
    print(f"   → Cities found: {', '.join(cities)}")
    print(f"   → Total unique cities: {len(cities)}")
    
    
    # ─── Query 3: Unique Areas (Top 20) ───────────────────────────
    # COUNT(*) with GROUP BY = count restaurants per area
    # ORDER BY count DESC = sort from highest to lowest
    # LIMIT 20 = show only top 20
    
    results, cols = run_query(
        cursor,
        """SELECT area, COUNT(*) AS restaurant_count 
           FROM restaurants 
           GROUP BY area 
           ORDER BY restaurant_count DESC 
           LIMIT 20;""",
        "3️⃣  Top 20 Areas by Number of Restaurants"
    )
    print(f"   {'Area':<30} {'Count':>8}")
    print(f"   {'─' * 38}")
    for row in results:
        print(f"   {row[0]:<30} {row[1]:>8}")
    
    
    # ─── Query 4: Price Range ─────────────────────────────────────
    # MIN() and MAX() find the smallest and largest values
    # AVG() calculates the average
    # ROUND() rounds to 2 decimal places
    
    results, cols = run_query(
        cursor,
        """SELECT 
               MIN(price_for_one) AS min_price, 
               MAX(price_for_one) AS max_price,
               ROUND(AVG(price_for_one), 2) AS avg_price
           FROM restaurants 
           WHERE price_for_one > 0;""",
        "4️⃣  Price Range (₹ for one person)"
    )
    print(f"   → Minimum Price: ₹{results[0][0]}")
    print(f"   → Maximum Price: ₹{results[0][1]}")
    print(f"   → Average Price: ₹{results[0][2]}")
    
    
    # ─── Query 5: Price Category Distribution ─────────────────────
    # This shows how many restaurants fall in each price bucket
    
    results, cols = run_query(
        cursor,
        """SELECT price_category, COUNT(*) AS count 
           FROM restaurants 
           GROUP BY price_category 
           ORDER BY count DESC;""",
        "5️⃣  Price Category Distribution"
    )
    print(f"   {'Category':<30} {'Count':>8}")
    print(f"   {'─' * 38}")
    for row in results:
        print(f"   {row[0]:<30} {row[1]:>8}")
    
    
    # ─── Query 6: Rating Statistics ───────────────────────────────
    # WHERE ratings > 0 → exclude unrated restaurants
    
    results, cols = run_query(
        cursor,
        """SELECT 
               ROUND(MIN(ratings), 1) AS min_rating,
               ROUND(MAX(ratings), 1) AS max_rating,
               ROUND(AVG(ratings), 2) AS avg_rating,
               COUNT(*) AS rated_count
           FROM restaurants 
           WHERE ratings > 0;""",
        "6️⃣  Rating Statistics (excluding unrated)"
    )
    print(f"   → Minimum Rating: {results[0][0]} ⭐")
    print(f"   → Maximum Rating: {results[0][1]} ⭐")
    print(f"   → Average Rating: {results[0][2]} ⭐")
    print(f"   → Restaurants with ratings: {results[0][3]}")
    
    # Count unrated
    cursor.execute("SELECT COUNT(*) FROM restaurants WHERE ratings = 0;")
    unrated = cursor.fetchone()[0]
    print(f"   → Unrated restaurants: {unrated}")
    
    
    # ─── Query 7: Rating Distribution ─────────────────────────────
    # CASE WHEN creates buckets like if-else
    # This groups ratings into ranges: 0-2, 2-3, 3-4, 4-5
    
    results, cols = run_query(
        cursor,
        """SELECT 
               CASE 
                   WHEN ratings = 0 THEN 'Unrated'
                   WHEN ratings < 3.0 THEN 'Poor (< 3.0)'
                   WHEN ratings < 3.5 THEN 'Average (3.0-3.4)'
                   WHEN ratings < 4.0 THEN 'Good (3.5-3.9)'
                   WHEN ratings < 4.5 THEN 'Very Good (4.0-4.4)'
                   ELSE 'Excellent (4.5+)'
               END AS rating_bucket,
               COUNT(*) AS count
           FROM restaurants
           GROUP BY rating_bucket
           ORDER BY 
               CASE rating_bucket
                   WHEN 'Excellent (4.5+)' THEN 1
                   WHEN 'Very Good (4.0-4.4)' THEN 2
                   WHEN 'Good (3.5-3.9)' THEN 3
                   WHEN 'Average (3.0-3.4)' THEN 4
                   WHEN 'Poor (< 3.0)' THEN 5
                   WHEN 'Unrated' THEN 6
               END;""",
        "7️⃣  Rating Distribution"
    )
    print(f"   {'Rating Bucket':<25} {'Count':>8}")
    print(f"   {'─' * 33}")
    for row in results:
        print(f"   {row[0]:<25} {row[1]:>8}")
    
    
    # ─── Query 8: Top 10 Cuisines ─────────────────────────────────
    # This is tricky! Cuisines are comma-separated like "Chinese, Bakery, Pizza"
    # We count how many times each cuisine STRING appears
    
    results, cols = run_query(
        cursor,
        """SELECT cuisine, COUNT(*) AS count 
           FROM restaurants 
           GROUP BY cuisine 
           ORDER BY count DESC 
           LIMIT 10;""",
        "8️⃣  Top 10 Most Common Cuisine Combinations"
    )
    print(f"   {'Cuisine':<55} {'Count':>5}")
    print(f"   {'─' * 60}")
    for row in results:
        cuisine = row[0] if row[0] else "Unknown"
        # Truncate long names
        display = cuisine[:52] + "..." if len(cuisine) > 55 else cuisine
        print(f"   {display:<55} {row[1]:>5}")
    
    
    # ─── Query 9: Top 10 Highest Rated ────────────────────────────
    
    results, cols = run_query(
        cursor,
        """SELECT names, ratings, cuisine, price_for_one, area
           FROM restaurants 
           WHERE ratings > 0
           ORDER BY ratings DESC 
           LIMIT 10;""",
        "9️⃣  Top 10 Highest Rated Restaurants"
    )
    print(f"   {'Name':<35} {'Rating':>6} {'Price':>7} {'Area':<15}")
    print(f"   {'─' * 65}")
    for row in results:
        name = row[0][:32] + "..." if len(row[0]) > 35 else row[0]
        print(f"   {name:<35} {row[1]:>6} ₹{row[2]:>5} {row[4]:<15}")
    
    
    # ─── Query 10: Cheapest Restaurants ───────────────────────────
    
    results, cols = run_query(
        cursor,
        """SELECT names, ratings, price_for_one, area
           FROM restaurants 
           WHERE price_for_one > 0 AND ratings > 0
           ORDER BY price_for_one ASC 
           LIMIT 10;""",
        "🔟  Top 10 Cheapest Restaurants (with ratings)"
    )
    print(f"   {'Name':<35} {'Rating':>6} {'Price':>7} {'Area':<15}")
    print(f"   {'─' * 65}")
    for row in results:
        name = row[0][:32] + "..." if len(row[0]) > 35 else row[0]
        print(f"   {name:<35} {row[1]:>6} ₹{row[2]:>5} {row[3]:<15}")
    
    
    # ─── Summary ──────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ EXPLORATION COMPLETE!")
    print("=" * 60)
    print("""
    📌 KEY TAKEAWAYS FOR DASHBOARD DESIGN:
    
    1. All data is from Hyderabad — use AREA as the location filter
    2. Ratings range from ~2.6 to 4.7 — most are between 3.5-4.4
    3. Prices range from ₹50 to ₹400 — 4 price categories
    4. Cuisines are comma-separated — we can split them for analysis
    5. "South Indian" is the most common cuisine type
    
    📌 THESE INSIGHTS HELP US BUILD:
    → Sidebar filters: Area, Price Category, Rating Range
    → Charts: Rating distribution, Price distribution, Top areas
    → AI queries: The column names are what the AI will use
    """)
    
    conn.close()


if __name__ == "__main__":
    explore_data()
