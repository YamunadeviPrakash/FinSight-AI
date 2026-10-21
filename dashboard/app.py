
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="FinSight AI | Financial Intelligence",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "cleaned_transactions.csv"

GREEN = "#70F59A"
MUTED = "#92959F"
BG = "#0B0D0F"
CARD = "#141719"

# -------------------- CUSTOM THEME --------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #0B0D0F;
        color: #F4F5F6;
    }

    [data-testid="stSidebar"] {
        background: #101211;
        border-right: 1px solid #292D2A;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    h1, h2, h3 {
        color: #F5F6F5 !important;
        letter-spacing: -0.6px;
    }

    p, label, .stMarkdown {
        color: #D6D8D7;
    }

    [data-testid="stMetric"] {
        background: #141719;
        border: 1px solid #282D2A;
        padding: 20px 22px;
        border-radius: 15px;
    }

    [data-testid="stMetricLabel"] {
        color: #A5AAA7 !important;
    }

    [data-testid="stMetricValue"] {
        color: #F5F6F5 !important;
        font-size: 1.65rem;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: #171A18;
        border-color: #303631;
        border-radius: 9px;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #303631;
        background: #171A18;
        color: #F5F6F5;
    }

    .stButton > button:hover {
        border-color: #70F59A;
        color: #70F59A;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #292D2A;
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: #292D2A;
    }

    .brand {
        font-size: 1.45rem;
        font-weight: 800;
        color: #F5F6F5;
        margin-bottom: 2px;
    }

    .brand-dot {
        color: #70F59A;
    }

    .muted {
        color: #92959F;
        font-size: 0.9rem;
    }

    .hero {
        background: linear-gradient(120deg, #151B17, #111412);
        border: 1px solid #2B3930;
        border-radius: 18px;
        padding: 26px 28px;
        margin-bottom: 24px;
    }

    .hero-label {
        color: #70F59A;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
    }

    .hero-title {
        color: #F5F6F5;
        font-size: 2rem;
        font-weight: 800;
        margin: 8px 0;
    }

    .hero-copy {
        color: #A8AEA9;
        font-size: 0.95rem;
    }

    .section-heading {
        font-size: 1.12rem;
        font-weight: 700;
        color: #F5F6F5;
        margin: 8px 0 3px;
    }

    .section-subtitle {
        color: #92959F;
        font-size: 0.82rem;
        margin-bottom: 16px;
    }

    .insight-card {
        background: #141719;
        border: 1px solid #292D2A;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .insight-title {
        color: #70F59A;
        font-weight: 700;
        margin-bottom: 7px;
    }

    .insight-copy {
        color: #C4C8C5;
        font-size: 0.9rem;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: transparent;
        border-radius: 9px;
        padding: 7px 10px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #1B241E;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE)
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data = data.dropna(subset=["Date", "Amount"]).copy()

    if "Transaction_Type" not in data.columns:
        data["Transaction_Type"] = data["Income/Expense"].map({
            "Expense": "Expense",
            "Income": "Income",
            "Transfer-Out": "Transfer",
        }).fillna("Other")

    data["Year"] = data["Date"].dt.year
    data["Year_Month"] = data["Date"].dt.to_period("M").astype(str)
    data["Week"] = data["Date"].dt.to_period("W").astype(str)
    data["Day"] = data["Date"].dt.date
    return data


try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the cleaned dataset: {exc}")
    st.info("Check that data/processed/cleaned_transactions.csv exists.")
    st.stop()


# -------------------- HELPERS --------------------
def money(value):
    return f"₹{value:,.0f}"


def heading(title, subtitle=None):
    st.markdown(f'<div class="section-heading">{title}</div>',
                unsafe_allow_html=True)
    if subtitle:
        st.markdown(
            f'<div class="section-subtitle">{subtitle}</div>',
            unsafe_allow_html=True
        )


def chart_layout(fig, height=330):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(family="Inter", color="#D6D8D7", size=12),
        height=height,
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#292D2A", zeroline=False)
    return fig


# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown(
    '<div class="brand"><span class="brand-dot">Fin</span>Sight AI</div>'
    '<div class="muted">Financial Intelligence</div>',
    unsafe_allow_html=True
)
    st.divider()

    
    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
           "Transactions",
            "Analytics",
            "Trends",
            "Insights",
           "Spending Forecast",
        ],
        label_visibility="collapsed",
        format_func=lambda x: {
            "Dashboard": "⌂   Dashboard",
            "Transactions": "⇄   Transactions",
            "Analytics": "▥   Analytics",
            "Trends": "↗   Trends",
            "Insights": "✧   Insights",
            "Spending Forecast": "◷   Spending Forecast",
        }[x],
    )


    st.divider()
    st.markdown("**DATA FILTERS**")

    available_years = sorted(df["Year"].dropna().unique().tolist())
    selected_years = st.multiselect(
        "Years",
        available_years,
        default=available_years
    )

    type_options = sorted(df["Transaction_Type"].dropna().unique().tolist())
    selected_types = st.multiselect(
        "Transaction types",
        type_options,
        default=type_options
    )

    st.divider()
    st.markdown(
        '<div class="muted">Portfolio project · Historical sample data</div>',
        unsafe_allow_html=True
    )


