import io
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sankeyflow import Sankey

st.set_page_config(layout="wide", page_title="Sankey Diagram Generator")
st.title("Sankey Diagram Generator")

st.sidebar.title("Sankey Diagram")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

def load_demo_df():
    return pd.DataFrame(
        {
            "Col 1": ["Product", "Service and other", "Total revenue", "Total revenue"],
            "Col 2": ["Total revenue", "Total revenue", "Gross margin", "Cost of revenue"],
            "Value": [20779, 30949, 34768, 10000],
        }
    )

def draw_sankey(df, source, target, value, remove_labels):
    # Filter out rows where the source and target are the same
    df_filtered = df[df[source] != df[target]]
    flows_clean = [x for x in df_filtered[[source, target, value]].itertuples(index=False, name=None) if all(x)]
    
    # Calculate a reasonable figure size based on the number of flows or nodes
    num_flows = len(flows_clean)
    num_nodes = len(set(df_filtered[source]).union(df_filtered[target]))
    
    # Use a size that scales with the number of nodes or flows
    fig_width = st.session_state.chart_width
    fig_height = st.session_state.chart_height
    
    plt.figure(figsize=(fig_width, fig_height))
    
    plt.rcParams['font.family'] = 'Arial'
    diagram = Sankey(
        flows=flows_clean,
        cmap=plt.get_cmap(st.session_state.color),
        flow_color_mode=st.session_state.flow_color_mode,
        node_opts={"label_format": '{label}' if remove_labels else '{label} - {value}', "label_opts": {"fontsize": st.session_state.font_size}},
        flow_opts={"curvature": st.session_state.curvature / 10.0},
    )

    for row in df_filtered[target].unique():
        node = diagram.find_node(row)[0]
        node.label_pos = 'right'
        
    _, col2, _ = st.columns([1, 7, 1])
    with col2:
        diagram.draw()
        st.pyplot(plt)
        img = io.BytesIO()
        plt.savefig(img, format="png", bbox_inches="tight")  # Use bbox_inches="tight" to ensure no clipping
        plt.close()  # Close the figure to free memory
        st.session_state.image = img

def timestamp():
    return pd.Timestamp.now().strftime("%Y%m%d%H%M%S")

if uploaded_file:
    st.session_state.df = pd.read_csv(uploaded_file)
elif "df" not in st.session_state:
    st.session_state.df = load_demo_df()

columns = st.session_state.df.columns.tolist() if "df" in st.session_state else []
source_col = st.sidebar.selectbox("Select Source Column", columns, index=0, key="source_col") if columns else None
target_col = st.sidebar.selectbox("Select Target Column", columns, index=1, key="target_col") if columns else None
value_col = st.sidebar.selectbox("Select Value Column", columns, index=2, key="value_col") if columns else None

st.sidebar.number_input("Font Size", 5, 20, 10, 1, key="font_size")
st.sidebar.number_input("Curviness", 0, 10, 3, 1, key="curvature")
st.sidebar.selectbox("Color Palette", options=["tab10", "tab20", "Pastel1", "Pastel2", "Set1", "Set2", "Set3", "Oranges", "plasma", "autumn"], key="color")
st.sidebar.selectbox("Flow Color Mode", options=["source", "dest"], key="flow_color_mode")
remove_labels = st.sidebar.checkbox("Remove Numbers", value=False)

st.sidebar.number_input("Chart Width", 9, key="chart_width")
st.sidebar.number_input("Chart Height", 9, key="chart_height")

st.sidebar.markdown("---")  
st.sidebar.markdown("**[Luka Filipovic](https://lukafilipovic.com)**")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button("Empty Table", on_click=lambda: st.session_state.update(df=pd.DataFrame({"source": [""], "target": [""], "value": [None]}).astype({"value": float})))
with col2:
    st.button("Load Demo", on_click=lambda: st.session_state.update(df=load_demo_df()))
with col3:
    st.download_button("Download Table", data=st.session_state.df.to_csv(index=False), file_name=f"sankey-{timestamp()}.csv", mime="text/csv")
with col4:
    download_button_placeholder = st.empty()

if source_col and target_col and value_col:
    edited_df = st.data_editor(st.session_state.df, key="demo_df", num_rows="dynamic", use_container_width=True, hide_index=True)
    sankey_placeholder = st.empty()
    draw_sankey(edited_df, source_col, target_col, value_col, remove_labels)

    if "image" in st.session_state and st.session_state.image:
        download_button_placeholder.download_button("Download Diagram", data=st.session_state.image, file_name=f"sankey-{timestamp()}.png", mime="image/png")
        
