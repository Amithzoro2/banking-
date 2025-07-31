import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ---------- Page Config ----------
st.set_page_config(page_title="💰 Expense Tracker", layout="wide")
st.title("💰 Personal & Gaming Expense Tracker")

# ---------- Session State ----------
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=['DateTime', 'Category', 'Product', 'Game_Item', 'Payment_Mode', 'Amount', 'Description']
    )

# ---------- Predefined Products for Each Category ----------
products_by_category = {
    'Food': ['Subway Lunch', 'Pizza', 'Burger', 'Coffee', 'Snacks', 'Grocery Meal'],
    'Groceries': ['Rice', 'Vegetables', 'Fruits', 'Milk', 'Eggs', 'Toiletries'],
    'Transport': ['Petrol', 'Diesel', 'Bus Ticket', 'Train Ticket', 'Taxi Ride', 'Bike Service'],
    'Shopping': ['Clothes', 'Shoes', 'Watch', 'Bag', 'Perfume'],
    'Clothes & Accessories': ['T-Shirt', 'Jeans', 'Shoes', 'Cap', 'Belt', 'Wallet'],
    'Electronics & Gadgets': ['Mobile', 'Laptop', 'Headphones', 'Charger', 'Power Bank'],
    'Utilities': ['Electricity Bill', 'Water Bill', 'Gas Bill', 'Internet Recharge', 'DTH'],
    'Health & Fitness': ['Gym Membership', 'Doctor Visit', 'Medicine', 'Protein Supplement'],
    'Gaming': ['Game Top-Up', 'Battle Pass', 'Skin Purchase'],
    'Entertainment': ['Movie Ticket', 'OTT Subscription', 'Concert Ticket'],
    'Education': ['Books', 'Course', 'Exam Fees', 'Stationery'],
    'Gifts & Donations': ['Birthday Gift', 'Wedding Gift', 'Donation'],
    'Travel & Trips': ['Flight Ticket', 'Hotel Stay', 'Food on Trip', 'Cab on Trip'],
    'Housing & Rent': ['Rent', 'Maintenance', 'Furniture', 'Cleaning Service'],
    'Savings & Investments': ['FD', 'Mutual Fund', 'Stocks', 'Gold Purchase'],
    'Insurance': ['Health Insurance', 'Car Insurance', 'Life Insurance'],
    'EMI / Loans': ['Car EMI', 'Home EMI', 'Personal Loan EMI'],
    'Pets': ['Pet Food', 'Vet Visit', 'Toys', 'Accessories'],
    'Other': ['Miscellaneous']
}

# ---------- Add Expense Section ----------
st.header("➕ Add New Expense")
with st.form("expense_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Date", datetime.today())
        expense_time = st.time_input("Time", datetime.now().time())
        
        # Expanded categories
        category = st.selectbox("Category", list(products_by_category.keys()))
        
        # Suggest predefined products
        predefined_products = products_by_category[category]
        product = st.selectbox("Product / Item Name", predefined_products + ["Other"])
        if product == "Other":
            product = st.text_input("Enter Product Name", placeholder="e.g., iPhone, Petrol, Lunch")

    with col2:
        amount = st.number_input("Amount (₹)", min_value=0.0, step=0.5)
        payment_mode = st.selectbox(
            "Payment Mode",
            ['UPI', 'Credit Card', 'Debit Card', 'Cash', 'Wallet (Paytm/PhonePe)', 'Other']
        )
        
        # Gaming currency dropdown always visible
        game_item_selected = st.selectbox(
            "🎮 Game Currency (only recorded for Gaming)",
            [
                'UC (BGMI)', 'Diamonds (Free Fire)', 'CP (COD Mobile)',
                'Gems (Clash of Clans)', 'V-Bucks (Fortnite)', 'Valorant Points',
                'Robux (Roblox)', 'Other Game Currency'
            ]
        )

    submitted = st.form_submit_button("💾 Add Expense")
    if submitted:
        if amount > 0:
            datetime_expense = datetime.combine(date, expense_time)
            # Record game item only for Gaming
            game_item = game_item_selected if category == "Gaming" else ""
            
            # Auto description
            description_parts = [category]
            if product:
                description_parts.append(product)
            if game_item:
                description_parts.append(game_item)
            description_parts.append(payment_mode)
            description = " | ".join(description_parts)

            new_row = pd.DataFrame(
                [[datetime_expense, category, product, game_item, payment_mode, amount, description]], 
                columns=st.session_state.df.columns
            )
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            
            st.success(f"✅ Added ₹{amount:,.2f} to {category} ({product})")
        else:
            st.warning("⚠️ Please enter an amount greater than 0.")

# ---------- Expense History ----------
if not st.session_state.df.empty:
    df = st.session_state.df.copy()
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Date'] = df['DateTime'].dt.date
    df['Month'] = df['DateTime'].dt.to_period('M').astype(str)

    st.header("📋 Expense History")

    # Product name filter
    product_filter = st.text_input("🔍 Search by Product Name (optional)").strip().lower()
    if product_filter:
        filtered_df = df[df['Product'].str.lower().str.contains(product_filter)]
    else:
        filtered_df = df

    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download CSV", data=csv, file_name='expense_data.csv', mime='text/csv')

    # ---------- Analytics ----------
    st.header("📊 Analytics Dashboard")
    total_spent = df['Amount'].sum()
    avg_per_month = df.groupby('Month')['Amount'].sum().mean()
    today_spent = df[df['Date'] == datetime.today().date()]['Amount'].sum()
    gaming_spent = df[df['Category'] == 'Gaming']['Amount'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💸 Total Spent", f"₹{total_spent:,.2f}")
    col2.metric("🎮 Gaming Spent", f"₹{gaming_spent:,.2f}")
    col3.metric("📆 Avg per Month", f"₹{avg_per_month:,.2f}")
    col4.metric("📍 Today’s Spending", f"₹{today_spent:,.2f}")

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Monthly Spending")
        monthly = df.groupby('Month')['Amount'].sum()
        st.bar_chart(monthly)

    with col2:
        st.subheader("📂 Spending by Category")
        category_data = df.groupby('Category')['Amount'].sum()
        fig, ax = plt.subplots()
        category_data.plot.pie(autopct='%1.1f%%', ax=ax, startangle=90, shadow=True)
        ax.set_ylabel("")
        st.pyplot(fig)

    # Gaming-specific chart
    gaming_data = df[df['Category'] == 'Gaming']
    if not gaming_data.empty:
        st.subheader("🎮 Gaming Expenses Breakdown")
        game_summary = gaming_data.groupby('Game_Item')['Amount'].sum()
        st.bar_chart(game_summary)

else:
    st.info("No expenses yet. Start adding some! 💡")
