import streamlit as st
import pandas as pd
import plotly.graph_objects as go

DURATION = 15

st.set_page_config(
    page_title="EL-DAM Curves",
    layout="wide"
)

st.title("EL-DAM Curves")

uploaded_file = st.file_uploader(
    "Ανέβασε το Excel αρχείο",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Ανέβασε ένα Excel αρχείο για να ξεκινήσεις.")
    st.stop()


@st.cache_data
def load_excel(file):
    df = pd.read_excel(file)

    df["MTU"] = pd.to_datetime(
        df["DELIVERY_MTU"],
        format="%Y/%m/%d %H:%M:%S"
    )

    return df


df = load_excel(uploaded_file)

# Κρατάμε μόνο 15λεπτα
df = df[
    df["DELIVERY_DURATION"] == DURATION
].copy()

# Διαθέσιμες ημερομηνίες / ώρες
available_dates = sorted(
    df["MTU"].dt.date.unique()
)

available_times = sorted(
    df["MTU"].dt.strftime("%H:%M").unique()
)


# --------------------------------------------------
# Επιλογές καμπυλών
# --------------------------------------------------

st.subheader("Καμπύλες προς εμφάνιση")

# Αρχικές γραμμές
default_rows = pd.DataFrame({
    "Ημερομηνία": [available_dates[0], available_dates[0]],
    "Τέταρτο": ["12:00", "12:15"],
    "Τύπος": ["Buy", "Sell"]
})

edited = st.data_editor(
    default_rows,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Ημερομηνία": st.column_config.DateColumn(
            "Ημερομηνία",
            format="DD/MM/YYYY"
        ),

        "Τέταρτο": st.column_config.SelectboxColumn(
            "Τέταρτο",
            options=available_times
        ),

        "Τύπος": st.column_config.SelectboxColumn(
            "Τύπος",
            options=["Buy", "Sell"]
        )
    },
    hide_index=True
)


# --------------------------------------------------
# Έλεγχος
# --------------------------------------------------

if edited.empty:
    st.warning("Πρόσθεσε τουλάχιστον μία καμπύλη.")
    st.stop()


# --------------------------------------------------
# Plot
# --------------------------------------------------

fig = go.Figure()

for _, selection in edited.iterrows():

    selected_date = selection["Ημερομηνία"]
    selected_time = selection["Τέταρτο"]
    selected_side = selection["Τύπος"]

    # Δημιουργούμε το MTU
    mtu = pd.Timestamp(
        f"{selected_date} {selected_time}"
    )

    curve = df[
        (df["MTU"] == mtu)
        &
        (df["SIDE_DESCR"] == selected_side)
    ].sort_values("AA")

    if curve.empty:
        continue

    name = (
        f"{pd.Timestamp(selected_date):%d/%m/%Y} "
        f"{selected_time} - "
        f"{selected_side}"
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


# --------------------------------------------------
# Layout
# --------------------------------------------------

fig.update_layout(
    title="EL-DAM Aggregated Curves",

    xaxis_title="Αθροιστική ποσότητα (MW)",

    yaxis_title="Τιμή (€/MWh)",

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


st.plotly_chart(
    fig,
    use_container_width=True
)
