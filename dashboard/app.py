"""
RetailSphere Enterprise Analytics & Governance Dashboard
Interactive Streamlit Business Intelligence Platform
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import DUCKDB_PATH, METADATA_DIR, DOCS_DIR

st.set_page_config(
    page_title="RetailSphere Enterprise Data Warehouse",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stMetric label {
        font-size: 0.85rem !important;
        color: #475569 !important;
    }
</style>
""", unsafe_allow_html=True)


import shutil
import tempfile
from src.data_generator import generate_all_data
from src.ingestion.load_csv import load_raw_csvs_to_staging
from src.transformation.transformer import transform_and_build_warehouse
from src.validation.data_quality_engine import run_dq_pipeline
from src.governance.metadata_manager import run_governance_generation
from src.config import RAW_DATA_DIR, SAMPLE_DATA_DIR

@st.cache_resource
def get_connection():
    """Cache robust database connection with fallback and auto-build for cloud deployments."""
    # If database does not exist, auto-build lightweight warehouse for instant cloud deployment
    if not DUCKDB_PATH.exists() or DUCKDB_PATH.stat().st_size == 0:
        target_dir = SAMPLE_DATA_DIR if SAMPLE_DATA_DIR.exists() and (SAMPLE_DATA_DIR / "orders.csv").exists() else RAW_DATA_DIR
        if not (target_dir / "orders.csv").exists():
            generate_all_data(n_customers=1000, n_products=200, n_stores=15, n_orders=5000, target_dir=SAMPLE_DATA_DIR)
            target_dir = SAMPLE_DATA_DIR
        load_raw_csvs_to_staging(source_dir=target_dir, db_path=DUCKDB_PATH)
        con_temp = duckdb.connect(str(DUCKDB_PATH))
        run_dq_pipeline(con_temp)
        transform_and_build_warehouse(con_temp)
        run_governance_generation()
        con_temp.close()

    try:
        con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
        con.execute("SELECT 1 FROM warehouse.fact_sales LIMIT 1")
        return con
    except Exception:
        temp_db = Path(tempfile.gettempdir()) / "retailsphere_dw_temp.duckdb"
        try:
            shutil.copy2(DUCKDB_PATH, temp_db)
            return duckdb.connect(str(temp_db), read_only=True)
        except Exception:
            return duckdb.connect(str(DUCKDB_PATH), read_only=False)


con = get_connection()

# Sidebar Navigation & Filters
st.sidebar.image("https://img.icons8.com/fluency/96/shop.png", width=64)
st.sidebar.title("RetailSphere DW")
st.sidebar.caption("Governed Star Schema Analytics")

