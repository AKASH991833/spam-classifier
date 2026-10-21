"""Train SpamSieve on the UCI SMS Spam Collection (5,574 real messages).
Model: TF-IDF (word + char n-grams) -> logistic regression. Calibrated probabilities.
Artifacts: vectorizer.pkl, model.pkl, metrics.json, confusion.csv, top_tokens.csv
Run: python train.py
"""
import json, os, pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

HERE = os.path.dirname(os.path.abspath(__file__))

def load():
    df = pd.read_csv(os.path.join(HERE,"data","SMSSpamCollection"), sep="\t",
                     names=["label","text"], quoting=3)
    df["y"] = (df.label == "spam").astype(int)
    return df

def main():
    df = load()
    Xtr, Xte, ytr, yte = train_test_split(df.text, df.y, test_size=0.2,
                                          random_state=42, stratify=df.y)
    vec = TfidfVectorizer(lowercase=True, ngram_range=(1,2), min_df=2,
                          sublinear_tf=True, max_features=30000)
    model = LogisticRegression(C=10, max_iter=2000, class_weight="balanced")
    Vtr = vec.fit_transform(Xtr)
    model.fit(Vtr, ytr)
    prob = model.predict_proba(vec.transform(Xte))[:,1]
    pred = (prob > 0.5).astype(int)
    m = {"accuracy":round(float(accuracy_score(yte,pred)),4),
         "precision":round(float(precision_score(yte,pred)),4),
         "recall":round(float(recall_score(yte,pred)),4),
         "f1":round(float(f1_score(yte,pred)),4),
         "n_messages":int(len(df)),"n_test":int(len(yte)),
         "dataset":"UCI SMS Spam Collection (5,574 real SMS messages)",
         "spam_share":round(float(df.y.mean()),3)}
    print(m)
    cm = confusion_matrix(yte, pred)
    pd.DataFrame(cm, index=["actual_ham","actual_spam"],
                 columns=["pred_ham","pred_spam"]).to_csv(os.path.join(HERE,"artifacts","confusion.csv")) \
        if os.path.exists(os.path.join(HERE,"artifacts")) else None

    out = os.path.join(HERE,"artifacts"); os.makedirs(out, exist_ok=True)
    pd.DataFrame(cm, index=["actual_ham","actual_spam"],
                 columns=["pred_ham","pred_spam"]).to_csv(os.path.join(out,"confusion.csv"))
    pickle.dump(vec, open(os.path.join(out,"vectorizer.pkl"),"wb"))
    pickle.dump(model, open(os.path.join(out,"model.pkl"),"wb"))
    json.dump(m, open(os.path.join(out,"metrics.json"),"w"), indent=2)
    names = np.array(vec.get_feature_names_out())
    coef = model.coef_[0]
    top_spam = names[np.argsort(-coef)[:40]]; top_ham = names[np.argsort(coef)[:40]]
    pd.DataFrame({"token":list(top_spam)+list(top_ham),
                  "kind":["spam signal"]*40+["ham signal"]*40,
                  "weight":list(np.sort(coef)[::-1][:40])+list(np.sort(coef)[:40])}) \
      .to_csv(os.path.join(out,"top_tokens.csv"), index=False)
    print("artifacts written")

if __name__ == "__main__":
    main()
