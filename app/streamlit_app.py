import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="Logistics Delivery Performance & Cost Analytics",
    page_icon="🚚",
    layout="wide"
)

# Function to load cleaned dataset and standardize types
@st.cache_data
def load_data():
    file_path = os.path.join("data", "cleaned", "logistics_cleaned.csv")
    if not os.path.exists(file_path):
        st.error(f"Cleaned dataset not found at `{file_path}`. Please run `python run_pipeline.py` first.")
        st.stop()
    
    df = pd.read_csv(file_path)

    # Standardize column names (lowercase & whitespace stripped)
    df.columns = df.columns.str.strip().str.lower()

    # Ensure numeric columns are properly typed float/int
    numeric_cols = [
        'delay_days', 'delivery_days', 'on_time_flag', 'total_logistics_cost', 
        'shipping_cost', 'fuel_cost', 'damage_flag', 'return_flag', 
        'warehouse_processing_hours', 'distance_km', 'quantity', 'weight_kg'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0.0

    # Ensure 'delivery_status' column exists
    if 'delivery_status' not in df.columns:
        if 'on_time_flag' in df.columns:
            df['delivery_status'] = df['on_time_flag'].apply(lambda x: 'On-Time' if x == 1 else 'Delayed')
        elif 'delay_days' in df.columns:
            df['delivery_status'] = df['delay_days'].apply(lambda x: 'Delayed' if x > 0 else 'Delivered')
        else:
            df['delivery_status'] = 'Delivered'

    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

    if 'route' not in df.columns and 'origin_city' in df.columns and 'destination_city' in df.columns:
        df['route'] = df['origin_city'].astype(str) + " -> " + df['destination_city'].astype(str)
    elif 'route' not in df.columns:
        df['route'] = 'Standard Route'

    return df

df = load_data()

# ---------------------------------------------------------
# Sidebar Navigation & All 6 Requested Filters
# ---------------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to Page",
    [
        "Executive Overview",
        "Delivery Analysis",
        "Route Analysis",
        "Warehouse Analysis",
        "Cost Analysis",
        "Partner Analysis"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("Filter Options")

# 1. Warehouse Filter
warehouses = ["All"] + sorted(list(df['warehouse'].dropna().unique())) if 'warehouse' in df.columns else ["All"]
selected_warehouse = st.sidebar.selectbox("Warehouse", warehouses)

# 2. Origin City Filter
origins = ["All"] + sorted(list(df['origin_city'].dropna().unique())) if 'origin_city' in df.columns else ["All"]
selected_origin = st.sidebar.selectbox("Origin City", origins)

# 3. Destination City Filter
destinations = ["All"] + sorted(list(df['destination_city'].dropna().unique())) if 'destination_city' in df.columns else ["All"]
selected_destination = st.sidebar.selectbox("Destination City", destinations)

# 4. Shipping Mode Filter
shipping_modes = ["All"] + sorted(list(df['shipping_mode'].dropna().unique())) if 'shipping_mode' in df.columns else ["All"]
selected_shipping = st.sidebar.selectbox("Shipping Mode", shipping_modes)

# 5. Delivery Partner Filter
partners = ["All"] + sorted(list(df['delivery_partner'].dropna().unique())) if 'delivery_partner' in df.columns else ["All"]
selected_partner = st.sidebar.selectbox("Delivery Partner", partners)

# 6. Delivery Status Filter
statuses = ["All"] + sorted(list(df['delivery_status'].dropna().unique())) if 'delivery_status' in df.columns else ["All"]
selected_status = st.sidebar.selectbox("Delivery Status", statuses)

# Apply All 6 Filters
filtered_df = df.copy()
if selected_warehouse != "All" and 'warehouse' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['warehouse'] == selected_warehouse]
if selected_origin != "All" and 'origin_city' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['origin_city'] == selected_origin]
if selected_destination != "All" and 'destination_city' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['destination_city'] == selected_destination]
if selected_shipping != "All" and 'shipping_mode' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['shipping_mode'] == selected_shipping]
if selected_partner != "All" and 'delivery_partner' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['delivery_partner'] == selected_partner]
if selected_status != "All" and 'delivery_status' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['delivery_status'] == selected_status]

if filtered_df.empty:
    st.warning("No data available for the selected filter criteria.")
    st.stop()

# Helper function to display performance data table on every page
def display_performance_data(df_to_show):
    st.markdown("---")
    st.subheader("📋 Cleaned Performance Data Preview")
    st.dataframe(df_to_show.head(50), use_container_width=True)