view_mode = st.sidebar.radio(
    "Navigation Mode",
    ["📊 Executive Analytics", "👥 Customer & RFM", "🛒 Product & Merchandising", "🛡️ Data Quality & Governance", "📖 Data Dictionary"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")

regions = ["All Regions"] + [r[0] for r in con.execute("SELECT DISTINCT region FROM warehouse.dim_store ORDER BY region").fetchall()]
selected_region = st.sidebar.selectbox("Filter by Region", regions)

categories = ["All Categories"] + [c[0] for c in con.execute("SELECT DISTINCT category FROM warehouse.dim_product ORDER BY category").fetchall()]
selected_category = st.sidebar.selectbox("Filter by Category", categories)

channels = ["All Channels", "Physical Retail", "Digital Channel"]
selected_channel = st.sidebar.selectbox("Channel Group", channels)

# Filter clauses
where_clauses = ["1=1"]
if selected_region != "All Regions":
    where_clauses.append(f"s.region = '{selected_region}'")
if selected_category != "All Categories":
    where_clauses.append(f"p.category = '{selected_category}'")
if selected_channel != "All Channels":
    where_clauses.append(f"s.channel_group = '{selected_channel}'")

filter_sql = " AND ".join(where_clauses)


# ==============================================================================
# TAB 1: EXECUTIVE ANALYTICS
# ==============================================================================
if view_mode == "📊 Executive Analytics":
    st.markdown('<div class="main-header">Executive Sales & Revenue Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time analytical insights powered by Kimball Star Schema data marts</div>', unsafe_allow_html=True)

    # Core High-Level KPIs
    kpi_query = f"""
        SELECT
            COUNT(DISTINCT f.order_id) AS total_orders,
            COUNT(DISTINCT f.customer_key) AS unique_customers,
            SUM(f.quantity) AS total_units,
            SUM(f.net_sales_amount) AS net_revenue,
            SUM(f.gross_profit_amount) AS gross_profit,
            ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS margin_pct,
            ROUND(SUM(f.net_sales_amount) / NULLIF(COUNT(DISTINCT f.order_id), 0), 2) AS aov
        FROM warehouse.fact_sales f
        JOIN warehouse.dim_store s ON f.store_key = s.store_key
        JOIN warehouse.dim_product p ON f.product_key = p.product_key
        JOIN warehouse.dim_date d ON f.date_key = d.date_key
        WHERE {filter_sql};
    """
    kpis = con.execute(kpi_query).fetchdf().iloc[0]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Net Revenue", f"₹{kpis['net_revenue']:,.0f}")
    c2.metric("Gross Profit", f"₹{kpis['gross_profit']:,.0f}")
    c3.metric("Profit Margin", f"{kpis['margin_pct']:.1f}%")
    c4.metric("Total Orders", f"{kpis['total_orders']:,}")
    c5.metric("Avg Order Value", f"₹{kpis['aov']:,.0f}")
    c6.metric("Active Customers", f"{kpis['unique_customers']:,}")

    st.markdown("---")

    # Monthly Trends
    row1_c1, row1_c2 = st.columns([7, 5])
    
    with row1_c1:
        st.subheader("Monthly Revenue & Gross Profit Trend")
        monthly_query = f"""
            SELECT
                d.year_month,
                SUM(f.net_sales_amount) AS net_revenue,
                SUM(f.gross_profit_amount) AS gross_profit
            FROM warehouse.fact_sales f
            JOIN warehouse.dim_store s ON f.store_key = s.store_key
            JOIN warehouse.dim_product p ON f.product_key = p.product_key
            JOIN warehouse.dim_date d ON f.date_key = d.date_key
            WHERE {filter_sql}
            GROUP BY d.year_month
            ORDER BY d.year_month;
        """
        df_monthly = con.execute(monthly_query).df()
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=df_monthly["year_month"], y=df_monthly["net_revenue"], name="Net Revenue", marker_color="#1E3A8A"))
        fig_trend.add_trace(go.Scatter(x=df_monthly["year_month"], y=df_monthly["gross_profit"], name="Gross Profit", line=dict(color="#10B981", width=3)))
        fig_trend.update_layout(xaxis_title="Month", yaxis_title="INR (₹)", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_trend, use_container_width=True)

    with row1_c2:
        st.subheader("Revenue by Sales Region")
        region_query = f"""
            SELECT
                s.region,
                SUM(f.net_sales_amount) AS region_revenue
            FROM warehouse.fact_sales f
            JOIN warehouse.dim_store s ON f.store_key = s.store_key
            JOIN warehouse.dim_product p ON f.product_key = p.product_key
            JOIN warehouse.dim_date d ON f.date_key = d.date_key
            WHERE {filter_sql}
            GROUP BY s.region
            ORDER BY region_revenue DESC;
        """
        df_region = con.execute(region_query).df()
        fig_pie = px.pie(df_region, names="region", values="region_revenue", hole=0.45, color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_pie, use_container_width=True)


# ==============================================================================
# TAB 2: CUSTOMER & RFM SEGMENTATION
# ==============================================================================
elif view_mode == "👥 Customer & RFM":
    st.markdown('<div class="main-header">Customer Segmentation & RFM Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Behavioral clustering: Recency, Frequency, Monetary spend distribution</div>', unsafe_allow_html=True)

    rfm_summary_query = """
        SELECT
            rfm_customer_tier,
            COUNT(*) AS customer_count,
            ROUND(SUM(monetary_spend), 2) AS total_spend,
            ROUND(AVG(monetary_spend), 2) AS avg_spend,
            ROUND(AVG(frequency_orders), 1) AS avg_orders,
            ROUND(AVG(recency_days), 1) AS avg_recency_days
        FROM warehouse.mart_customer_rfm
        GROUP BY rfm_customer_tier
        ORDER BY total_spend DESC;
    """
    df_rfm = con.execute(rfm_summary_query).df()

    c1, c2 = st.columns([6, 6])
    with c1:
        st.subheader("Customer Count by RFM Tier")
        fig_rfm_count = px.bar(df_rfm, x="rfm_customer_tier", y="customer_count", color="rfm_customer_tier", color_discrete_sequence=px.colors.qualitative.Safe)
        fig_rfm_count.update_layout(xaxis_title="RFM Tier", yaxis_title="Customer Count", showlegend=False)
        st.plotly_chart(fig_rfm_count, use_container_width=True)

    with c2:
        st.subheader("Revenue Contribution by RFM Tier")
        fig_rfm_rev = px.pie(df_rfm, names="rfm_customer_tier", values="total_spend", hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_rfm_rev, use_container_width=True)

    st.subheader("Detailed RFM Segment Performance Table")
    st.dataframe(df_rfm, use_container_width=True)


