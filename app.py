import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# 1. SETUP & CUSTOM CSS (THE GLOW-UP)
# ==========================================
st.set_page_config(page_title="Food Rescue Pro", layout="wide", page_icon="🍲")

# Injecting Custom CSS for "Cool Colours" and sleek UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sleek buttons with a warm gradient-like orange */
    div.stButton > button:first-child {
        background-color: #FF7043;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #E64A19;
        color: white;
        transform: scale(1.02);
    }
    
    /* Custom header colors */
    h1, h2, h3 {
        color: #2E7D32 !important; /* Fresh, earthy green */
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE HELPER FUNCTIONS
# ==========================================
@st.cache_data
def fetch_data(query):
    conn = sqlite3.connect('food_wastage.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def execute_query(query, params=()):
    conn = sqlite3.connect('food_wastage.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    st.cache_data.clear()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🍲 Food Rescue Pro")
st.sidebar.markdown("---")
page = st.sidebar.radio("📌 Main Menu", [
    "📊 Executive Dashboard", 
    "🔍 Find Available Food", 
    "⚙️ Manage Listings (CRUD)", 
    "📞 Provider Directory"
])
st.sidebar.markdown("---")
st.sidebar.info("A Local Food Wastage Management System connecting surplus food to those in need.")

# ==========================================
# 4. PAGE LOGIC
# ==========================================

# -------------------------------------------------------------
# PAGE 1: EXECUTIVE DASHBOARD (ALL 15 QUERIES)
# -------------------------------------------------------------
if page == "📊 Executive Dashboard":
    st.title("Executive Insights & Analytics")
    
    # KPI Metric Cards
    col1, col2, col3 = st.columns(3)
    try:
        total_food = fetch_data("SELECT SUM(Quantity) as total FROM food_listings").iloc[0]['total']
        total_providers = fetch_data("SELECT COUNT(*) as total FROM providers").iloc[0]['total']
        total_receivers = fetch_data("SELECT COUNT(*) as total FROM receivers").iloc[0]['total']
        
        with col1:
            st.metric(label="Total Food Available", value=f"{total_food:,} items", delta="High Impact")
        with col2:
            st.metric(label="Active Providers", value=total_providers)
        with col3:
            st.metric(label="Active Receivers", value=total_receivers)
    except Exception:
        st.warning("Database might be empty. Please add some data first.")
        
    st.markdown("---")
    
    st.subheader("Deep Dive Analysis Reports")
    query_selection = st.selectbox("Select a specialized report to run:", [
        "1. Providers & Receivers by City",
        "2. Top Contributing Provider Type",
        "3. Provider Contact Info (Sample City)",
        "4. Top 5 Receivers by Claimed Food",
        "5. Total Food Available",
        "6. City with Highest Food Listings",
        "7. Most Commonly Available Food Types",
        "8. Claims per Food Item (Top 5)",
        "9. Provider with Most Successful Claims",
        "10. Claim Status Percentages",
        "11. Average Quantity Claimed per Receiver (Top 5)",
        "12. Most Claimed Meal Type",
        "13. Top 5 Providers by Total Donated",
        "14. Food Items Expiring Soon",
        "15. Monthly Claim Trends"
    ])

    if query_selection == "1. Providers & Receivers by City":
        sql = """
        SELECT City, 'Provider' AS Entity_Type, COUNT(*) AS Total FROM providers GROUP BY City
        UNION ALL
        SELECT City, 'Receiver' AS Entity_Type, COUNT(*) AS Total FROM receivers GROUP BY City;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "2. Top Contributing Provider Type":
        sql = """
        SELECT p.Type, SUM(f.Quantity) AS Total_Quantity
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Type
        ORDER BY Total_Quantity DESC LIMIT 1;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "3. Provider Contact Info (Sample City)":
        sql = """
        SELECT Name, Contact, Address, City
        FROM providers
        WHERE City = (SELECT City FROM providers LIMIT 1);
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "4. Top 5 Receivers by Claimed Food":
        sql = """
        SELECT r.Name, SUM(f.Quantity) AS Total_Food_Claimed
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY r.Name
        ORDER BY Total_Food_Claimed DESC
        LIMIT 5;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "5. Total Food Available":
        sql = "SELECT SUM(Quantity) AS Total_Food_Available FROM food_listings;"
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "6. City with Highest Food Listings":
        sql = """
        SELECT Location AS City, COUNT(Food_ID) AS Total_Listings
        FROM food_listings
        GROUP BY Location
        ORDER BY Total_Listings DESC LIMIT 1;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "7. Most Commonly Available Food Types":
        sql = """
        SELECT Food_Type, COUNT(Food_ID) AS Frequency
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY Frequency DESC;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "8. Claims per Food Item (Top 5)":
        sql = """
        SELECT Food_ID, COUNT(Claim_ID) AS Total_Claims
        FROM claims
        GROUP BY Food_ID
        ORDER BY Total_Claims DESC LIMIT 5;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "9. Provider with Most Successful Claims":
        sql = """
        SELECT p.Name AS Provider_Name, COUNT(c.Claim_ID) AS Successful_Claims
        FROM food_listings f
        JOIN claims c ON f.Food_ID = c.Food_ID
        JOIN providers p ON f.Provider_ID = p.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Name
        ORDER BY Successful_Claims DESC LIMIT 1;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "10. Claim Status Percentages":
        sql = """
        SELECT Status, 
               ROUND((COUNT(Claim_ID) * 100.0 / (SELECT COUNT(*) FROM claims)), 2) AS Percentage
        FROM claims
        GROUP BY Status;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "11. Average Quantity Claimed per Receiver (Top 5)":
        sql = """
        SELECT r.Name, AVG(f.Quantity) AS Avg_Food_Claimed
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings f ON c.Food_ID = f.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY r.Name
        ORDER BY Avg_Food_Claimed DESC
        LIMIT 5;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "12. Most Claimed Meal Type":
        sql = """
        SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
        FROM food_listings f
        JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY f.Meal_Type
        ORDER BY Total_Claims DESC LIMIT 1;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "13. Top 5 Providers by Total Donated":
        sql = """
        SELECT p.Name, SUM(f.Quantity) AS Total_Donated
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Name
        ORDER BY Total_Donated DESC
        LIMIT 5;
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "14. Food Items Expiring Soon":
        sql = """
        SELECT COUNT(Food_ID) AS Expiring_Soon
        FROM food_listings
        WHERE date(Expiry_Date) <= date('now', '+1 day')
        AND Food_ID NOT IN (SELECT Food_ID FROM claims WHERE Status = 'Completed');
        """
        st.dataframe(fetch_data(sql), use_container_width=True)

    elif query_selection == "15. Monthly Claim Trends":
        sql = """
        SELECT strftime('%Y-%m', Timestamp) AS Claim_Month, COUNT(Claim_ID) AS Total_Claims
        FROM claims
        GROUP BY Claim_Month
        ORDER BY Claim_Month ASC;
        """
        df_trends = fetch_data(sql)
        st.bar_chart(df_trends.set_index("Claim_Month"), color="#FF7043") # Styled chart color!
        st.dataframe(df_trends, use_container_width=True)

# -------------------------------------------------------------
# PAGE 2: FIND AVAILABLE FOOD
# -------------------------------------------------------------
elif page == "🔍 Find Available Food":
    st.title("Search Surplus Food")
    col1, col2 = st.columns(2)
    with col1:
        cities_df = fetch_data("SELECT DISTINCT Location FROM food_listings ORDER BY Location")
        selected_city = st.selectbox("Select City", ["All"] + cities_df['Location'].tolist())
    with col2:
        meals_df = fetch_data("SELECT DISTINCT Meal_Type FROM food_listings ORDER BY Meal_Type")
        selected_meal = st.selectbox("Select Meal Type", ["All"] + meals_df['Meal_Type'].tolist())

    query = "SELECT Food_Name, Quantity, Expiry_Date, Provider_Type, Location, Meal_Type FROM food_listings WHERE 1=1"
    if selected_city != "All": query += f" AND Location = '{selected_city}'"
    if selected_meal != "All": query += f" AND Meal_Type = '{selected_meal}'"
    st.dataframe(fetch_data(query), use_container_width=True)

# -------------------------------------------------------------
# PAGE 3: MANAGE LISTINGS (CRUD)
# -------------------------------------------------------------
elif page == "⚙️ Manage Listings (CRUD)":
    st.title("Manage Inventory")
    action = st.radio("Choose an action:", ["Add Listing", "Update Quantity", "Delete Listing"], horizontal=True)

    if action == "Add Listing":
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            food_id = col1.number_input("New Food ID", min_value=2000, step=1) 
            food_name = col2.text_input("Food Name (e.g., Apple Pie)")
            quantity = col1.number_input("Quantity", min_value=1, step=1)
            expiry_date = col2.date_input("Expiry Date")
            provider_id = col1.number_input("Provider ID", min_value=1, step=1)
            location = col2.text_input("City/Location")
            
            if st.form_submit_button("Add Food to Database"):
                sql = "INSERT INTO food_listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Location, Food_Type, Meal_Type, Provider_Type) VALUES (?, ?, ?, ?, ?, ?, 'General', 'Snacks', 'Restaurant')"
                try:
                    execute_query(sql, (food_id, food_name, quantity, expiry_date, provider_id, location))
                    st.success(f"Successfully added {quantity} x {food_name}!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error: {e}")

    elif action == "Update Quantity":
        with st.form("update_form"):
            food_id = st.number_input("Enter Food ID to Update", min_value=1, step=1)
            new_qty = st.number_input("New Quantity", min_value=0, step=1)
            if st.form_submit_button("Update Inventory"):
                execute_query("UPDATE food_listings SET Quantity = ? WHERE Food_ID = ?", (new_qty, food_id))
                st.success(f"Food ID {food_id} updated to {new_qty} items!")

    elif action == "Delete Listing":
        with st.form("delete_form"):
            food_id = st.number_input("Enter Food ID to Delete", min_value=1, step=1)
            if st.form_submit_button("Delete Permanently"):
                execute_query("DELETE FROM food_listings WHERE Food_ID = ?", (food_id,))
                st.error(f"Food ID {food_id} deleted permanently!")

# -------------------------------------------------------------
# PAGE 4: PROVIDER DIRECTORY
# -------------------------------------------------------------
elif page == "📞 Provider Directory":
    st.title("Our Generous Providers")
    st.markdown("Use this directory to locate and contact surplus food donors directly.")
    st.dataframe(fetch_data("SELECT Name, Type, Address, City, Contact FROM providers"), use_container_width=True)