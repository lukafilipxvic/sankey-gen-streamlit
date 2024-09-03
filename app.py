"""This module contains code for creating a dynamic Sankey diagram using Streamlit."""

import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sankeyflow import Sankey
from matplotlib import rcParams

st.set_page_config(layout="wide", page_title="Sankey Diagram Generator")
st.title("Sankey Diagram Generator")

st.sidebar.title("Sankey Diagram")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)

if "df" in st.session_state:
    columns = st.session_state.df.columns.tolist()
    source_col = st.sidebar.selectbox("Select Source Column", columns, index=0, key="source_col")
    target_col = st.sidebar.selectbox("Select Target Column", columns, index=1, key="target_col")
    value_col = st.sidebar.selectbox("Select Value Column", columns, index=2, key="value_col")
else:
    source_col, target_col, value_col = None, None, None

st.sidebar.number_input("Font Size", 5, 20, 10, 1, key="font_size")
st.sidebar.number_input("Curviness", 0, 10, 3, 1, key="curvature")
st.sidebar.selectbox(
    "Color Palette",
    index=0,
    options=["tab10", "tab20", "Pastel1", "Pastel2", "Set1", "Set2", "Set3", "Oranges", "plasma", "autumn"],
    key="color",
)
st.sidebar.selectbox("Flow Color Mode", index=0, options=["source", "dest"], key="flow_color_mode")
remove_labels = st.sidebar.checkbox("Remove Numbers", value=False)
st.sidebar.markdown("---")  # Horizontal line
st.sidebar.markdown("**[Luka Filipovic](https://lukafilipovic.com/)**")  # Bold text

def load_demo_df():
    st.session_state.df = pd.DataFrame(
        {
            "Col 1": ["Product", "Service and other", "Total revenue", "Total revenue"],
            "Col 2": ["Total revenue", "Total revenue", "Gross margin", "Cost of revenue"],
            "Value": [20779, 30949, 34768, 10000],
        }
    )


def draw_sankey(df, source, target, value, remove_labels):
    flows = list(df[[source, target, value]].itertuples(index=False, name=None))
    # Remove empty and nan values
    flows_clean = [x for x in flows if x[0] and x[1] and x[2] > 0]
    
    # Set the font to Arial
    rcParams['font.family'] = 'Arial'
    
    diagram = Sankey(
        flows=flows_clean,
        cmap=plt.get_cmap(st.session_state.color),
        flow_color_mode=st.session_state.flow_color_mode,
        node_opts=dict(
            label_format='{label}',
            label_opts={"fontsize": st.session_state.font_size, "ha": "right"}
            ) if remove_labels else dict(
            label_format='{label} - {value}', label_opts: {"fontsize": st.session_state.font_size, "ha": "right"}
        ),
        flow_opts={"curvature": st.session_state.curvature / 10.0},
    )

    _, col2, _ = st.columns([1, 7, 1])
    with col2:
        diagram.draw()
        st.pyplot(plt)
        img = io.BytesIO()
        plt.savefig(img, format="png")
        st.session_state.image = img


def empty_df():
    df = pd.DataFrame({"source": [""], "target": [""], "value": [None]})
    st.session_state.df = df.astype({"value": float})


def timestamp():
    return pd.Timestamp.now().strftime("%Y%m%d%H%M%S")


if "df" not in st.session_state:
    load_demo_df()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button("Empty Table", on_click=empty_df)
with col2:
    st.button("Load Demo", on_click=load_demo_df)
with col3:
    st.download_button(
        "Download Table",
        data=st.session_state.df.to_csv(index=False),
        file_name=f"sankey-{timestamp()}.csv",
        mime="text/csv",
    )
with col4:
    download_button_placeholder = st.empty()

if source_col and target_col and value_col:
    edited_df = st.data_editor(
        st.session_state.df,
        key="demo_df",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )

    sankey_placeholder = st.empty()
    draw_sankey(edited_df, source_col, target_col, value_col, remove_labels)

    if "image" in st.session_state and st.session_state.image:
        download_button_placeholder.download_button(
            "Download Diagram",
            data=st.session_state.image,
            file_name=f"sankey-{timestamp()}.png",
            mime="image/png",
        )
