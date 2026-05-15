# 📈 ISA (BVC) — análisis con 2 regresoras

Dashboard interactivo en Streamlit que analiza el precio de la acción **ISA**
(Interconexión Eléctrica S.A. – Bolsa de Valores de Colombia) expresado en **COP**,
explicado mediante dos variables regresoras:

1. **ICOLCAP.CL** — ETF iShares COLCAP (proxy del índice COLCAP).
2. **COP=X** — tasa de cambio USD/COP.

## Características

- Serie temporal diaria de ~1 año (>90 observaciones, configurable).
- Dos gráficos de serie temporal con doble eje (uno por regresora).
- Dos gráficos de dispersión con ajuste OLS.
- Coeficientes de correlación de **Pearson** y **Spearman** + R² y p-values.
- Matriz de correlación (heatmap).
- Opción de analizar **niveles** o **log-retornos**.
- Descarga de los datos en CSV.

## Fuente de datos

Yahoo Finance vía `yfinance`. Tickers:

| Variable        | Ticker         | Unidad |
|-----------------|----------------|--------|
| ISA (target)    | `ISA.CL`       | COP    |
| COLCAP (proxy)  | `ICOLCAP.CL`   | COP    |
| USD/COP         | `COP=X`        | COP    |

> Nota: `^COLCAP` no está disponible en Yahoo Finance; se usa el ETF `ICOLCAP.CL`
> como proxy del índice.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy en Streamlit Community Cloud

1. Push del repositorio a GitHub.
2. En <https://share.streamlit.io>, conectar el repo.
3. Configurar:
   - **Main file path:** `streamlit_app.py`
   - **Python version:** 3.11+ (recomendado)
4. Deploy.

## Archivos

- `streamlit_app.py` — dashboard principal.
- `main.py` — script auxiliar de descarga directa a CSV.
- `requirements.txt` — dependencias.
