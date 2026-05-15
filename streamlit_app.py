"""Dashboard: precio ISA (COP) explicado por COLCAP y USD/COP."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from scipy import stats

st.set_page_config(page_title="ISA vs COLCAP & USD/COP", layout="wide")

TARGET = {"ticker": "ISA.CL", "label": "ISA (Interconexión Eléctrica)"}
REGRESSORS = {
    "COLCAP (ETF iShares ICOLCAP)": "ICOLCAP.CL",
    "USD/COP (tasa de cambio)": "COP=X",
}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch(ticker: str, period: str, interval: str) -> pd.Series:
    df = yf.download(ticker, period=period, interval=interval,
                     progress=False, auto_adjust=False)
    if df.empty:
        return pd.Series(dtype=float, name=ticker)
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.name = ticker
    return close.dropna()


def load_dataset(period: str, interval: str) -> pd.DataFrame:
    target = fetch(TARGET["ticker"], period, interval)
    cols = {TARGET["label"]: target}
    for label, tk in REGRESSORS.items():
        cols[label] = fetch(tk, period, interval)
    df = pd.concat(cols, axis=1).dropna()
    return df


def correlation_block(x: pd.Series, y: pd.Series) -> dict:
    pear_r, pear_p = stats.pearsonr(x, y)
    spear_r, spear_p = stats.spearmanr(x, y)
    return {
        "Pearson r": pear_r, "Pearson p": pear_p,
        "Spearman r": spear_r, "Spearman p": spear_p,
        "R²": pear_r ** 2,
    }


def scatter_with_fit(x: pd.Series, y: pd.Series, xlabel: str, ylabel: str) -> go.Figure:
    fig = px.scatter(x=x, y=y, trendline="ols",
                     labels={"x": xlabel, "y": ylabel},
                     opacity=0.7)
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=420)
    return fig


def dual_axis_timeseries(t: pd.DatetimeIndex, y1: pd.Series, y2: pd.Series,
                         lbl1: str, lbl2: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=y1, name=lbl1, line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=t, y=y2, name=lbl2, yaxis="y2",
                             line=dict(color="#d62728")))
    fig.update_layout(
        yaxis=dict(title=lbl1),
        yaxis2=dict(title=lbl2, overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.12),
        margin=dict(l=10, r=10, t=40, b=10),
        height=420,
    )
    return fig


# ---------------- UI ----------------
st.title("📈 Precio ISA (COP) vs. COLCAP y USD/COP")
st.caption(
    "Acción colombiana **ISA** listada en la Bolsa de Valores de Colombia. "
    "Regresoras: **ICOLCAP** (proxy índice COLCAP) y **USD/COP**. "
    "Datos: Yahoo Finance vía yfinance."
)

with st.sidebar:
    st.header("Parámetros")
    period = st.selectbox("Periodo", ["6mo", "1y", "2y", "5y"], index=1)
    interval = st.selectbox("Intervalo", ["1d", "1wk"], index=0)
    use_returns = st.toggle("Analizar retornos (log diff) en vez de niveles", value=False)
    st.markdown("---")
    st.markdown("**Objetivo:** explicar el precio de ISA con 2 regresoras.")
    st.markdown(f"**Target:** `{TARGET['ticker']}`")
    for lbl, tk in REGRESSORS.items():
        st.markdown(f"- {lbl} → `{tk}`")

with st.spinner("Descargando datos de Yahoo Finance..."):
    df = load_dataset(period, interval)

if df.empty or len(df) < 90:
    st.error(f"Solo {len(df)} observaciones tras alineación. Se requieren ≥90. "
             "Ampliar periodo en la barra lateral.")
    st.stop()

# Transform
if use_returns:
    data = np.log(df).diff().dropna()
    unit_y = "log-retorno"
else:
    data = df.copy()
    unit_y = "COP"

target_col = TARGET["label"]
reg_cols = list(REGRESSORS.keys())

# Header metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Observaciones", f"{len(data)}")
c2.metric("Desde", str(data.index.min().date()))
c3.metric("Hasta", str(data.index.max().date()))
c4.metric(f"Último {target_col}",
          f"${df[target_col].iloc[-1]:,.0f} COP",
          delta=f"{(df[target_col].iloc[-1]/df[target_col].iloc[0]-1)*100:.2f}% periodo")

st.markdown("### Serie temporal — ISA vs. cada regresora")
tab1, tab2 = st.tabs(reg_cols)
for tab, reg in zip((tab1, tab2), reg_cols):
    with tab:
        fig = dual_axis_timeseries(df.index, df[target_col], df[reg],
                                   target_col, reg)
        st.plotly_chart(fig, use_container_width=True)

st.markdown("### Gráfico de dispersión + regresión OLS")
g1, g2 = st.columns(2)
for col, reg in zip((g1, g2), reg_cols):
    with col:
        st.markdown(f"**{target_col}  vs.  {reg}**")
        fig = scatter_with_fit(data[reg], data[target_col], reg,
                               f"{target_col} ({unit_y})")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("### Coeficientes de correlación")
rows = []
for reg in reg_cols:
    s = correlation_block(data[reg], data[target_col])
    rows.append({"Regresora": reg, **{k: round(v, 4) for k, v in s.items()}})
corr_df = pd.DataFrame(rows).set_index("Regresora")
st.dataframe(corr_df, use_container_width=True)

st.markdown("#### Matriz de correlación (Pearson) — todas las series")
heat = data.corr()
fig_h = px.imshow(heat, text_auto=".3f", color_continuous_scale="RdBu_r",
                  zmin=-1, zmax=1, aspect="auto")
fig_h.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig_h, use_container_width=True)

with st.expander("Interpretación"):
    r0 = corr_df.iloc[0]["Pearson r"]
    r1 = corr_df.iloc[1]["Pearson r"]
    st.markdown(f"""
- **{reg_cols[0]}**: Pearson r = **{r0:.3f}**, R² = **{r0**2:.3f}**.
  Como proxy del mercado accionario colombiano, se espera relación positiva con ISA.
- **{reg_cols[1]}**: Pearson r = **{r1:.3f}**, R² = **{r1**2:.3f}**.
  USD/COP refleja exposición cambiaria; signo y magnitud dependen del periodo.
- Con `Analizar retornos` activado, la correlación se calcula sobre log-retornos
  (más adecuado estadísticamente: elimina tendencias no estacionarias).
""")

with st.expander("Datos crudos"):
    st.dataframe(df.tail(50), use_container_width=True)
    st.download_button("Descargar CSV completo",
                       df.to_csv().encode(),
                       file_name="isa_colcap_usdcop.csv")
