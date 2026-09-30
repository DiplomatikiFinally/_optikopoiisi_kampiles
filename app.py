import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SETTINGS
# ============================================================

DURATION = 15
YMIN = -20
YMAX = 400


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


# ============================================================
# STREAMLIT PAGE
# ============================================================

st.set_page_config(
    page_title="EL-DAM Curves",
    layout="wide"
)

st.title("EL-DAM Offer / Demand Curves")


# ============================================================
# UPLOAD EXCEL
# ============================================================

uploaded_file = st.file_uploader(
    "Ανέβασε το Excel αρχείο",
    type=["xlsx"]
)


if uploaded_file is not None:

    # ========================================================
    # LOAD DATA
    # ========================================================

    df = load_excel(uploaded_file)

    # Κρατάμε μόνο το duration που μας ενδιαφέρει
    df = df[
        df["DELIVERY_DURATION"] == DURATION
    ].copy()


    # ========================================================
    # FILTERS
    # ========================================================

    st.subheader("Επιλογές")


    col1, col2, col3 = st.columns(3)


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    dates = sorted(
        df["MTU"].dt.date.unique()
    )

    with col1:

        selected_date = st.selectbox(
            "Ημερομηνία",
            dates,
            format_func=lambda x:
                pd.Timestamp(x).strftime("%d/%m/%Y")
        )


    # --------------------------------------------------------
    # QUARTER
    # --------------------------------------------------------

    df_date = df[
        df["MTU"].dt.date == selected_date
    ]

    mtus = sorted(
        df_date["MTU"].unique()
    )

    with col2:

        selected_mtu = st.selectbox(
            "Τέταρτο",
            mtus,
            format_func=lambda x:
                pd.Timestamp(x).strftime("%H:%M")
        )


    # --------------------------------------------------------
    # CURVE TYPE
    # --------------------------------------------------------

    with col3:

        curve_type = st.selectbox(
            "Καμπύλη",
            [
                "Προσφορά (Sell)",
                "Ζήτηση (Buy)"
            ]
        )


    # ========================================================
    # FILTER SELECTED MTU
    # ========================================================

    d = df[
        df["MTU"] == selected_mtu
    ]


    # ========================================================
    # SELECT BUY / SELL
    # ========================================================

    if curve_type == "Προσφορά (Sell)":

        curve = d[
            d["SIDE_DESCR"] == "Sell"
        ].sort_values("AA")

        curve_label = "Προσφορά (Sell)"

    else:

        curve = d[
            d["SIDE_DESCR"] == "Buy"
        ].sort_values("AA")

        curve_label = "Ζήτηση (Buy)"


    # ========================================================
    # PLOT
    # ========================================================

    if curve.empty:

        st.warning(
            f"Δεν βρέθηκαν δεδομένα για "
            f"{pd.Timestamp(selected_mtu):%d/%m/%Y %H:%M}"
        )

    else:

        fig, ax = plt.subplots(
            figsize=(12, 7)
        )


        ax.plot(
            curve["QUANTITY"],
            curve["UNITPRICE"],
            lw=1.8,
            label=curve_label
        )


        # ----------------------------------------------------
        # AXES
        # ----------------------------------------------------

        ax.set_ylim(
            YMIN,
            YMAX
        )

        ax.set_xlabel(
            "Αθροιστική ποσότητα (MW)"
        )

        ax.set_ylabel(
            "Τιμή (€/MWh)"
        )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        ax.set_title(
            f"EL-DAM {curve_label} – "
            f"{pd.Timestamp(selected_mtu):%d/%m/%Y %H:%M}"
        )


        ax.grid(
            alpha=0.3
        )

        ax.legend()

        fig.tight_layout()


        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        st.pyplot(fig)


        # ====================================================
        # INFORMATION
        # ====================================================

        st.write(
            f"**Ημερομηνία:** "
            f"{pd.Timestamp(selected_mtu):%d/%m/%Y}"
        )

        st.write(
            f"**Τέταρτο:** "
            f"{pd.Timestamp(selected_mtu):%H:%M}"
        )

        st.write(
            f"**Καμπύλη:** {curve_label}"
        )