filtered = df[
    df["Year"].isin(selected_years)
    & df["Transaction_Type"].isin(selected_types)
].copy()

expenses = filtered.loc[
    filtered["Transaction_Type"] == "Expense", "Amount"
].sum()
income = filtered.loc[
    filtered["Transaction_Type"] == "Income", "Amount"
].sum()
transfers = filtered.loc[
    filtered["Transaction_Type"] == "Transfer", "Amount"
].sum()

# Categories that may represent investments or movement of money,
# rather than everyday consumption.
non_daily_categories = {
    "investment", "money transfer", "fixed deposit",
    "recurring deposit", "public provident fund",
    "share market", "equity mutual fund b"
}

everyday_expenses = filtered[
    (filtered["Transaction_Type"] == "Expense")
    & (~filtered["Category"].str.lower().isin(non_daily_categories))
].copy()


# -------------------- PAGE: DASHBOARD --------------------
if page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <div class="hero-label">YOUR FINANCIAL OVERVIEW</div>
        <div class="hero-title">Make your money make sense.</div>
        <div class="hero-copy">
            Explore spending patterns, understand your cash flow,
            and discover insights hidden in your transactions.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total income", money(income))
    c2.metric("Total expenses", money(expenses))
    c3.metric("Income − expenses", money(income - expenses))
    c4.metric("Transfers", money(transfers))

    st.caption(
        "Historical sample data. Income minus expenses is not a verified "
        "account balance. Transfers are tracked separately."
    )
    st.divider()

    left, right = st.columns([1.5, 1])

    with left:
        heading("Cash flow over time", "Monthly income compared with expenses")
        monthly = (
            filtered[
                filtered["Transaction_Type"].isin(["Income", "Expense"])
            ]
            .groupby(["Year_Month", "Transaction_Type"], as_index=False)
            ["Amount"].sum()
        )

        if not monthly.empty:
            fig = px.line(
                monthly,
                x="Year_Month",
                y="Amount",
                color="Transaction_Type",
                markers=True,
                color_discrete_map={
                    "Income": GREEN,
                    "Expense": "#F5A16C"
                },
                labels={
                    "Year_Month": "Month",
                    "Amount": "Amount (₹)",
                    "Transaction_Type": "Type"
                }
            )
            st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
        else:
            st.info("No matching income or expense records.")

    with right:
        heading("Where your money goes", "Everyday expense categories")
        category_totals = (
            everyday_expenses.groupby("Category", as_index=False)["Amount"]
            .sum()
            .sort_values("Amount", ascending=False)
        )

        if not category_totals.empty:
            top = category_totals.head(7).copy()
            remaining = category_totals.iloc[7:]["Amount"].sum()
            if remaining > 0:
                top = pd.concat([
                    top,
                    pd.DataFrame([{
                        "Category": "Other categories",
                        "Amount": remaining
                    }])
                ], ignore_index=True)

            fig = px.pie(
                top,
                names="Category",
                values="Amount",
                hole=0.64,
                color_discrete_sequence=[
                    GREEN, "#4DBD7A", "#A4E9B9", "#5D9D75",
                    "#D1E9D7", "#8BBA98", "#397D53", "#59645C"
                ]
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate="%{label}<br>₹%{value:,.2f}<extra></extra>"
            )
            st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
        else:
            st.info("No everyday expense data for these filters.")

    st.divider()
    heading("Recent transactions", "Your latest recorded activity")

    recent = filtered.sort_values("Date", ascending=False).head(8)
    if not recent.empty:
        show_cols = [
            "Date", "Category", "Mode", "Amount",
            "Income/Expense", "Currency"
        ]
        st.dataframe(
            recent[show_cols].reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions match the selected filters.")


# -------------------- PAGE: TRANSACTIONS --------------------
elif page == "Transactions":
    st.title("Transactions")
    st.markdown(
        '<div class="muted">Search and explore your recorded transactions.</div>',
        unsafe_allow_html=True
    )

    search = st.text_input(
        "Search transactions",
        placeholder="Search category, note, or payment mode..."
    )

    transaction_view = filtered.copy()
    if search:
        mask = (
            transaction_view["Category"].astype(str).str.contains(
                search, case=False, na=False
            )
            | transaction_view["Note"].astype(str).str.contains(
                search, case=False, na=False
            )
            | transaction_view["Mode"].astype(str).str.contains(
                search, case=False, na=False
            )
        )
        transaction_view = transaction_view[mask]

    st.caption(f"{len(transaction_view):,} transactions found")

    display_cols = [
        "Date", "Mode", "Category", "Subcategory",
        "Amount", "Income/Expense", "Currency"
    ]
    st.dataframe(
        transaction_view[display_cols].sort_values(
            "Date", ascending=False
        ),
        use_container_width=True,
        hide_index=True,
        height=520
    )

    csv_data = transaction_view[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered transactions as CSV",
        data=csv_data,
        file_name="filtered_transactions.csv",
        mime="text/csv"
    )


# -------------------- PAGE: ANALYTICS --------------------
elif page == "Analytics":
    st.title("Financial Analytics")
    st.markdown(
        '<div class="muted">Break down spending and compare transaction types.</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        heading("Top everyday expense categories")
        totals = (
            everyday_expenses.groupby("Category", as_index=False)["Amount"]
            .sum()
            .sort_values("Amount", ascending=True)
            .tail(10)
        )
        if not totals.empty:
            fig = px.bar(
                totals,
                x="Amount",
                y="Category",
                orientation="h",
                color_discrete_sequence=[GREEN],
                labels={"Amount": "Amount (₹)", "Category": ""}
            )
            st.plotly_chart(chart_layout(fig, 420), use_container_width=True)
        else:
            st.info("No matching expenses.")

    with col2:
        heading("Income, expenses and transfers")
        type_summary = (
            filtered.groupby("Transaction_Type", as_index=False)["Amount"]
            .sum()
        )
        if not type_summary.empty:
            fig = px.bar(
                type_summary,
                x="Transaction_Type",
                y="Amount",
                color="Transaction_Type",
                color_discrete_map={
                    "Income": GREEN,
                    "Expense": "#F5A16C",
                    "Transfer": "#8D9BE8"
                },
                labels={
                    "Transaction_Type": "Type",
                    "Amount": "Total amount (₹)"
                }
            )
            st.plotly_chart(chart_layout(fig, 420), use_container_width=True)
        else:
            st.info("No matching transactions.")

    st.divider()
    heading("Category summary")
    if not everyday_expenses.empty:
        summary = (
            everyday_expenses.groupby("Category")["Amount"]
            .agg(Transaction_Count="count", Total_Spent="sum",
                 Average_Transaction="mean")
            .sort_values("Total_Spent", ascending=False)
            .reset_index()
        )
        summary[["Total_Spent", "Average_Transaction"]] = summary[
            ["Total_Spent", "Average_Transaction"]
        ].round(2)
        st.dataframe(summary, use_container_width=True, hide_index=True)


# -------------------- PAGE: TRENDS --------------------
elif page == "Trends":
    st.title("Spending Trends")
    st.markdown(
        '<div class="muted">Explore historical daily, weekly, and monthly patterns.</div>',
        unsafe_allow_html=True
    )

    trend_type = st.segmented_control(
        "Time interval",
        options=["Daily", "Weekly", "Monthly"],
        default="Monthly"
    )

    period_column = {
        "Daily": "Day",
        "Weekly": "Week",
        "Monthly": "Year_Month"
    }[trend_type]

    trend_data = everyday_expenses.copy()
    trend_data["Period"] = trend_data[period_column].astype(str)

    grouped = (
        trend_data.groupby("Period", as_index=False)["Amount"]
        .sum()
        .sort_values("Period")
    )

    if not grouped.empty:
        a, b, c = st.columns(3)
        a.metric("Total in selection", money(grouped["Amount"].sum()))
        a = grouped["Amount"].mean()
        b.metric("Average per period", money(a))
        c.metric("Highest period", money(grouped["Amount"].max()))

        fig = px.line(
            grouped,
            x="Period",
            y="Amount",
            markers=True,
            color_discrete_sequence=[GREEN],
            labels={"Period": trend_type, "Amount": "Spending (₹)"}
        )
        fig.update_traces(line_width=3, fill="tozeroy", fillcolor="rgba(112,245,154,0.08)")
        st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

        st.caption(
            "These are historical records from 2015–2018, not live recent spending."
        )
    else:
        st.info("No matching expense records.")

# -------------------- PAGE: INSIGHTS --------------------
elif page == "Insights":
    st.title("AI Financial Insights")
    st.markdown(
        '<div class="muted">Machine-learning alerts based on historical '
        'transaction patterns.</div>',
        unsafe_allow_html=True
    )

    RESULTS_FILE = (
        BASE_DIR / "data" / "processed" / "anomaly_results.csv"
    )

    if not RESULTS_FILE.exists():
        st.warning(
            "Anomaly results not found. Run "
            "`python src/anomaly_detection.py` first."
        )
        st.stop()

    anomalies = pd.read_csv(RESULTS_FILE)
    anomalies["Date"] = pd.to_datetime(
        anomalies["Date"], errors="coerce"
    )
    anomalies["Amount"] = pd.to_numeric(
        anomalies["Amount"], errors="coerce"
    )

    # Apply the dashboard's year and transaction-type filters
    anomalies = anomalies[
        anomalies["Date"].dt.year.isin(selected_years)
    ].copy()

    if "Anomaly_Flag" in anomalies.columns:
        anomalies["Anomaly_Flag"] = (
            anomalies["Anomaly_Flag"]
            .astype(str).str.lower().eq("true")
        )
    else:
        st.error("The anomaly results are missing the Anomaly_Flag column.")
        st.stop()

    flagged = anomalies[anomalies["Anomaly_Flag"]].copy()

    total_analyzed = len(anomalies)
    flagged_count = len(flagged)
    flagged_pct = (
        flagged_count / total_analyzed * 100
        if total_analyzed else 0
    )

    a, b, c = st.columns(3)
    a.metric("Expenses analyzed", f"{total_analyzed:,}")
    b.metric("Potential anomalies", f"{flagged_count:,}")
    c.metric("Flagged percentage", f"{flagged_pct:.2f}%")

    st.info(
        "These are unusual-pattern alerts, not fraud predictions. "
        "Review each transaction in context."
    )

    st.divider()
    heading(
        "Transactions to review",
        "Sorted by the model's anomaly score, highest first."
    )

    if not flagged.empty:
        flagged = flagged.sort_values(
            "Anomaly_Score", ascending=False
        )

        category_options = sorted(
            flagged["Category"].dropna().unique().tolist()
        )
        chosen_categories = st.multiselect(
            "Filter flagged categories",
            category_options,
            default=category_options
        )

        shown = flagged[
            flagged["Category"].isin(chosen_categories)
        ].copy()

        display_cols = [
            "Date", "Category", "Subcategory", "Amount",
            "Anomaly_Score", "Review_Reason"
        ]
        st.dataframe(
            shown[display_cols],
            use_container_width=True,
            hide_index=True
        )

        csv_data = shown[display_cols].to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download flagged transactions",
            data=csv_data,
            file_name="finsight_anomaly_alerts.csv",
            mime="text/csv"
        )

        st.subheader("Flagged transactions by category")
        category_counts = (
            flagged.groupby("Category", as_index=False)
            .size()
            .rename(columns={"size": "Flagged transactions"})
            .sort_values("Flagged transactions", ascending=True)
            .tail(10)
        )

        fig = px.bar(
            category_counts,
            x="Flagged transactions",
            y="Category",
            orientation="h",
            color_discrete_sequence=[GREEN],
            labels={"Category": "Category"}
        )
        st.plotly_chart(
            chart_layout(fig, 350),
            use_container_width=True
        )
    else:
        st.success(
            "No transactions were flagged in the selected years."
        )

    st.caption(
        "Isolation Forest is an unsupervised model. The current "
        "contamination setting controls the expected fraction of "
        "outliers; it does not measure real-world fraud accuracy."
    )

elif page == "Spending Forecast":
    from pathlib import Path

    import pandas as pd
    import plotly.graph_objects as go

    project_root = Path(__file__).resolve().parent.parent
    forecast_path = (
        project_root / "data" / "processed" / "spending_forecast.csv"
    )
    cleaned_path = (
        project_root / "data" / "processed" / "cleaned_transactions.csv"
    )

    st.title("Spending Forecast")
    st.caption("Historical household expense analysis")

    if not forecast_path.exists() or not cleaned_path.exists():
        st.warning(
            "Forecast files are missing. Run "
            "`python src/spending_forecast.py` first."
        )
    else:
        forecast_df = pd.read_csv(forecast_path)
        transactions = pd.read_csv(cleaned_path)

        transactions["Date"] = pd.to_datetime(
            transactions["Date"], errors="coerce"
        )
        transactions["Amount"] = pd.to_numeric(
            transactions["Amount"], errors="coerce"
        )

        expenses = transactions[
            transactions["Income/Expense"]
            .astype(str).str.strip().str.lower() == "expense"
        ].dropna(subset=["Date", "Amount"])

        monthly_actual = (
            expenses.set_index("Date")["Amount"]
            .resample("MS")
            .sum()
            .asfreq("MS", fill_value=0)
        )

        forecast_df["Month"] = pd.to_datetime(
            forecast_df["Month"], errors="coerce"
        )
        forecast_df["Forecast_Expense"] = pd.to_numeric(
            forecast_df["Forecast_Expense"], errors="coerce"
        )
        forecast_df = forecast_df.dropna(
            subset=["Month", "Forecast_Expense"]
        )

        if forecast_df.empty or monthly_actual.empty:
            st.warning("There is not enough valid data to display forecasts.")
        else:
            st.info(
                "This dataset ends in September 2018. "
                "The forecasts below are historical-period estimates, "
                "not predictions for the current year."
            )

            
            col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
            "Average monthly expense",
            f"₹{monthly_actual.mean():,.2f}",
        )

        with col2:
            st.metric(
            "Forecast periods",
            len(forecast_df),
        )

        with col3:
            st.metric(
                "Seasonal model MAE",
                "₹20,635.15",
                help=(
                "Mean Absolute Error measured on 12 historical test months. "
                "This does not guarantee future accuracy."
            ),
        )


        st.subheader("Historical Expenses and Forecasts")

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_actual.index,
                y=monthly_actual.values,
                mode="lines+markers",
                name="Historical expenses",
                line=dict(width=2),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=forecast_df["Month"],
                y=forecast_df["Forecast_Expense"],
                mode="lines+markers",
                name="Seasonal-naive forecast",
                line=dict(width=3, dash="dash"),
            )
        )
            # Mark where historical data ends and forecasting begins
        forecast_start = forecast_df["Month"].min()

        fig.add_vline(
            x=forecast_start.timestamp() * 1000,
            line_dash="dot",
            line_width=2,
            annotation_text="Forecast begins",
            annotation_position="top",
        )

        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Month",
            yaxis_title="Expenses (₹)",
            legend_title="Series",
            margin=dict(l=10, r=10, t=30, b=10),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Forecast Estimates")

        display_forecast = forecast_df.copy()
        display_forecast["Month"] = (
            display_forecast["Month"].dt.strftime("%B %Y")
        )
        display_forecast["Forecast_Expense"] = (
            display_forecast["Forecast_Expense"]
            .map(lambda amount: f"₹{amount:,.2f}")
        )

        st.dataframe(
            display_forecast.rename(
                columns={
                    "Month": "Forecast month",
                    "Forecast_Expense": "Estimated expenses",
                    "Forecast_Method": "Method",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("How the Forecast Works")
        st.write(
            "The seasonal-naive method estimates each month using "
            "the actual expense total from the same calendar month "
            "in the previous year."
        )

        st.caption(
            "Validation on 12 historical months: seasonal-naive "
            "MAE ₹20,635.15; previous-month baseline MAE ₹32,598.09. "
            "These are historical evaluation results, not a guarantee "
            "of future accuracy."
        )

