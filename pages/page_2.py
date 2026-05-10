import plotly.graph_objects as go
import pandas as pd
import numpy as np
from itertools import cycle
import plotly.express as px
import sys
from datetime import datetime, timedelta
import streamlit as st
import base64
from pathlib import Path
import json
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import streamlit_shadcn_ui as ui
import ast
from streamlit_js_eval import streamlit_js_eval
import time
from localStoragePy import localStoragePy
import storage



class LineSimulation:

    def __init__(self, min_amount_moon_accepts, plutons_initial_proposal, moon_risk_aversion, pluton_fin_situation):
        self.min_amount_moon_accepts = min_amount_moon_accepts
        self.plutons_initial_proposal = plutons_initial_proposal
        self.moon_risk_aversion = moon_risk_aversion
        self.pluton_fin_situation = pluton_fin_situation
        self.moon_external_counsel_skill = np.random.normal(0, 0.226)
        self.pluton_external_counsel_skill = np.random.normal(0, 0.226) #0.226
        self.pluton_internal_legal_team_skill = np.random.normal(1.74, 0.3)
        if plutons_initial_proposal < min_amount_moon_accepts:
            self.instant_sett_amount = min_amount_moon_accepts
        else:
            self.instant_sett_amount = plutons_initial_proposal
        
        self.x_values = np.linspace(0, 12, 2000).tolist()

        self.y_values = []

        self.model_output()
        

    def model_output(self):
        g = self.min_amount_moon_accepts
        p = self.plutons_initial_proposal
        b = self.moon_risk_aversion
        c = self.pluton_fin_situation
        d = self.pluton_external_counsel_skill
        t = self.moon_external_counsel_skill
        j = self.pluton_internal_legal_team_skill
        a = self.instant_sett_amount
        f = 0.24

        for x in self.x_values:
            res = a + ((b**-1)*(p/1000)*x)**(d-t+2)*(10-j)**(-f*(x-c))
            self.y_values.append(res)

class LinePlot:

    def __init__(self, min_amount_moon_accepts, plutons_initial_proposal, moon_risk_aversion, pluton_fin_situation):
        self.data = [LineSimulation(min_amount_moon_accepts, plutons_initial_proposal, moon_risk_aversion, pluton_fin_situation) for i in range(300)]
        self.x_data = [element.x_values for element in self.data]
        self.y_data = [element.y_values for element in self.data]

        self.y_data = np.array(self.y_data)

        y_mean = np.mean(self.y_data.reshape(-1))
        y_max = max(self.y_data.reshape(-1))

        self.create_figure("", "Pluton's final proposal ($M)", "Months since the start of arbitration", y_max)

    def get_data(self):
        return self.x_data, self.y_data


    def create_figure(self, fig_title, yaxis_title, xaxis_title, y_max):
        fig = go.Figure().update_layout(template ="plotly_white", title = fig_title, title_x = 0.5, title_y = 0.94, title_font_weight = 600)
        fig.update_layout(autosize = False) # H465, W600
        fig.update_layout(font_family = "Georgia", font_weight = 600, font_size = 18)
        fig.update_layout(paper_bgcolor = "#FFFFFF")
        fig.update_layout(plot_bgcolor = "#FFFFFF")                                         #y_mean * 0.9, y_mean * 3 range = [450, y_max * 1.1]
        fig.update_yaxes(ticksuffix = " ", title = yaxis_title, title_standoff = 20, showgrid = True, showline = False, linecolor = "#FFFFFF", zeroline = False, title_font = dict(size = 16), tickfont = dict(size = 14))
        fig.update_layout(margin=dict(t=0, b=95, l=100, r=0))
        fig.update_xaxes(title = xaxis_title, title_standoff = 20.25, range = [-0.5, 12], showgrid = True, showline = False, linecolor = "#FFFFFF", zeroline = False, title_font = dict(size = 16), tickfont = dict(size = 14))
        self.plot_data(self.x_data, self.y_data, 3, fig)

    def find_median_values(self, data):
        median_values = []
        corresp_values = np.dstack(data)
        corresp_values = corresp_values[0]
        for element in corresp_values:
            median_values.append(np.median(element))

        return median_values

    def plot_data(self, x_data, y_data, line_width, fig):
        palette = cycle(px.colors.sequential.RdBu)
        for i in range(len(y_data)):
            fig.add_trace(go.Scatter(x = x_data[i], y = y_data[i], line = dict(width = line_width, color = next(palette)), opacity = 0.15, showlegend=False))
        median_values = self.find_median_values(y_data)

        max_y = max(median_values)

        pointer = median_values.index(max_y)

        month = x_data[0][pointer]

        self.median_maximizer = month
        self.median_maximum = max_y

        fig.add_trace(go.Scatter(x = x_data[0], y = median_values, line = dict(width = line_width, color = "#8B0000"), opacity = 1, showlegend=False))
        self.fig = fig
        return self.fig