# ==============================================================================
# TAB 3: PRODUCT & MERCHANDISING
# ==============================================================================
elif view_mode == "🛒 Product & Merchandising":
    st.markdown('<div class="main-header">Product & Merchandising Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Category margins, top velocity SKUs, and price tier profitability</div>', unsafe_allow_html=True)

    top_prod_query = f"""
        SELECT
            p.sku,
            p.product_name,
            p.category,
            p.subcategory,
            SUM(f.quantity) AS units_sold,
            ROUND(SUM(f.net_sales_amount), 2) AS revenue,
            ROUND(SUM(f.gross_profit_amount), 2) AS gross_profit,
            ROUND((SUM(f.gross_profit_amount) / NULLIF(SUM(f.net_sales_amount), 0)) * 100.0, 2) AS realized_margin_pct
        FROM warehouse.fact_sales f
        JOIN warehouse.dim_product p ON f.product_key = p.product_key
        JOIN warehouse.dim_store s ON f.store_key = s.store_key
        WHERE {filter_sql}
        GROUP BY p.sku, p.product_name, p.category, p.subcategory
        ORDER BY revenue DESC
        LIMIT 15;
    """
    df_top_prod = con.execute(top_prod_query).df()

    st.subheader("Top 15 Revenue Contributing Products")
    st.dataframe(df_top_prod, use_container_width=True)


# ==============================================================================
# TAB 4: DATA QUALITY & GOVERNANCE
# ==============================================================================
elif view_mode == "🛡️ Data Quality & Governance":
    st.markdown('<div class="main-header">Data Quality Audit & Quarantine Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enterprise data-quality framework tracking 10 check categories & anomaly routing</div>', unsafe_allow_html=True)

    q_orders = con.execute("SELECT COUNT(*) FROM quarantine.quarantine_orders").fetchone()[0]
    q_items = con.execute("SELECT COUNT(*) FROM quarantine.quarantine_order_items").fetchone()[0]
    q_cust = con.execute("SELECT COUNT(*) FROM quarantine.quarantine_customers").fetchone()[0]

    qc1, qc2, qc3 = st.columns(3)
    qc1.metric("Quarantined Orders", f"{q_orders:,}", delta="Anomalies Isolated", delta_color="inverse")
    qc2.metric("Quarantined Order Items", f"{q_items:,}", delta="Anomalies Isolated", delta_color="inverse")
    qc3.metric("Quarantined Customers", f"{q_cust:,}", delta="Anomalies Isolated", delta_color="inverse")

    st.markdown("---")
    st.subheader("Quarantine Reason Code Breakdown")
    reason_query = """
        SELECT rejection_reason_code, COUNT(*) AS anomaly_count 
        FROM quarantine.quarantine_orders 
        GROUP BY rejection_reason_code
        UNION ALL
        SELECT rejection_reason_code, COUNT(*) AS anomaly_count 
        FROM quarantine.quarantine_order_items 
        GROUP BY rejection_reason_code
        UNION ALL
        SELECT rejection_reason_code, COUNT(*) AS anomaly_count 
        FROM quarantine.quarantine_customers 
        GROUP BY rejection_reason_code
        ORDER BY anomaly_count DESC;
    """
    df_reasons = con.execute(reason_query).df()
    fig_reasons = px.bar(df_reasons, x="rejection_reason_code", y="anomaly_count", color="rejection_reason_code")
    fig_reasons.update_layout(xaxis_title="Rejection Reason Code", yaxis_title="Record Count", showlegend=False)
    st.plotly_chart(fig_reasons, use_container_width=True)


# ==============================================================================
# TAB 5: DATA DICTIONARY
# ==============================================================================
elif view_mode == "📖 Data Dictionary":
    st.markdown('<div class="main-header">Enterprise Data Dictionary & Metadata Catalog</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Documented warehouse attributes with classification and business rules</div>', unsafe_allow_html=True)

    meta_csv = METADATA_DIR / "metadata.csv"
    if meta_csv.exists():
        df_meta = pd.read_csv(meta_csv)
        search = st.text_input("🔍 Search column, definition, or table name:")
        if search:
            df_filtered = df_meta[
                df_meta["column_name"].str.contains(search, case=False, na=False) |
                df_meta["table_name"].str.contains(search, case=False, na=False) |
                df_meta["business_definition"].str.contains(search, case=False, na=False)
            ]
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.dataframe(df_meta, use_container_width=True)
