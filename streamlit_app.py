import pandas as pd
import streamlit as st
import altair as alt

from trading_strategy import (
    analyze_results,
    calculate_moving_averages,
    get_stock_data,
    identify_golden_cross,
    implement_strategy,
)

st.set_page_config(page_title="MSFT Trading Strategy Dashboard", layout="wide")


@st.cache_data
def load_strategy_data():
    data = get_stock_data("MSFT")
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    positions = implement_strategy(data)
    summary = analyze_results(positions)

    chart_df = data.reset_index().rename(columns={"index": "Date"})
    chart_df["Date"] = pd.to_datetime(chart_df["Date"])
    chart_df = chart_df.sort_values("Date").reset_index(drop=True)

    return chart_df, positions, summary


chart_df, positions, summary = load_strategy_data()

st.title("MSFT Trading Strategy Dashboard")

chart_tab, stats_tab, trades_tab = st.tabs([
    "Price Chart",
    "Trade Statistics",
    "Detailed Trades",
])

with chart_tab:
    st.subheader("Price Trend with Moving Averages and Trade Signals")

    buy_points = positions[["BuyDate", "BuyPrice"]].rename(
        columns={"BuyDate": "Date", "BuyPrice": "Price"}
    )
    sell_points = positions[["SellDate", "SellPrice"]].rename(
        columns={"SellDate": "Date", "SellPrice": "Price"}
    )

    buy_points["Date"] = pd.to_datetime(buy_points["Date"])
    sell_points["Date"] = pd.to_datetime(sell_points["Date"])

    line_close = (
        alt.Chart(chart_df)
        .mark_line(color="#2563eb", strokeWidth=2)
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Close:Q", title="Price ($)"),
            tooltip=["Date:T", "Close:Q"],
        )
    )

    ma50 = (
        alt.Chart(chart_df)
        .mark_line(color="#10b981", strokeWidth=1.5)
        .encode(
            x=alt.X("Date:T"),
            y=alt.Y("MA50:Q"),
            tooltip=["Date:T", "MA50:Q"],
        )
    )

    ma200 = (
        alt.Chart(chart_df)
        .mark_line(color="#f59e0b", strokeWidth=1.5)
        .encode(
            x=alt.X("Date:T"),
            y=alt.Y("MA200:Q"),
            tooltip=["Date:T", "MA200:Q"],
        )
    )

    buy_marks = (
        alt.Chart(buy_points)
        .mark_circle(size=70, color="#22c55e")
        .encode(
            x="Date:T",
            y="Price:Q",
            tooltip=["Date:T", "Price:Q"],
        )
    )

    sell_marks = (
        alt.Chart(sell_points)
        .mark_circle(size=70, color="#ef4444")
        .encode(
            x="Date:T",
            y="Price:Q",
            tooltip=["Date:T", "Price:Q"],
        )
    )

    combined = alt.layer(line_close, ma50, ma200, buy_marks, sell_marks).properties(
        width=1200,
        height=600,
        title="MSFT Price vs Moving Averages",
    ).interactive()

    st.altair_chart(combined, use_container_width=True)

with stats_tab:
    st.subheader("Overall Trade Statistics")

    metrics = [
        ("Total Trades", summary["total_trades"]),
        ("Winning Trades", summary["winning_trades"]),
        ("Losing Trades", summary["losing_trades"]),
        ("Win Rate", f"{summary['win_rate']}%"),
        ("Average Profit", f"{summary['average_profit']}%"),
        ("Average Holding Days", summary["average_holding_days"]),
        ("Target Reached", summary["target_reached"]),
        ("Max Holding Period", summary["max_period"]),
    ]

    cols = st.columns(4)
    for index, (label, value) in enumerate(metrics):
        cols[index % 4].metric(label=label, value=value)

with trades_tab:
    st.subheader("Detailed Trade Record")

    display_positions = positions.copy()
    display_positions["BuyDate"] = display_positions["BuyDate"].dt.strftime("%Y-%m-%d")
    display_positions["SellDate"] = display_positions["SellDate"].dt.strftime("%Y-%m-%d")
    display_positions["BuyPrice"] = display_positions["BuyPrice"].round(4)
    display_positions["SellPrice"] = display_positions["SellPrice"].round(4)
    display_positions["ProfitPct"] = display_positions["ProfitPct"].round(2)

    st.dataframe(display_positions, use_container_width=True, hide_index=True)
