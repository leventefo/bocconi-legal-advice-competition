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
import ast
from streamlit_js_eval import streamlit_js_eval
from localStoragePy import localStoragePy
import uuid
import storage
import storage_id_cleanup
import os
from pathlib import Path
import random

class SingleLineSimualtion:

    def __init__(self, min_amount_moon_accepts, plutons_initial_proposal, moon_risk_aversion, pluton_fin_situation):
        self.min_amount_moon_accepts = min_amount_moon_accepts
        self.plutons_initial_proposal = plutons_initial_proposal
        self.moon_risk_aversion = moon_risk_aversion
        self.pluton_fin_situation = pluton_fin_situation
        self.moon_external_counsel_skill = 0
        self.pluton_external_counsel_skill = 0
        self.pluton_internal_legal_team_skill = 1.74

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


class SingleLinePlot:

    def __init__(self, min_amount_moon_accepts, plutons_initial_proposal, moon_risk_aversion, pluton_fin_situation):
        self.data = [SingleLineSimualtion(min_amount_moon_accepts, plutons_initial_proposal, moon_risk_aversion, pluton_fin_situation) for i in range(1)]
        self.x_data = [element.x_values for element in self.data]
        self.y_data = [element.y_values for element in self.data]

        self.y_data = np.array(self.y_data)

        y_mean = np.mean(self.y_data.reshape(-1))

        y_max = max(self.y_data.reshape(-1).tolist())

        if y_max <= 900:
            y_max = 900
        
        else:
            y_max = y_max * 1.1

        if max(self.y_data.reshape(-1)) >= 2000:
            sys.exit()

        self.create_figure("", "Pluton's final proposal ($M)", "Months elapsed since the start of arbitration", y_mean, y_max)

    def create_figure(self, fig_title, yaxis_title, xaxis_title, y_mean, y_max):
        fig = go.Figure().update_layout(template ="plotly_white", title = fig_title, title_x = 0.5, title_y = 0.94, title_font_weight = 600)
        fig.update_layout(autosize = True)
        fig.update_layout(font_family = "Georgia", font_weight = 600, font_size = 18)
        fig.update_layout(paper_bgcolor = "#FFFFFF")
        fig.update_layout(plot_bgcolor = "#FFFFFF")                                         #y_mean * 0.9, y_mean * 3
        fig.update_yaxes(ticksuffix = " ", title = yaxis_title, title_standoff = 20, range = [500, y_max], showgrid = True, showline = False, linecolor = "#FFFFFF", zeroline = False, title_font = dict(size = 20), tickfont = dict(size = 18))
        fig.update_layout(margin=dict(t=0, b=65, l=100, r=0))
        fig.update_xaxes(title = xaxis_title, title_standoff = 20, range = [-0.5, 12], showgrid = True, showline = False, linecolor = "#FFFFFF", zeroline = False, title_font = dict(size = 20), tickfont = dict(size = 18))
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

        fig.add_trace(go.Scatter(x = x_data[0], y = median_values, line = dict(width = line_width, color = "#8B0000"), opacity = 1, showlegend=False))
        fig.add_vline(x=month, line_width=3, line_dash="dash", line_color="#12294F", annotation_text = f"  Pluton's proposal peaked at {round(max_y, 1)} ($M) after {round(month, 1)} months.", annotation_position="top right")
        fig.update_annotations(font=dict(size = 13, color = "#12294F"))
        st.plotly_chart(fig, config = {'scrollZoom': False}, theme = None)


def load_css(file_name):
    with open(file_name) as f:
        st.html(f"<style>{f.read()}</style>")


def save_to_local_storage(to_save_param):

    for key, value in to_save_param.items():
        localStorage.setItem(key, value)


def main():

    file = Path.home() / ".config" / "localStoragePy"

    if not file.exists():
        with open("last_cleanup.txt", "w") as f:
            f.write(str(datetime.now().isoformat()))
    elif file.exists():
        content = f.read_text().strip()

        if not content:
            with open("last_cleanup.txt", "w") as f:
                f.write(str(datetime.now().isoformat()))


    with open("last_cleanup.txt", "r") as f:
        last_cleanup_time = datetime.fromisoformat(f.read().strip())

    if datetime.now() - last_cleanup_time >= timedelta(minutes=120):
        storage_id_cleanup.main()


    global localStorage

    if "user_storage_id" not in st.session_state:
        user_storage_id = storage.create_storage_id()
        st.session_state["user_storage_id"] = user_storage_id
    else:
        user_storage_id = st.session_state["user_storage_id"]


    localStorage = localStoragePy(f'my_app_{user_storage_id}.py')

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
        

    nav_row_container = st.container(horizontal=True, horizontal_alignment="center", gap="small", key="nav_row")

    with nav_row_container:

        if st.button("Overview", key="overview"):
            pass
        
        if st.button("Model description", key="model_description"):
            localStorage.setItem("page_switch", True)
            st.switch_page("pages/page_1.py")
        
        if st.button("Simulate!", key="simulation"):
            localStorage.setItem("page_switch", True)
            st.switch_page("pages/page_2.py")
        
        if st.button("Reset", key = "reset"):
            st.session_state["left_slider"] = 650
            st.session_state["middle_slider"] = 75
            st.session_state["right_slider"] = 25.0

            st.cache_data.clear()
            localStorage.clear()

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

    col1, gap1, col2, gap2, col3 = st.columns([1, 0.1, 1, 0.1, 1])

    if (localStorage.getItem("PIP") != None) and (localStorage.getItem("MRA") != None) and (localStorage.getItem("PFS") != None):
        ls = int(localStorage.getItem("PIP"))
        ms = int(localStorage.getItem("MRA"))
        rs = float(localStorage.getItem("PFS"))
    
    else:
        ls, ms, rs = 650, 75, 25.0


    with col1:
        val1 = st.slider("Pluton's initial proposal ($M)", 550, 750, ls, key = "left_slider")
  
    with col2:
        val2 = st.slider("Moon's risk aversion", 45, 105, ms, key = "middle_slider")

    with col3:
        val3 = st.slider("Pluton's financial situation", 23.0, 27.0, rs, key = "right_slider")


    states_dict = {"left_slider" : val1, "middle_slider" : val2, "right_slider" : val3}

    to_save = {"PIP" : val1, "MRA" : val2, "PFS" : val3}

    SingleLinePlot(550, val1, val2, val3)

    save_to_local_storage(to_save)

main()
    


