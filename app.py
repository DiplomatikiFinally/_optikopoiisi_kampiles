import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SETTINGS
# ============================================================

duration = 15
ymin = -20
ymax = 400


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
# STREAMLIT
# ============================================================

st.title("EL-DAM Offer Curves")

uploaded_file = st.file_uploader(
    "Ανέβασε το Excel αρχείο",
    type=["xlsx"]
)


# ============================================================
# WAIT FOR FILE
# ============================================================

if uploaded_file is not None:

    # Διαβάζουμε το Excel
    df = load_excel(uploaded_file)

    # Κρατάμε μόνο 15λεπτα
    df = df[
        df["DELIVERY_DURATION"] == duration
    ].copy()

    # ========================================================
    # SELECT QUARTER
    # ========================================================

    mtus = sorted(df["MTU"].unique())

    selected_mtu = st.selectbox(
        "Επίλεξε τέταρτο:",
        mtus,
        format_func=lambda x:
            pd.Timestamp(x).strftime("%H:%M")
    )

    # ========================================================
    # SELECTED MTU
    # ========================================================

    d = df[
        df["MTU"] == selected_mtu
    ]

    # Μόνο προσφορές Sell
    sell = d[
        d["SIDE_DESCR"] == "Sell"
    ].sort_values("AA")

    # ========================================================
    # PLOT
    # ========================================================

    if sell.empty:

        st.warning(
            f"Δεν βρέθηκαν προσφορές για "
            f"{pd.Timestamp(selected_mtu):%d/%m/%Y %H:%M}"
        )

    else:

        fig, ax = plt.subplots(
            figsize=(10, 6)
        )

        ax.plot(
            sell["QUANTITY"],
            sell["UNITPRICE"],
            color="#1f77b4",
            lw=1.8,
            label="Προσφορά (Sell)"
        )

        ax.set_ylim(
            ymin,
            ymax
        )

        ax.set_xlabel(
            "Αθροιστική ποσότητα (MW)"
        )

        ax.set_ylabel(
            "Τιμή (€/MWh)"
        )

        ax.set_title(
            f"EL-DAM Offer Curve – "
            f"{pd.Timestamp(selected_mtu):%d/%m/%Y %H:%M}"
        )

        ax.grid(
            alpha=0.3
        )

        ax.legend()

        fig.tight_layout()

        st.pyplot(fig)