# =========================================================
# Executive Overview
# =========================================================
if page == "Executive Overview":
    st.title("📊 Executive Overview")
    st.markdown("---")
    
    total_orders = len(filtered_df)
    delivered_orders = (filtered_df['delivery_status'].astype(str).str.lower() == 'delivered').sum()
    delayed_orders = (filtered_df['delay_days'] > 0).sum()
    on_time_pct = (filtered_df['on_time_flag'].mean() * 100) if 'on_time_flag' in filtered_df.columns else 0.0
    avg_delivery_days = filtered_df['delivery_days'].mean()
    total_cost = filtered_df['total_logistics_cost'].sum()
    avg_cost = filtered_df['total_logistics_cost'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Delivered Orders", f"{delivered_orders:,}")
    col3.metric("Delayed Orders", f"{delayed_orders:,}")
    col4.metric("On-Time %", f"{on_time_pct:.1f}%")

    col5, col6, col7 = st.columns(3)
    col5.metric("Average Delivery Days", f"{avg_delivery_days:.2f}")
    col6.metric("Total Logistics Cost", f"${total_cost:,.2f}")
    col7.metric("Average Logistics Cost", f"${avg_cost:,.2f}")

    display_performance_data(filtered_df)

# =========================================================
# Delivery Analysis
# =========================================================
elif page == "Delivery Analysis":
    st.title("🚚 Delivery Analysis")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Delivery Status")
        status_df = filtered_df['delivery_status'].value_counts().reset_index()
        status_df.columns = ['Status', 'Count']
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=status_df, x='Status', y='Count', palette='Set2', ax=ax)
        ax.set_title("Orders by Delivery Status", fontweight='bold')
        st.pyplot(fig)
            
    with col2:
        st.subheader("Delay Analysis")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(filtered_df['delay_days'], bins=15, kde=True, color='indianred', ax=ax)
        ax.set_title("Distribution of Delay Days", fontweight='bold')
        ax.set_xlabel("Delay Days")
        st.pyplot(fig)

    st.subheader("Monthly Delivery Trend")
    if 'order_date' in filtered_df.columns and filtered_df['order_date'].notna().any():
        trend_df = filtered_df.set_index('order_date').resample('ME').size().reset_index(name='Order Count')
        trend_df['Month'] = trend_df['order_date'].dt.strftime('%Y-%m')
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=trend_df, x='Month', y='Order Count', marker='o', ax=ax, color='teal')
        ax.set_title("Monthly Order Volume Trend", fontweight='bold')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    display_performance_data(filtered_df)

# =========================================================
# Route Analysis
# =========================================================
elif page == "Route Analysis":
    st.title("🗺️ Route Analysis")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Routes (by Order Volume)")
        top_routes = filtered_df['route'].value_counts().head(10).reset_index()
        top_routes.columns = ['Route', 'Volume']
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.barplot(data=top_routes, x='Volume', y='Route', palette='Blues_r', ax=ax)
        ax.set_title("Top 10 Most Frequent Routes", fontweight='bold')
        st.pyplot(fig)

    with col2:
        st.subheader("Route Delays")
        delayed_routes = filtered_df.groupby('route')['delay_days'].mean().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.barplot(data=delayed_routes, x='delay_days', y='route', palette='Reds_r', ax=ax)
        ax.set_title("Top 10 Routes by Average Delay Days", fontweight='bold')
        ax.set_xlabel("Average Delay Days")
        st.pyplot(fig)

    st.subheader("Route Costs")
    costly_routes = filtered_df.groupby('route')['total_logistics_cost'].mean().sort_values(ascending=False).head(10).reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=costly_routes, x='route', y='total_logistics_cost', palette='Purples_r', ax=ax)
    ax.set_title("Top 10 Most Expensive Routes (Avg Cost)", fontweight='bold')
    ax.set_ylabel("Avg Logistics Cost ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    display_performance_data(filtered_df)

# =========================================================
# Warehouse Analysis
# =========================================================
elif page == "Warehouse Analysis":
    st.title("🏭 Warehouse Analysis")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Orders by Warehouse")
        if 'warehouse' in filtered_df.columns:
            wh_orders = filtered_df['warehouse'].value_counts().reset_index()
            wh_orders.columns = ['Warehouse', 'Orders']
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=wh_orders, x='Warehouse', y='Orders', palette='viridis', ax=ax)
            ax.set_title("Total Orders Processed per Warehouse", fontweight='bold')
            st.pyplot(fig)
        else:
            st.info("Warehouse field not found in dataset.")

    with col2:
        st.subheader("Processing Time")
        if 'warehouse' in filtered_df.columns:
            wh_time = filtered_df.groupby('warehouse')['warehouse_processing_hours'].mean().reset_index()
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=wh_time, x='warehouse', y='warehouse_processing_hours', palette='magma', ax=ax)
            ax.set_title("Avg Processing Time (Hours)", fontweight='bold')
            ax.set_ylabel("Hours")
            st.pyplot(fig)

    st.subheader("Delay Percentage by Warehouse")
    if 'warehouse' in filtered_df.columns:
        wh_delay = filtered_df.groupby('warehouse')['on_time_flag'].apply(lambda x: (1 - x.mean()) * 100).reset_index()
        wh_delay.columns = ['Warehouse', 'Delay %']
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=wh_delay, x='Warehouse', y='Delay %', palette='Oranges_r', ax=ax)
        ax.set_title("Delay Percentage by Warehouse (%)", fontweight='bold')
        ax.set_ylabel("Delay Rate (%)")
        st.pyplot(fig)

    display_performance_data(filtered_df)

