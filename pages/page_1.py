import streamlit as st
import base64
from pathlib import Path
import textwrap
from streamlit_js_eval import streamlit_js_eval
from localStoragePy import localStoragePy

localStorage = localStoragePy('my_app.py')


def load_css(file_name):
    with open(file_name) as f:
        st.html(f"<style>{f.read()}</style>")



def image_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


def main():

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
            pass
        
        if st.button("Simulate!", key="simulation"):
            localStorage.setItem("page_switch", True)
            st.switch_page("pages/page_2.py")

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

    with st.container(key = "formula"):
        st.latex(r"""
\begin{aligned}
Y &: [0,\infty) \to \mathbb{R} \\
Y(x) &= a + \left(b^{-1}qx\right)^{d-t+2}\cdot (10-j)^{-f(x-c)}
\end{aligned}
""")

    col1, gap1, col2, = st.columns([1, 0.05, 1], vertical_alignment="center")

    with col1:
        with st.container(key="parameter_exp"):
            st.markdown(
        """
        <ul class="parameter-list">
            <li>
                a (also the y-intercept and asymptote) is defined by<br>
                {p &lt; g: g, p} that is, if p is less than g, than g,<br>
                otherwise p.
            </li>
            <li>p constitutes to Pluton's initial proposal amount.</li>
            <li>g is the minimum amount Moon is willing to settle for (assumed to be 550 ($M)).</li>
            <li>b represents the risk aversion of Moon.</li>
            <li>q is simply p/1000.</li>
            <li>x is the number of months elapsed since the start of arbitration (the independent variable).</li>
            <li>d signifies Pluton's external council's skill level.</li>
            <li>t, in conjunction, constitutes to Moon's external council's skill level.</li>
            <li>j stands for the Pluton's internal legal team's skill level.</li>
            <li>c represents the financial situation of Pluton.</li>
            <li>f is a calibration parameter.</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

    
    with col2:
        with st.container(key="model_exp"):
            st.markdown(
            '''
            The model endevours to support the assertions and the final strategy outlined in the report.
            It models (through 300 simulations), given a set of parameters - some of which are uncertain and drawn from normal distributions (d, t & j), Pluton's final proposal amount
            after a given amount of months spent at arbitration.
            For instance, if Moon is risk loving with an adept external council and Pluton is financially stabel with an entry level legal team and external council,
            then the maximizer (the number of months elapsed since arbitration commenced and until a deal is reached) will be much smaller, and Pluton's final offer will be substantially higher. <br>

            *To interact with the model, you may alter p, b, and c on the 'Overview' page. These changes will then be reflected after clicking 'Simulate!' in the top ribbon. To reset the model and clear
            cached data, press 'Reset'.*
            
            ''', unsafe_allow_html = True)

main()