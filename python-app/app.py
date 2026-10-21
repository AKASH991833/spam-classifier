"""SpamSieve - SMS spam detection (Streamlit).
Run: streamlit run app.py
Model: TF-IDF + logistic regression on the UCI SMS Spam Collection.
"""
import json, os, pickle
import numpy as np
import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(page_title="SpamSieve - Spam Classifier", page_icon="🛡️", layout="wide")

@st.cache_resource
def load_model():
    a = os.path.join(HERE,"artifacts")
    vec = pickle.load(open(os.path.join(a,"vectorizer.pkl"),"rb"))
    model = pickle.load(open(os.path.join(a,"model.pkl"),"rb"))
    return vec, model

@st.cache_data
def load_meta():
    a = os.path.join(HERE,"artifacts")
    return (json.load(open(os.path.join(a,"metrics.json"))),
            pd.read_csv(os.path.join(a,"top_tokens.csv")),
            pd.read_csv(os.path.join(a,"confusion.csv"), index_col=0))

vec, model = load_model()
metrics, tokens, cm = load_meta()

st.title("🛡️ SpamSieve")
st.caption("Paste any SMS or message - a logistic-regression model trained on 5,574 real "
           "texts (UCI SMS Spam Collection) judges it and shows its reasoning.")

default = "Congratulations! You have WON a free iPhone 16. Claim now at win-big.example - text STOP to opt out"
msg = st.text_area("Message to classify", value=default, height=100)

def classify(text):
    X = vec.transform([text])
    prob = float(model.predict_proba(X)[0,1])
    names = np.array(vec.get_feature_names_out())
    coef = model.coef_[0]
    row = X.toarray()[0]
    hits = [(names[i], coef[i]*row[i]) for i in row.nonzero()[0]]
    hits = sorted(hits, key=lambda h: -abs(h[1]))[:8]
    return prob, hits

if msg.strip():
    prob, hits = classify(msg)
    c1, c2, c3 = st.columns(3)
    c1.metric("Spam probability", f"{prob*100:.0f}%")
    c2.metric("Verdict", "SPAM 🚫" if prob > 0.5 else "Looks fine ✅")
    c3.metric("Confidence", "High" if abs(prob-0.5) > 0.4 else "Moderate" if abs(prob-0.5) > 0.15 else "Low")
    st.progress(min(1.0, prob))
    if hits:
        st.subheader("Why - the words that tipped it")
        why = pd.DataFrame(hits, columns=["token","contribution"])
        why["direction"] = np.where(why.contribution > 0, "toward spam", "toward legit")
        st.dataframe(why, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Model report card (1,115 unseen messages)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Accuracy", f"{metrics['accuracy']*100:.1f}%")
c2.metric("Precision", f"{metrics['precision']*100:.1f}%", "when it says spam")
c3.metric("Recall", f"{metrics['recall']*100:.1f}%", "spam it catches")
c4.metric("F1", f"{metrics['f1']*100:.1f}%")
st.caption(f"Confusion matrix: {int(cm.loc['actual_ham','pred_ham'])} ham correctly passed, "
           f"{int(cm.loc['actual_spam','pred_spam'])} spam correctly caught, "
           f"{int(cm.loc['actual_spam','pred_ham'])} spam missed, "
           f"{int(cm.loc['actual_ham','pred_spam'])} legit messages wrongly flagged.")

st.subheader("Strongest learned signals")
kind = st.radio("Show", ["spam signal","ham signal"], horizontal=True)
d = tokens[tokens.kind == kind].head(15)
st.bar_chart(d.set_index("token")["weight"])

with st.sidebar:
    st.subheader("Honest limits")
    st.caption("Trained on English SMS from 2011-2012. Modern WhatsApp forwards, "
               "Hindi/Hinglish texts and fresh scam phrasing can slip through or get "
               "over-flagged. Precision matters: a legit message wrongly flagged is "
               "worse than spam that sneaks in - the threshold is tuned for that.")