# =========================================================
# Cost Analysis
# =========================================================
elif page == "Cost Analysis":
    st.title("💰 Cost Analysis")
    st.markdown("---")
    
    total_cost = filtered_df['total_logistics_cost'].sum()
    avg_cost = filtered_df['total_logistics_cost'].mean()
    
    c1, c2 = st.columns(2)
    c1.metric("Total Cost", f"${total_cost:,.2f}")
    c2.metric("Average Cost", f"${avg_cost:,.2f}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost by Mode")
        if 'shipping_mode' in filtered_df.columns:
            mode_cost = filtered_df.groupby('shipping_mode')['total_logistics_cost'].sum().reset_index()
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=mode_cost, x='shipping_mode', y='total_logistics_cost', palette='Greens_r', ax=ax)
            ax.set_title("Total Logistics Cost by Shipping Mode", fontweight='bold')
            st.pyplot(fig)

    with col2:
        st.subheader("Cost by Route (Top 10)")
        route_cost = filtered_df.groupby('route')['total_logistics_cost'].sum().sort_values(ascending=False).head(10).reset_index()
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(data=route_cost, x='total_logistics_cost', y='route', palette='YlOrRd_r', ax=ax)
        ax.set_title("Top 10 Routes by Total Spending", fontweight='bold')
        st.pyplot(fig)

    st.subheader("Cost Trend")
    if 'order_date' in filtered_df.columns and filtered_df['order_date'].notna().any():
        cost_trend = filtered_df.set_index('order_date').resample('ME')['total_logistics_cost'].sum().reset_index()
        cost_trend['Month'] = cost_trend['order_date'].dt.strftime('%Y-%m')
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=cost_trend, x='Month', y='total_logistics_cost', marker='s', color='darkgreen', ax=ax)
        ax.set_title("Monthly Total Logistics Cost Trend", fontweight='bold')
        plt.xticks(rotation=45)
        st.pyplot(fig)

    display_performance_data(filtered_df)

# =========================================================
# Partner Analysis
# =========================================================
elif page == "Partner Analysis":
    st.title("🤝 Partner Analysis")
    st.markdown("---")
    
    if 'delivery_partner' in filtered_df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Partner Shipments")
            partner_shipments = filtered_df['delivery_partner'].value_counts().reset_index()
            partner_shipments.columns = ['Partner', 'Shipments']
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=partner_shipments, x='Partner', y='Shipments', palette='mako', ax=ax)
            ax.set_title("Total Shipments Handled per Partner", fontweight='bold')
            st.pyplot(fig)

        with col2:
            st.subheader("Partner Delay %")
            partner_delay = filtered_df.groupby('delivery_partner')['on_time_flag'].apply(lambda x: (1 - x.mean()) * 100).reset_index()
            partner_delay.columns = ['Partner', 'Delay %']
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=partner_delay, x='Partner', y='Delay %', palette='Reds_r', ax=ax)
            ax.set_title("Delay Rate by Delivery Partner (%)", fontweight='bold')
            ax.set_ylim(0, 100)
            st.pyplot(fig)

        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Partner Cost")
            partner_cost = filtered_df.groupby('delivery_partner')['total_logistics_cost'].mean().reset_index()
            partner_cost.columns = ['Partner', 'Avg Cost']
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=partner_cost, x='Partner', y='Avg Cost', palette='crest', ax=ax)
            ax.set_title("Average Cost per Order by Partner ($)", fontweight='bold')
            st.pyplot(fig)

        with col4:
            st.subheader("Partner Damage Rate")
            partner_damage = filtered_df.groupby('delivery_partner')['damage_flag'].mean().apply(lambda x: x * 100).reset_index()
            partner_damage.columns = ['Partner', 'Damage %']
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=partner_damage, x='Partner', y='Damage %', palette='rocket', ax=ax)
            ax.set_title("Damage Rate by Partner (%)", fontweight='bold')
            st.pyplot(fig)
    else:
        st.info("Delivery partner column not present in the dataset.")

    display_performance_data(filtered_df)