class HistSimulation:

    def __init__(self, months_elapsed, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data
        self.calculate(months_elapsed)


    def calculate(self, months_elapsed):
        absolute_values = []

        for val in self.x_data[0]:
            absolute_values.append(abs(val-months_elapsed))

        pointer = absolute_values.index(min(absolute_values))

        self.data = np.dstack(self.y_data)[0][pointer]

        return self.data

class HistPlot:

    def __init__(self, month, x_data, y_data):
        Worlddata = HistSimulation(month, x_data, y_data)
        self.values = Worlddata.data

        self.median = np.median(self.values)

        self.create_figure(fig_title = "", yaxis_title = "Frequency", xaxis_title= f"Offers ($M) {month} month(s) after arbitration began")

    def create_figure(self, fig_title, yaxis_title, xaxis_title):
        fig = make_subplots(rows = 2, shared_xaxes = True, vertical_spacing = 0.00, row_heights=[0.3,0.7]).update_layout(template ="plotly_white", title = fig_title, title_x = 0.5, title_y = 0.94, title_font_weight = 600)
        fig.update_layout(autosize = True)
        fig.update_layout(font_family = "Georgia", font_weight = 600, font_size = 18)
        fig.update_layout(paper_bgcolor = "#FFFFFF")
        fig.update_layout(plot_bgcolor = "#FFFFFF")
        fig.update_yaxes(ticksuffix = " ", title = yaxis_title, title_standoff = 20, title_font = dict(size = 15), tickfont = dict(size = 14))
        fig.update_layout(margin=dict(t=0, b=95, l=90, r=20), showlegend = False)
        fig.update_xaxes(title = xaxis_title, title_standoff = 18, ticklabelstandoff = 10, title_font = dict(size = 15), row = 2, col = 1, tickfont = dict(size = 14))
        self.plot_data(fig, self.values, self.median)

    def plot_data(self, fig, dataset, median):

        self.median = median

        fig.add_trace(go.Histogram(x = dataset, marker_color = "#2A3F5F"), row = 2, col = 1)
        fig.add_trace(go.Box(x=dataset, marker_color = "#8B0000"), row = 1, col = 1)
        fig.update_yaxes(title_text = None, showticklabels=False, row = 1, col = 1)
        self.fig = fig
        return fig


def load_css(file_name):
    with open(file_name) as f:
        st.html(f"<style>{f.read()}</style>")


def image_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


@st.cache_data
def get_line_simulation(min_amount_moon_accepts, p, b, c):
    line_plot = LinePlot(min_amount_moon_accepts, p, b, c)
    line_maximizer = line_plot.median_maximizer
    line_maximum = line_plot.median_maximum
    x_data, y_data = line_plot.get_data()
    return x_data, y_data, line_plot.fig, line_maximizer, line_maximum


def metric_card(title, value, subtitle=None):
    subtitle_html = f'<div class="metric-card-subtitle">{subtitle}</div>' if subtitle else ""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-title">{title}</div>
            <div class="metric-card-value">{value}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def main():


    global localStorage


    if "user_storage_id" not in st.session_state:
        user_storage_id = storage.create_storage_id()
        st.session_state["user_storage_id"] = user_storage_id
    else:
        user_storage_id = st.session_state["user_storage_id"]


    localStorage = localStoragePy(f'my_app_{user_storage_id}.py')



    page_switch =  ast.literal_eval(localStorage.getItem("page_switch"))

    st.set_page_config(layout="wide")

    load_css("styles.css")

    st.markdown(
        """
        <div id="mobile-blocker">
            <div class="mobile-blocker-card">
                <h1>Desktop required</h1>
                <p>This website is optimized for laptop and desktop screens.</p>
                <p>Please open it on a larger display.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True)

    with st.container(key="page_title"):
        st.title("Legal Advice Competition Supporting Submission")

    with st.container(key = "authors"):
        st.markdown("By Alejandra Zambrano, Lucas Abrantes, Mattia De Santis, and Levente Faludi-Országh&nbsp;&nbsp;&nbsp;BIEM 18&nbsp;&nbsp;2026/05/04", unsafe_allow_html = True)

    with st.container(key="leibniz_quote"):
        st.markdown(
            '''“When there are disputes among persons, we can simply say: Let us calculate.” <br>
— Gottfried Wilhelm Leibniz''', unsafe_allow_html = True)

    with st.container(horizontal=True, horizontal_alignment="center", gap="small", key="nav_row"):

        if st.button("Overview", key="overview"):
            localStorage.setItem("page_switch", True)
            st.switch_page("streamlit_app.py")
        
        if st.button("Model description", key="model_description"):
            localStorage.setItem("page_switch", True)
            st.switch_page("pages/page_1.py")
        
        if st.button("Simulate!", key="simulation"):
            pass

        if st.button("Reset", key = "reset"):
            st.cache_data.clear()
            localStorage.clear()
            st.switch_page("streamlit_app.py")

        with open("memo.pdf", "rb") as f:
            btn = st.download_button(
                label = "Download memo",
                data = f,
                file_name = "memo.pdf",
                mime = "memo/pdf",
                icon = ":material/download:",
                key = "download"
            )

    st.divider()

    loading_placeholder = st.empty()

    if page_switch:

        loading_placeholder.markdown(
            """
            <div class="simulation-loading">
                <div class="simulation-loading-card">
                    <div class="simulation-loading-title">
                        Loading simulation<span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        localStorage.setItem("page_switch", False)

    p = int(localStorage.getItem("PIP"))
    b =  int(localStorage.getItem("MRA"))
    c = float(localStorage.getItem("PFS"))

    render = False

    while render == False:
        try:
            x_data, y_data, line_fig, line_maximizer, line_maximum = get_line_simulation(550, p, b, c)
            render = True
        except ValueError:
            pass

    with st.container(key="metric_slider_row"):
        left_col, slider_col, right_col = st.columns(
            [1, 2.2, 1],
            gap="medium",
            vertical_alignment="center"
        )


    if localStorage.getItem("slider_pos") == None:
        slider_position = 7
    else:
        slider_position = int(localStorage.getItem("slider_pos"))

    try:
        slider_position = st.session_state["month_slider"]
    except KeyError:
        pass


    hist_fig = HistPlot(slider_position, x_data, y_data)

    hist_median = hist_fig.median

    hist_fig = hist_fig.fig


    with st.container(key = "wide_chart_section"):
        col1, col2 = st.columns(2, gap="small", vertical_alignment="center")

        with col1:
            st.plotly_chart(line_fig, width="stretch", config={"scrollZoom": False}, theme = None)

        with col2:
            st.plotly_chart(hist_fig, width="stretch", config={"scrollZoom": False}, theme = None)


    with slider_col:
            slider_position = st.slider(
                "Please select a month to inspect",
                1, 12, slider_position, step = 1,
                key="month_slider"
            )

    localStorage.setItem("slider_pos", int(slider_position))

    with left_col:
        line_metric = metric_card("Metric", f"On Median, Pluton's proposals peaked at {round(line_maximum, 1)} ($M) after {round(line_maximizer, 1)} months.")

    
    with right_col:
        hist_metric = metric_card("Metric", f"Pluton proposed {round(hist_median, 1)} ($M) on median {slider_position} month(s) after the commencement of arbitration.")

    loading_placeholder.empty()

main()