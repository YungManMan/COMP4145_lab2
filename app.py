from flask import Flask, render_template

from trading_strategy import (
    analyze_results,
    calculate_moving_averages,
    get_stock_data,
    identify_golden_cross,
    implement_strategy,
)

app = Flask(__name__)


def prepare_data():
    data = get_stock_data("MSFT")
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    positions = implement_strategy(data)
    summary = analyze_results(positions)

    chart_df = data.reset_index().rename(columns={"index": "Date"})
    chart_df["Date"] = chart_df["Date"].dt.strftime("%Y-%m-%d")
    chart_df["Close"] = chart_df["Close"].round(4)
    chart_df["MA50"] = chart_df["MA50"].round(4)
    chart_df["MA200"] = chart_df["MA200"].round(4)

    buy_points = []
    sell_points = []

    for _, trade in positions.iterrows():
        buy_points.append({
            "date": trade["BuyDate"].strftime("%Y-%m-%d"),
            "price": round(float(trade["BuyPrice"]), 4)
        })
        sell_points.append({
            "date": trade["SellDate"].strftime("%Y-%m-%d"),
            "price": round(float(trade["SellPrice"]), 4)
        })

    return chart_df, positions, summary, buy_points, sell_points


@app.route("/")
def chart_page():
    chart_df, positions, summary, buy_points, sell_points = prepare_data()
    return render_template(
        "chart.html",
        chart_data=chart_df.to_dict("records"),
        buy_points=buy_points,
        sell_points=sell_points,
        positions=positions.to_dict("records"),
        summary=summary,
    )


@app.route("/stats")
def stats_page():
    _, _, summary, _, _ = prepare_data()
    return render_template("stats.html", summary=summary)


@app.route("/trades")
def trades_page():
    _, positions, _, _, _ = prepare_data()
    trades = positions.to_dict("records")
    for trade in trades:
        trade["BuyDate"] = trade["BuyDate"].strftime("%Y-%m-%d")
        trade["SellDate"] = trade["SellDate"].strftime("%Y-%m-%d")
        trade["BuyPrice"] = round(float(trade["BuyPrice"]), 4)
        trade["SellPrice"] = round(float(trade["SellPrice"]), 4)
        trade["ProfitPct"] = round(float(trade["ProfitPct"]), 2)
    return render_template("trades.html", trades=trades)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
