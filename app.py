import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# SETTINGS
# ============================================================

DURATION = 15


# ============================================================
# STREAMLIT
# ============================================================

st.set_page_config(
    page_title="EL-DAM Curves",
    layout="wide"
)

st.title("EL-DAM Curves")


# ============================================================
# UPLOAD EXCEL
# ============================================================

uploaded_file = st.file_uploader(
    "Ανέβασε το Excel αρχείο",
    type=["xlsx"]
)


if uploaded_file is None:
    st.info("Ανέβασε ένα Excel αρχείο για να ξεκινήσεις.")
    st.stop()


# ============================================================
# LOAD EXCEL
# ============================================================

@st.cache_data
def load_excel(file):

    df = pd.read_excel(file)

    df["MTU"] = pd.to_datetime(
        df["DELIVERY_MTU"],
        format="%Y/%m/%d %H:%M:%S"
    )

    return df


df = load_excel(uploaded_file)


# ============================================================
# FILTER DURATION
# ============================================================

df = df[
    df["DELIVERY_DURATION"] == DURATION
].copy()


# ============================================================
# FILTER OPTIONS
# ============================================================

available_dates = sorted(
    df["MTU"].dt.date.unique()
)

available_times = sorted(
    df["MTU"].dt.strftime("%H:%M").unique()
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Filters")


# ------------------------------------------------------------
# DATE
# ------------------------------------------------------------

selected_dates = st.sidebar.multiselect(
    "Ημερομηνία",
    available_dates,
    default=[available_dates[0]],
    format_func=lambda x:
        pd.Timestamp(x).strftime("%d/%m/%Y")
)


# ------------------------------------------------------------
# QUARTER
# ------------------------------------------------------------

selected_times = st.sidebar.multiselect(
    "Τέταρτο",
    available_times,
    default=["12:00"]
)


# ------------------------------------------------------------
# CURVE TYPE
# ------------------------------------------------------------

curve_types = st.sidebar.multiselect(
    "Καμπύλες",
    ["Sell", "Buy"],
    default=["Sell"]
)


# ------------------------------------------------------------
# PRICE RANGE
# ------------------------------------------------------------

price_min = st.sidebar.number_input(
    "Min τιμή",
    value=-20.0
)

price_max = st.sidebar.number_input(
    "Max τιμή",
    value=400.0
)


# ============================================================
# CHECK FILTERS
# ============================================================

if not selected_dates:
    st.warning("Επίλεξε τουλάχιστον μία ημερομηνία.")
    st.stop()


if not selected_times:
    st.warning("Επίλεξε τουλάχιστον ένα τέταρτο.")
    st.stop()


if not curve_types:
    st.warning("Επίλεξε τουλάχιστον μία καμπύλη.")
    st.stop()


# ============================================================
# FILTER DATA
# ============================================================

df_filtered = df[
    df["MTU"].dt.date.isin(selected_dates)
    &
    df["MTU"].dt.strftime("%H:%M").isin(selected_times)
    &
    df["SIDE_DESCR"].isin(curve_types)
].copy()


# ============================================================
# PLOTLY
# ============================================================

fig = go.Figure()


for mtu in sorted(df_filtered["MTU"].unique()):

    for side in curve_types:

        curve = df_filtered[
            (df_filtered["MTU"] == mtu)
            &
            (df_filtered["SIDE_DESCR"] == side)
        ].sort_values("AA")


        if curve.empty:
            continue


        if side == "Sell":
            label = "Sell"
        else:
            label = "Buy"


        name = (
            f"{pd.Timestamp(mtu):%d/%m %H:%M} - "
            f"{label}"
        )


        fig.add_trace(
            go.Scatter(
                x=curve["QUANTITY"],
                y=curve["UNITPRICE"],
                mode="lines",
                name=name,
                hovertemplate=
                    "Quantity: %{x:,.0f} MW"
                    "<br>"
                    "Price: %{y:.2f} €/MWh"
                    "<extra>"
                    + name +
                    "</extra>"
            )
        )


# ============================================================
# LAYOUT
# ============================================================

fig.update_layout(

    title="EL-DAM Aggregated Curves",

    xaxis_title="Αθροιστική ποσότητα (MW)",

    yaxis_title="Τιμή (€/MWh)",

    yaxis=dict(
        range=[
            price_min,
            price_max
        ]
    ),

    hovermode="closest",

    height=700,

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),

    margin=dict(
        l=60,
        r=30,
        t=100,
        b=60
    )
)


# ============================================================
# DISPLAY
# ============================================================

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# INFO
# ============================================================

st.write(
    f"**{len(fig.data)} καμπύλες εμφανίζονται**"
)
