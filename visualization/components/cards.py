# UI kart bileşenleri (sadece render).
import streamlit as st


def render_proof_card(title, proof, key=""):
    status = proof.get("pass")
    if status is True:
        label, color = "PASS", "#10b981"
    elif status is False:
        label, color = "FAIL", "#ef4444"
    else:
        label, color = "-", "#6b7280"
    detail = proof.get("detail") or ""
    st.markdown("**%s**" % title)
    st.markdown("<span style='color:%s; font-weight:bold'>%s</span> %s" % (color, label, detail), unsafe_allow_html=True)
