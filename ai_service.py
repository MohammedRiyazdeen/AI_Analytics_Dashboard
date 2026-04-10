"""
🤖 ai_service.py — AI-Powered Text-to-SQL Engine
==================================================
Uses Google Gemini API via direct HTTP requests — simple & reliable.

Functions:
1. text_to_sql(question)        → Plain English → SQL query
2. run_query(sql)               → Runs SQL safely → returns results
3. summarize_result(q, result)  → Friendly summary of results
"""

import os
import sqlite3
import pandas as pd
import requests
from dotenv import load_dotenv

# ─── Load API Key ─────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Direct API URL — no special packages needed!
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


def call_gemini(prompt: str) -> str:
    """
    📡 Call Gemini API directly via HTTP POST.
    No special packages — just a simple web request!
    """
    if not GEMINI_API_KEY:
        return "ERROR: GEMINI_API_KEY not found in .env file"
    
    url = f"{API_URL}?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 500,
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        elif response.status_code == 429:
            return "ERROR: Rate limit hit. Please wait 60 seconds and try again."
        else:
            return f"ERROR: API returned status {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out. Check your internet connection."
    except Exception as e:
        return f"ERROR: {str(e)}"


def get_table_schema():
    """📋 Fetch database schema for AI context."""
    conn = sqlite3.connect("dashboard.db")
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(restaurants);")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    
    cursor.execute("SELECT COUNT(*) FROM restaurants;")
    total = cursor.fetchone()[0]
    
    # Get 3 sample values per column
    sample_values = {}
    for col_name in col_names:
        try:
            cursor.execute(
                f'SELECT DISTINCT "{col_name}" FROM restaurants '
                f'WHERE "{col_name}" IS NOT NULL LIMIT 3;'
            )
            sample_values[col_name] = [str(row[0]) for row in cursor.fetchall()]
        except Exception:
            sample_values[col_name] = ["N/A"]
    
    cursor.execute("SELECT DISTINCT area FROM restaurants ORDER BY area LIMIT 15;")
    areas = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT price_category FROM restaurants;")
    price_cats = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    schema = f"TABLE: restaurants ({total} rows)\n\nCOLUMNS:\n"
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        samples = ", ".join(sample_values.get(col_name, ["N/A"])[:3])
        schema += f"  - {col_name} ({col_type}) — examples: {samples}\n"
    
    schema += f"\nAREAS: {', '.join(areas)}"
    schema += f"\nPRICE CATEGORIES: {', '.join(str(p) for p in price_cats)}"
    
    return schema


def text_to_sql(question: str) -> str:
    """🤖 Convert plain English → SQL query using Gemini API."""
    
    schema = get_table_schema()
    
    prompt = f"""You are a SQLite SQL expert. Convert the question into a SQL query.

{schema}

RULES:
1. Return ONLY the raw SQL query. No explanation. No markdown. No backticks.
2. Use ONLY columns listed above. Use SQLite syntax.
3. For cuisine searches, use LIKE '%value%' (comma-separated text).
4. For area searches, use LIKE '%value%' for partial matching.
5. Exclude unrated (ratings = 0) unless asked.
6. For "best"/"top", ORDER BY ratings DESC.
7. For "cheapest", ORDER BY price_for_one ASC.
8. Query MUST start with SELECT.

Question: {question}

SQL:"""

    result = call_gemini(prompt)
    
    if result.startswith("ERROR"):
        return result
    
    # Clean response
    sql = result.replace("```sql", "").replace("```", "").strip()
    
    # Remove non-SQL lines
    lines = sql.split("\n")
    sql_lines = [l for l in lines if l.strip() and not l.strip().startswith("--") and not l.strip().startswith("#")]
    sql = " ".join(sql_lines).strip().rstrip(";").strip()
    
    if not sql.upper().startswith("SELECT"):
        return "ERROR: Only SELECT queries are allowed."
    
    return sql


def run_query(sql: str):
    """🏃 Safely execute SQL and return results as DataFrame."""
    
    sql_upper = sql.upper().strip()
    
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]
    for kw in dangerous:
        if kw in sql_upper:
            return (False, f"⚠️ Blocked: {kw} queries are not allowed.")
    
    if not sql_upper.startswith("SELECT"):
        return (False, "⚠️ Only SELECT queries are allowed.")
    
    try:
        conn = sqlite3.connect("dashboard.db")
        df = pd.read_sql(sql, conn)
        conn.close()
        
        if len(df) == 0:
            return (True, pd.DataFrame({"Result": ["No data found for this query."]}))
        return (True, df)
        
    except sqlite3.OperationalError as e:
        error_msg = str(e)
        if "no such column" in error_msg:
            return (False, "❌ Column not found. Available: names, ratings, cuisine, price_for_one, city, area, price_category")
        elif "no such table" in error_msg:
            return (False, "❌ Table not found. The table is called 'restaurants'.")
        return (False, f"❌ SQL Error: {error_msg}")
    except Exception as e:
        return (False, f"❌ Unexpected error: {str(e)}")


def summarize_result(question: str, result_df: pd.DataFrame) -> str:
    """💬 Generate a friendly summary of query results."""
    
    result_preview = result_df.head(10).to_string(index=False)
    
    prompt = f"""Based on this data, write a 1-2 sentence summary answering the question.
Be specific with numbers and names. Just answer, no repeating the question.

Question: {question}

Data:
{result_preview}

Summary:"""

    result = call_gemini(prompt)
    
    if result.startswith("ERROR"):
        # Fallback summary without AI
        if len(result_df) == 1 and len(result_df.columns) == 1:
            return f"The answer is: {result_df.iloc[0, 0]}"
        elif len(result_df) > 0:
            return f"Found {len(result_df)} results. Top result: {result_df.iloc[0].to_dict()}"
        return "Query completed but returned no results."
    
    return result


# ─── Quick Test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI SERVICE TEST (Gemini Direct API)")
    print("=" * 60)
    
    print(f"\n🔑 API Key: {'✅ Found' if GEMINI_API_KEY else '❌ Missing'}")
    
    question = "Which area has the most restaurants?"
    print(f"\n❓ Question: {question}")
    
    sql = text_to_sql(question)
    print(f"🔧 Generated SQL: {sql}")
    
    if not sql.startswith("ERROR"):
        success, result = run_query(sql)
        if success:
            print(f"\n✅ Result:\n{result.head(10).to_string(index=False)}")
            
            summary = summarize_result(question, result)
            print(f"\n💬 Summary: {summary}")
        else:
            print(f"\n❌ Error: {result}")
    
    print("\n" + "=" * 60)
