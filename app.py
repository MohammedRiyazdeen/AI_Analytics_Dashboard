"""
app.py - AI Data Analytics Dashboard
Streamlit dashboard for exploring Zomato restaurant data with
interactive charts, filters, and SQL-based insights.
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ─── Page Configuration ─────────────────────────────────────────────
st.set_page_config(
    page_title="📊 AI Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for Premium Look ────────────────────────────────────
st.markdown("""
<style>
    /* ── Main background ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* ── Sidebar styling ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0c29 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e94560 !important;
    }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(233, 69, 96, 0.2);
        border-radius: 12px;
        padding: 16px 20px;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        background: rgba(233, 69, 96, 0.08);
        border-color: rgba(233, 69, 96, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(233, 69, 96, 0.15);
    }
    div[data-testid="stMetric"] label {
        color: #8892b0 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e94560 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* ── Dataframe / table styling ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── Headers ── */
    .main h1 {
        background: linear-gradient(90deg, #e94560, #c23152, #e94560);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(233, 69, 96, 0.2) !important;
    }

    /* ── Selectbox and slider ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(233, 69, 96, 0.3) !important;
        border-radius: 8px !important;
    }

    /* ── Info/result count banner ── */
    .result-banner {
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.1), rgba(194, 49, 82, 0.05));
        border: 1px solid rgba(233, 69, 96, 0.25);
        border-radius: 10px;
        padding: 12px 20px;
        margin: 10px 0 20px 0;
        text-align: center;
    }
    .result-banner span {
        color: #e94560;
        font-weight: 700;
        font-size: 1.1rem;
    }
    .result-banner p {
        color: #8892b0;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Database Connection (Cached) ────────────────────────────
@st.cache_resource
def get_connection():
    """Create a cached database connection."""
    return sqlite3.connect("dashboard.db", check_same_thread=False)


@st.cache_data(ttl=600)
def load_all_data():
    """Load the full dataset from SQLite."""
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM restaurants", conn)
    return df


@st.cache_data(ttl=600)
def get_unique_areas():
    """Get all unique area values for the dropdown filter."""
    conn = get_connection()
    areas = pd.read_sql(
        "SELECT DISTINCT area FROM restaurants ORDER BY area", conn
    )
    return ["All Areas"] + areas["area"].tolist()


@st.cache_data(ttl=600)
def get_unique_cuisines():
    """Get unique individual cuisine types from comma-separated values."""
    conn = get_connection()
    cuisines_raw = pd.read_sql("SELECT DISTINCT cuisine FROM restaurants", conn)
    
    all_cuisines = set()
    for cuisine_str in cuisines_raw["cuisine"].dropna():
        for c in cuisine_str.split(","):
            cleaned = c.strip()
            if cleaned:
                all_cuisines.add(cleaned)
    
    return ["All Cuisines"] + sorted(all_cuisines)


@st.cache_data(ttl=600)
def get_unique_price_categories():
    """Get all unique price categories for the dropdown."""
    conn = get_connection()
    cats = pd.read_sql(
        "SELECT DISTINCT price_category FROM restaurants ORDER BY price_category", conn
    )
    return ["All Prices"] + cats["price_category"].tolist()


def filter_data(df, area, cuisine, price_category, min_rating, max_rating):
    """Apply sidebar filters and return filtered dataframe."""
    filtered = df.copy()
    
    if area != "All Areas":
        filtered = filtered[filtered["area"] == area]
    

    if cuisine != "All Cuisines":
        filtered = filtered[
            filtered["cuisine"].str.contains(cuisine, case=False, na=False)
        ]
    

    if price_category != "All Prices":
        filtered = filtered[filtered["price_category"] == price_category]
    

    filtered = filtered[
        (filtered["ratings"] >= min_rating) & (filtered["ratings"] <= max_rating)
    ]
    
    return filtered


# ─── Main App ───────────────────────────────────────────────────
def main():
    # Load data
    df = load_all_data()
    areas = get_unique_areas()
    cuisines = get_unique_cuisines()
    price_categories = get_unique_price_categories()
    
    # ─── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        # App name
        st.markdown("# 📊 AI Data Dashboard")
        st.markdown("---")
        
        # About section
        st.markdown("### ℹ️ About")
        st.markdown(
            "An interactive analytics dashboard built on the **Zomato Hyderabad** "
            "restaurant dataset (658 restaurants). Explore trends across areas, "
            "cuisines, prices and ratings using real-time SQL queries and dynamic charts."
        )
        st.markdown("---")
        
        # Filters heading
        st.markdown("### 🎛️ Filters")
        
        # Area filter
        st.markdown("##### 📍 Location")
        selected_area = st.selectbox(
            "Select Area",
            options=areas,
            index=0,
            help="Filter restaurants by locality in Hyderabad"
        )
        
        # Cuisine filter
        st.markdown("##### 🍳 Cuisine Type")
        selected_cuisine = st.selectbox(
            "Select Cuisine",
            options=cuisines,
            index=0,
            help="Filter by type of food served"
        )
        
        # Price category filter
        st.markdown("##### 💰 Price Range")
        selected_price = st.selectbox(
            "Select Price Category",
            options=price_categories,
            index=0,
            help="Filter by price tier"
        )
        
        # Rating slider
        st.markdown("##### ⭐ Rating Range")
        min_rating, max_rating = st.slider(
            "Select Rating Range",
            min_value=0.0,
            max_value=5.0,
            value=(0.0, 5.0),
            step=0.1,
            help="Slide to filter by minimum and maximum rating"
        )
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.markdown(
            "<p style='text-align:center; color:#555; font-size:0.75rem;'>"
            "Built by Riyaz • Powered by Streamlit</p>",
            unsafe_allow_html=True
        )
    
    # ─── APPLY FILTERS ────────────────────────────────────────
    filtered_df = filter_data(
        df, selected_area, selected_cuisine, 
        selected_price, min_rating, max_rating
    )
    
    # ─── HEADER ───────────────────────────────────────────────
    st.markdown("# 📊 AI Data Analytics Dashboard")
    st.markdown("*Explore restaurant data across cities, cuisines and ratings interactively — powered by real SQL queries*")
    
    # Result count banner
    total = len(df)
    showing = len(filtered_df)
    
    if showing == total:
        st.markdown(
            f"""<div class='result-banner'>
                <p>Showing <span>{showing}</span> of <span>{total}</span> restaurants — No filters applied</p>
            </div>""",
            unsafe_allow_html=True
        )
    else:
        active_filters = []
        if selected_area != "All Areas":
            active_filters.append(f"📍 {selected_area}")
        if selected_cuisine != "All Cuisines":
            active_filters.append(f"🍳 {selected_cuisine}")
        if selected_price != "All Prices":
            active_filters.append(f"💰 {selected_price}")
        if min_rating > 0 or max_rating < 5:
            active_filters.append(f"⭐ {min_rating}-{max_rating}")
        
        filter_text = " • ".join(active_filters) if active_filters else ""
        
        st.markdown(
            f"""<div class='result-banner'>
                <p>Showing <span>{showing}</span> of <span>{total}</span> restaurants — {filter_text}</p>
            </div>""",
            unsafe_allow_html=True
        )
    
    # ─── KEY METRICS ROW ──────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏪 Total Restaurants", f"{showing:,}")
    
    with col2:
        if len(filtered_df[filtered_df["ratings"] > 0]) > 0:
            avg_rating = filtered_df[filtered_df["ratings"] > 0]["ratings"].mean()
            st.metric("⭐ Average Rating", f"{avg_rating:.1f} / 5.0")
        else:
            st.metric("⭐ Average Rating", "—")
    
    with col3:
        if len(filtered_df) > 0:
            # Find the most popular individual cuisine
            cuisine_list = []
            for c in filtered_df["cuisine"].dropna():
                for item in c.split(","):
                    cleaned = item.strip()
                    if cleaned:
                        cuisine_list.append(cleaned)
            if cuisine_list:
                top_cuisine = pd.Series(cuisine_list).value_counts().index[0]
                st.metric("🍳 Top Cuisine", top_cuisine)
            else:
                st.metric("🍳 Top Cuisine", "—")
        else:
            st.metric("🍳 Top Cuisine", "—")
    
    with col4:
        if len(filtered_df) > 0:
            top_area = filtered_df["area"].value_counts().index[0]
            # Capitalize for display
            display_area = top_area.replace("-", " ").title()
            st.metric("📍 Top Area", display_area)
        else:
            st.metric("📍 Top Area", "—")
    
    st.markdown("---")

    # ─── DATA OVERVIEW ────────────────────────────────────────
    with st.expander("📂 Click to see raw data sample"):
        rows, cols = filtered_df.shape
        st.markdown(f"**Current filtered view:** `{rows}` rows × `{cols}` columns")
        st.dataframe(filtered_df.head(20), use_container_width=True, hide_index=True)

    # ─── CHARTS SECTION ───────────────────────────────────────
    if len(filtered_df) > 0:

        # ── Shared Plotly dark theme ──
        plot_layout = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ccd6f6", size=12),
            margin=dict(l=40, r=20, t=50, b=40),
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8892b0", size=10),
            ),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        )

        # Color palette matching our theme
        colors = [
            "#e94560", "#c23152", "#533483", "#0f3460",
            "#16213e", "#e94560", "#ff6b6b", "#ffa502",
            "#2ed573", "#1e90ff", "#a29bfe", "#fd79a8",
            "#00cec9", "#6c5ce7", "#fdcb6e", "#e17055",
        ]

        # ────────────────────────────────────────────────────────
        # ROW 1: Top Areas Bar Chart  |  Cuisine Pie Chart
        # ────────────────────────────────────────────────────────
        st.markdown("### 📊 Visual Analytics")
        chart_col1, chart_col2 = st.columns(2)

        # ── Chart 1: Top 10 Areas by Restaurant Count ──
        with chart_col1:
            area_counts = (
                filtered_df["area"]
                .value_counts()
                .head(10)
                .reset_index()
            )
            area_counts.columns = ["Area", "Count"]

            fig1 = px.bar(
                area_counts,
                x="Count",
                y="Area",
                orientation="h",
                title="🏙️ Top 10 Areas by Restaurant Count",
                color="Count",
                color_continuous_scale=["#533483", "#e94560"],
            )
            fig1.update_layout(**plot_layout, showlegend=False, coloraxis_showscale=False)
            fig1.update_layout(yaxis=dict(autorange="reversed"))
            fig1.update_traces(marker_line_width=0)
            st.plotly_chart(fig1, use_container_width=True)

        # ── Chart 2: Cuisine Distribution (Pie) ──
        with chart_col2:
            # Split comma-separated cuisines into individual entries
            cuisine_list = []
            for c in filtered_df["cuisine"].dropna():
                for item in c.split(","):
                    cleaned = item.strip()
                    if cleaned:
                        cuisine_list.append(cleaned)

            cuisine_counts = (
                pd.Series(cuisine_list)
                .value_counts()
                .head(10)
                .reset_index()
            )
            cuisine_counts.columns = ["Cuisine", "Count"]

            fig2 = px.pie(
                cuisine_counts,
                values="Count",
                names="Cuisine",
                title="🍳 Top 10 Cuisine Distribution",
                color_discrete_sequence=colors,
                hole=0.4,  # donut style
            )
            fig2.update_layout(**plot_layout)
            fig2.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont_size=10,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ────────────────────────────────────────────────────────
        # ROW 2: Rating vs Price Scatter  |  Avg Rating by Area
        # ────────────────────────────────────────────────────────
        chart_col3, chart_col4 = st.columns(2)

        # ── Chart 3: Rating vs Price (Scatter) ──
        with chart_col3:
            scatter_df = filtered_df[
                (filtered_df["ratings"] > 0) & (filtered_df["price_for_one"] > 0)
            ].copy()

            if len(scatter_df) > 0:
                fig3 = px.scatter(
                    scatter_df,
                    x="price_for_one",
                    y="ratings",
                    color="price_category",
                    hover_name="names",
                    hover_data=["cuisine", "area"],
                    title="⭐ Rating vs Price — Does Expensive Mean Better?",
                    labels={
                        "price_for_one": "Price for One (₹)",
                        "ratings": "Rating",
                        "price_category": "Price Tier",
                    },
                    color_discrete_sequence=colors,
                    opacity=0.7,
                )
                fig3.update_layout(**plot_layout)
                fig3.update_traces(marker=dict(size=8, line=dict(width=0.5, color="#1a1a2e")))
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No rated restaurants with valid prices to plot.")

        # ── Chart 4: Average Rating by Area (Bar) ──
        with chart_col4:
            rated_df = filtered_df[filtered_df["ratings"] > 0]

            if len(rated_df) > 0:
                avg_rating_by_area = (
                    rated_df.groupby("area")["ratings"]
                    .mean()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                )
                avg_rating_by_area.columns = ["Area", "Avg Rating"]
                avg_rating_by_area["Avg Rating"] = avg_rating_by_area["Avg Rating"].round(2)

                fig4 = px.bar(
                    avg_rating_by_area,
                    x="Area",
                    y="Avg Rating",
                    title="📍 Top 10 Areas by Average Rating",
                    color="Avg Rating",
                    color_continuous_scale=["#533483", "#e94560"],
                    text="Avg Rating",
                )
                fig4.update_layout(**plot_layout, showlegend=False, coloraxis_showscale=False)
                fig4.update_traces(
                    texttemplate="%{text:.2f}",
                    textposition="outside",
                    marker_line_width=0,
                )
                fig4.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No rated restaurants to show average ratings.")

    st.markdown("---")

    # ─── DATA TABLE ───────────────────────────────────────────
    st.markdown("### 📋 Restaurant Data")
    
    if len(filtered_df) > 0:
        # Show a clean table without the links column
        display_df = filtered_df[["names", "ratings", "cuisine", "price_for_one", "area", "price_category"]].copy()
        display_df.columns = ["Restaurant", "Rating ⭐", "Cuisine", "Price (₹)", "Area", "Price Tier"]
        display_df = display_df.sort_values("Rating ⭐", ascending=False).reset_index(drop=True)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            column_config={
                "Rating ⭐": st.column_config.NumberColumn(format="%.1f"),
                "Price (₹)": st.column_config.NumberColumn(format="₹%d"),
            }
        )
        
        # Download button for filtered data
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv_data,
            file_name="filtered_restaurants.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.warning("😕 No restaurants match your filters. Try adjusting them!")

    # ─── SQL QUERIES SECTION ──────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔬 SQL Queries — Data Analytics")
    st.markdown("*Each query below demonstrates a real SQL technique. The query is shown first, followed by the result.*")

    conn = get_connection()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Query 1: Top 5 Cuisines by Average Rating
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("#### **1. Top 5 Cuisines by Average Rating**")
    st.markdown("*Uses CTE + json_each() to split comma-separated cuisines, GROUP BY with HAVING to filter, ORDER BY for ranking*")
    
    query1 = """SELECT cuisine AS "Cuisine Combination",
       ROUND(AVG(ratings), 2) AS "Avg Rating",
       COUNT(*) AS "Restaurant Count"
FROM restaurants
WHERE ratings > 0
GROUP BY cuisine
HAVING COUNT(*) >= 3
ORDER BY AVG(ratings) DESC
LIMIT 5;"""
    
    st.code(query1, language="sql")
    
    try:
        df1 = pd.read_sql(query1, conn)
        st.dataframe(df1, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Query error: {e}")

    st.markdown("---")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Query 2: Top 10 Areas by Average Price
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("#### **2. Top 10 Areas by Average Price (Most Expensive)**")
    st.markdown("*Uses AVG() with GROUP BY, CASE WHEN for conditional aggregation, HAVING to filter small samples*")
    
    query2 = """SELECT 
    area AS "Area",
    ROUND(AVG(price_for_one), 0) AS "Avg Price (₹)",
    COUNT(*) AS "Restaurant Count",
    ROUND(AVG(CASE WHEN ratings > 0 THEN ratings END), 2) AS "Avg Rating"
FROM restaurants
GROUP BY area
HAVING COUNT(*) >= 3
ORDER BY AVG(price_for_one) DESC
LIMIT 10;"""
    
    st.code(query2, language="sql")
    df2 = pd.read_sql(query2, conn)
    st.dataframe(df2, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Query 3: Price vs Rating Correlation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("#### **3. Does Higher Price Mean Better Rating?**")
    st.markdown("*Uses GROUP BY with multiple aggregates (AVG, MIN, MAX, COUNT), CASE WHEN for conditional filtering*")
    
    query3 = """SELECT 
    price_category AS "Price Tier",
    COUNT(*) AS "Restaurant Count",
    ROUND(AVG(CASE WHEN ratings > 0 THEN ratings END), 2) AS "Avg Rating",
    ROUND(AVG(price_for_one), 0) AS "Avg Price (₹)",
    ROUND(MIN(CASE WHEN ratings > 0 THEN ratings END), 1) AS "Min Rating",
    ROUND(MAX(ratings), 1) AS "Max Rating"
FROM restaurants
GROUP BY price_category
ORDER BY AVG(price_for_one) ASC;"""
    
    st.code(query3, language="sql")
    df3 = pd.read_sql(query3, conn)
    st.dataframe(df3, use_container_width=True, hide_index=True)
    
    # Auto-generated insight
    if len(df3) > 1:
        cheapest_rating = df3["Avg Rating"].iloc[0]
        expensive_rating = df3["Avg Rating"].iloc[-1]
        if expensive_rating > cheapest_rating:
            st.success(f"💡 **Insight:** More expensive restaurants DO rate slightly higher ({expensive_rating} vs {cheapest_rating})")
        else:
            st.info(f"💡 **Insight:** Price doesn't guarantee quality! Budget restaurants rate {cheapest_rating} vs premium at {expensive_rating}")

    st.markdown("---")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Query 4: Hidden Gems
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("#### **4. Hidden Gems — Rating ≥ 4.5, Price Below Average**")
    st.markdown("*Uses a subquery to calculate average price, then filters with WHERE and multiple conditions*")
    
    query4 = """SELECT 
    names AS "Restaurant",
    ratings AS "Rating ⭐",
    price_for_one AS "Price (₹)",
    cuisine AS "Cuisine",
    area AS "Area"
FROM restaurants
WHERE ratings >= 4.5
  AND price_for_one < (SELECT AVG(price_for_one) FROM restaurants)
ORDER BY ratings DESC, price_for_one ASC;"""
    
    st.code(query4, language="sql")
    df4 = pd.read_sql(query4, conn)
    
    if len(df4) > 0:
        st.dataframe(df4, use_container_width=True, hide_index=True)
        st.success(f"🎯 Found **{len(df4)} hidden gems** — highly rated but affordable!")
    else:
        st.info("No restaurants match this criteria with current data.")

    st.markdown("---")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Query 5: Most Popular Cuisine per Area
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("#### **5. Most Popular Cuisine in Each Top Area**")
    st.markdown("*Uses CTE (WITH clause), ROW_NUMBER() window function with PARTITION BY, and JOIN — advanced SQL*")
    
    query5 = """WITH area_cuisines AS (
    SELECT area, cuisine, COUNT(*) as cnt,
        ROW_NUMBER() OVER (PARTITION BY area ORDER BY COUNT(*) DESC) as rn
    FROM restaurants
    GROUP BY area, cuisine
),
area_totals AS (
    SELECT area, COUNT(*) as total
    FROM restaurants
    GROUP BY area
    HAVING COUNT(*) >= 5
)
SELECT 
    a.area AS "Area",
    at2.total AS "Total Restaurants",
    a.cuisine AS "Most Popular Cuisine",
    a.cnt AS "Count"
FROM area_cuisines a
JOIN area_totals at2 ON a.area = at2.area
WHERE a.rn = 1
ORDER BY at2.total DESC
LIMIT 10;"""
    
    st.code(query5, language="sql")
    df5 = pd.read_sql(query5, conn)
    st.dataframe(df5, use_container_width=True, hide_index=True)

    # ─── Footer ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center; color:#555; font-size:0.8rem;'>"
        "🍽️ Zomato Analytics Dashboard • Built by Riyaz • "
        "Powered by Python, Streamlit, SQLite & Plotly</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
