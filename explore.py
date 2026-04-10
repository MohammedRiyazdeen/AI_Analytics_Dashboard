"""
explore.py - Data Exploration Script
Runs SQL queries against the database to understand the data structure.
"""

import sqlite3
import pandas as pd


def run_query(cursor, query, description):
    """Run a SQL query and print formatted results."""
    print(f"\n{'=' * 60}")
    print(f"  {description}")
    print(f"{'=' * 60}")
    print(f"  SQL: {query}")
    print()
    
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    return results, columns


def explore_data():
    """Run multiple SQL queries to explore the restaurant data."""
    
    conn = sqlite3.connect("dashboard.db")
    cursor = conn.cursor()
    
    print("=" * 60)
    print("  ZOMATO DATA EXPLORATION REPORT")
    print("=" * 60)
    
    # Query 1: Total rows
    results, cols = run_query(
        cursor,
        "SELECT COUNT(*) AS total_restaurants FROM restaurants;",
        "1. Total Number of Restaurants"
    )
    total = results[0][0]
    print(f"   Total restaurants in database: {total}")
    
    # Query 2: Unique cities
    results, cols = run_query(
        cursor,
        "SELECT DISTINCT city FROM restaurants ORDER BY city;",
        "2. All Unique Cities"
    )
    cities = [row[0] for row in results]
    print(f"   Cities found: {', '.join(cities)}")
    print(f"   Total unique cities: {len(cities)}")
    
    # Query 3: Top 20 areas by restaurant count
    results, cols = run_query(
        cursor,
        """SELECT area, COUNT(*) AS restaurant_count 
           FROM restaurants 
           GROUP BY area 
           ORDER BY restaurant_count DESC 
           LIMIT 20;""",
        "3. Top 20 Areas by Number of Restaurants"
    )
    print(f"   {'Area':<30} {'Count':>8}")
    print(f"   {'-' * 38}")
    for row in results:
        print(f"   {row[0]:<30} {row[1]:>8}")
    
    # Query 4: Price statistics
    results, cols = run_query(
        cursor,
        """SELECT 
               MIN(price_for_one) AS min_price, 
               MAX(price_for_one) AS max_price,
               ROUND(AVG(price_for_one), 2) AS avg_price
           FROM restaurants 
           WHERE price_for_one > 0;""",
        "4. Price Range (per person)"
    )
    print(f"   Minimum Price: Rs.{results[0][0]}")
    print(f"   Maximum Price: Rs.{results[0][1]}")
    print(f"   Average Price: Rs.{results[0][2]}")
    
    # Query 5: Price category distribution
    results, cols = run_query(
        cursor,
        """SELECT price_category, COUNT(*) AS count 
           FROM restaurants 
           GROUP BY price_category 
           ORDER BY count DESC;""",
        "5. Price Category Distribution"
    )
    print(f"   {'Category':<30} {'Count':>8}")
    print(f"   {'-' * 38}")
    for row in results:
        print(f"   {row[0]:<30} {row[1]:>8}")
    
    # Query 6: Rating statistics
    results, cols = run_query(
        cursor,
        """SELECT 
               ROUND(MIN(ratings), 1) AS min_rating,
               ROUND(MAX(ratings), 1) AS max_rating,
               ROUND(AVG(ratings), 2) AS avg_rating,
               COUNT(*) AS rated_count
           FROM restaurants 
           WHERE ratings > 0;""",
        "6. Rating Statistics (excluding unrated)"
    )
    print(f"   Minimum Rating: {results[0][0]}")
    print(f"   Maximum Rating: {results[0][1]}")
    print(f"   Average Rating: {results[0][2]}")
    print(f"   Restaurants with ratings: {results[0][3]}")
    
    cursor.execute("SELECT COUNT(*) FROM restaurants WHERE ratings = 0;")
    unrated = cursor.fetchone()[0]
    print(f"   Unrated restaurants: {unrated}")
    
    # Query 7: Rating distribution buckets
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
        "7. Rating Distribution"
    )
    print(f"   {'Rating Bucket':<25} {'Count':>8}")
    print(f"   {'-' * 33}")
    for row in results:
        print(f"   {row[0]:<25} {row[1]:>8}")
    
    # Query 8: Top 10 cuisine combinations
    results, cols = run_query(
        cursor,
        """SELECT cuisine, COUNT(*) AS count 
           FROM restaurants 
           GROUP BY cuisine 
           ORDER BY count DESC 
           LIMIT 10;""",
        "8. Top 10 Most Common Cuisine Combinations"
    )
    print(f"   {'Cuisine':<55} {'Count':>5}")
    print(f"   {'-' * 60}")
    for row in results:
        cuisine = row[0] if row[0] else "Unknown"
        display = cuisine[:52] + "..." if len(cuisine) > 55 else cuisine
        print(f"   {display:<55} {row[1]:>5}")
    
    # Query 9: Top 10 highest rated
    results, cols = run_query(
        cursor,
        """SELECT names, ratings, cuisine, price_for_one, area
           FROM restaurants 
           WHERE ratings > 0
           ORDER BY ratings DESC 
           LIMIT 10;""",
        "9. Top 10 Highest Rated Restaurants"
    )
    print(f"   {'Name':<35} {'Rating':>6} {'Price':>7} {'Area':<15}")
    print(f"   {'-' * 65}")
    for row in results:
        name = row[0][:32] + "..." if len(row[0]) > 35 else row[0]
        print(f"   {name:<35} {row[1]:>6} Rs.{row[2]:>4} {row[4]:<15}")
    
    # Query 10: Top 10 cheapest
    results, cols = run_query(
        cursor,
        """SELECT names, ratings, price_for_one, area
           FROM restaurants 
           WHERE price_for_one > 0 AND ratings > 0
           ORDER BY price_for_one ASC 
           LIMIT 10;""",
        "10. Top 10 Cheapest Restaurants (with ratings)"
    )
    print(f"   {'Name':<35} {'Rating':>6} {'Price':>7} {'Area':<15}")
    print(f"   {'-' * 65}")
    for row in results:
        name = row[0][:32] + "..." if len(row[0]) > 35 else row[0]
        print(f"   {name:<35} {row[1]:>6} Rs.{row[2]:>4} {row[3]:<15}")
    
    # Summary
    print("\n" + "=" * 60)
    print("  EXPLORATION COMPLETE")
    print("=" * 60)
    
    conn.close()


if __name__ == "__main__":
    explore_data()
