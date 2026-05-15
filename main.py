"""Script auxiliar: descarga datos a CSV para uso offline."""
import yfinance as yf
import pandas as pd

TICKERS = {
    "ISA": "ISA.CL",
    "ICOLCAP": "ICOLCAP.CL",
    "USDCOP": "COP=X",
}


def main(period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    frames = {}
    for name, ticker in TICKERS.items():
        df = yf.download(ticker, period=period, interval=interval,
                         progress=False, auto_adjust=False)
        close = df["Close"]
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]
        frames[name] = close
    out = pd.concat(frames, axis=1, sort=True).dropna()
    out.to_csv("dataset.csv")
    print(f"Saved {len(out)} rows -> dataset.csv")
    print(out.tail())
    return out


if __name__ == "__main__":
    main()
