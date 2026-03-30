# app/utils/style.py
import streamlit as st

def apply_global_style():
    """
    Inject global CSS for a consistent, professional dark theme
    across all pages of the dashboard.
    """
    st.markdown("""
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Background ── */
    .stApp {
        background-color: #0f1117;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #1a1d2e;
        border-right: 1px solid #2d3250;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #a0a8c0;
        font-size: 0.85rem;
    }

    /* ── Metric cards ── */
    div[data-testid="metric-container"] {
        background-color: #1a1d2e;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 16px 20px;
        transition: border-color 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #e74c3c;
    }
    div[data-testid="metric-container"] label {
        color: #a0a8c0 !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }

    /* ── Page title ── */
    h1 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        letter-spacing: -0.02em;
        padding-bottom: 0.2rem;
    }
    h2 {
        color: #e8e8e8 !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        margin-top: 1.5rem !important;
    }
    h3 {
        color: #a0a8c0 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-top: 1.2rem !important;
    }

    /* ── Divider ── */
    hr {
        border: none;
        border-top: 1px solid #2d3250;
        margin: 1rem 0;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1d2e;
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #a0a8c0;
        font-size: 0.85rem;
        font-weight: 500;
        padding: 6px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e74c3c !important;
        color: #ffffff !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background-color: #e74c3c;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 8px 20px;
        transition: background-color 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #c0392b;
    }

    /* ── Multiselect & Slider ── */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #e74c3c !important;
        border-radius: 4px;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border: 1px solid #2d3250;
        border-radius: 8px;
        overflow: hidden;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background-color: #1a1d2e !important;
        border: 1px solid #2d3250 !important;
        border-radius: 8px !important;
        color: #a0a8c0 !important;
        font-size: 0.85rem !important;
    }

    /* ── Caption / small text ── */
    .stCaption {
        color: #606480 !important;
        font-size: 0.78rem !important;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    @media (max-width: 900px) {
        header {
            visibility: visible !important;
        }
        #MainMenu {
            visibility: visible !important;
        }
    }

    /* ── Page padding ── */
    .block-container {
        padding-top: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
    }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """Render a consistent page header across all pages."""
    st.markdown(f"""
    <div style="
        padding: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #e74c3c;
        margin-bottom: 1.5rem;
    ">
        <div style="
            font-size: 0.75rem;
            color: #e74c3c;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.3rem;
        ">SAHEL SECURITY ANALYSIS</div>
        <h1 style="
            margin: 0;
            color: #ffffff;
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        ">{title}</h1>
        { f'<p style="margin: 0.4rem 0 0 0; color: #a0a8c0; font-size: 0.9rem;">{subtitle}</p>'
          if subtitle else '' }
    </div>
    """, unsafe_allow_html=True)


def stat_card(label: str, value: str, color: str = "#e74c3c", delta: str = ""):
    """
    Custom styled stat card — use instead of st.metric for more control.
    """
    delta_html = (
        f'<div style="font-size:0.78rem;color:#2ecc71;margin-top:4px;">{delta}</div>'
        if delta else ""
    )
    st.markdown(f"""
    <div style="
        background-color: #1a1d2e;
        border: 1px solid #2d3250;
        border-left: 3px solid {color};
        border-radius: 10px;
        padding: 16px 20px;
    ">
        <div style="
            font-size: 0.75rem;
            color: #a0a8c0;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        ">{label}</div>
        <div style="
            font-size: 1.7rem;
            color: #ffffff;
            font-weight: 700;
            letter-spacing: -0.02em;
        ">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
