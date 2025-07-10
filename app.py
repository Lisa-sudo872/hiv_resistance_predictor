import streamlit as st 
import os, re, joblib
import numpy as np 
import pandas as pd 
import xgboost as xgb 
from auth.auth_utils import authenticate_user, register_user
from db_utils import init_db, save_prediction, get_user_history, delete_prediction

init_db()

# --- Styling ---

LOGIN_BOX_STYLE = """

<style>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 90vh;
}
.login-box {
    background: white;
    padding: 2rem;
    border-radius: 15px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 0 20px rgba(0,0,0,0.15);
    text-align: center;
    font-family: 'Segoe UI', sans-serif;
    color: #0f1e39;
}
.login-box h1 {
    margin-bottom: 1.5rem;
    color: #00bcd4;
}
.stTextInput input, .stPassword input {
    background-color: #f0f4f8;
    border-radius: 8px;
    border: 1px solid #00bcd4;
    color: #0f1e39;
    padding: 8px;
    width: 100%;
    margin-bottom: 1rem;
}
button[kind="primary"] {
    background-color: #00bcd4 !important;
    color: white !important;
    border-radius: 10px !important;
    width: 100%;
    padding: 10px;
    font-weight: bold;
}
.stRadio > div {
    flex-direction: row !important;
    justify-content: center;
    margin-bottom: 1rem;
    color: #0f1e39;
}
</style>""" 
st.markdown(LOGIN_BOX_STYLE, unsafe_allow_html=True)

# --- Auth ---

def login_screen(): 
    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True) 
    st.markdown('<h1>HIV-1 RESISTANCE PREDICTOR Login</h1>', unsafe_allow_html=True) 
    choice = st.radio("Mode", ["Login", "Register"], horizontal=True) 
    username = st.text_input("Username") 
    password = st.text_input("Password", type="password")

    if choice == "Login":
     if st.button("Login"):
        if authenticate_user(username, password):
            st.success(f"Welcome back, {username}!")
            st.session_state["authenticated"] = True
            st.session_state["user"] = username
        else:
            st.error("Invalid username or password.")
    else:
     if st.button("Register"):
        if register_user(username, password):
            st.success("Account created. Please login.")
        else:
            st.warning("Username already exists.")

    st.markdown('</div></div>', unsafe_allow_html=True)

# --- Session Check ---

if "authenticated" not in st.session_state or not st.session_state["authenticated"]: 
    login_screen() 
    st.stop()

st.write(f"Welcome {st.session_state['user']}!")

# --- Load Models ---

tfidf_vectorizer = joblib.load("models/tfidf_vectorizer.pkl") 
boosters = [] 
for i in range(6): 
    bst = xgb.Booster() 
    bst.load_model(f"models/xgb_booster_label_{i}.json") 
    boosters.append(bst)

# --- Constants ---

drug_labels = ["3TC", "ABC", "D4T", "AZT", "DDI", "TDF"] 
res_labels = ["Susceptible", "Potential Low Resistance", "Low Resistance", "Intermediate Resistance", "High Resistance"] 
KNOWN_NRTI_DRMS = {"M184V", "K65R", "D67N", "K70R", "L210W", "T215Y", "T215F", "K219Q", "K219E", "M41L", "A62V", "T69D", "L74V"} 
CROSS_EFFECTS_DETAILED = {"M184V": {"effect": "↑ AZT & TDF susceptibility; 3TC resistance", "clinical": "Keep AZT/TDF despite 3TC failure."}, 
                          "K65R": {"effect": "↓ TDF, ABC, 3TC susceptibility", "clinical": "Avoid TDF/ABC if K65R present."}, 
                         "T215Y": {"effect": "Major TAM, high AZT resistance", "clinical": "Key TAM-1 mutation."},
                         "M41L": {"effect": "TAM → AZT/D4T resistance", "clinical": "Part of TAM-1 cluster."},
                         "D67N": {"effect": "TAM → AZT/D4T resistance", "clinical": "Adds when with others."},
                         "K70R": {"effect": "TAM → AZT/D4T resistance", "clinical": "Common early TAM."},
                         "L210W": {"effect": "TAM → AZT/D4T resistance", "clinical": "Enhances TAM pattern."},
                         "T215F": {"effect": "TAM similar to T215Y", "clinical": "High AZT resistance."},
                         "K219Q": {"effect": "Minor TAM", "clinical": "Adds to AZT resistance."},
                        "K219E": {"effect": "Minor TAM", "clinical": "Adds to AZT resistance."},
                        "A62V": {"effect": "Part of Q151M complex multi-drug reisstance complex", "clinical": "Broad NRTI resistance."},
                        "T69D": {"effect": "Indicates multi-NRTI pattern", "clinical": "Little alone."},
                        "L74V": {"effect": "↓ ABC & DDI susceptibility: reduces sensitivity to these drugs", "clinical": "Compromises ABC/ddI."}


                          
                          } 
WT = "PISPIETVPVKLKPGMDGPKVKQWPLTEEKIKALVEICTEMEKEGKISKIGPENPYNTPVFAIKKKDSTKWRKLVDFRELNKRTQDFWEVQLGIPHPAGLKKKKSVTVLDVGDAYFSVPLDKDFRKYTAFTIPSINNETPGIRYQYNVLPQGWKGSPAIFQSSMTKILEPFRKQNPDIVIYQYMDDLYVGSDLEIGQHRTKIEELRQHLLW"[:240]

# --- Utilities ---

def list_mutations(seq): 
    seq = re.sub(r"[^A-Za-z]", "", seq.upper()) 
    padded_seq = (seq + WT[len(seq):])[:len(WT)] 
    mutations = []
    for i, (wt, aa) in enumerate(zip(WT, padded_seq),start=1):
        if wt != aa:
            mutations.append(f"{wt}{i}{aa}")
    return mutations 
    

def kmers(seq, k=5): 
    return " ".join(seq[i:i+k] for i in range(len(seq)-k+1))

def boosters_predict(X_csr): 
    dmat = xgb.DMatrix(X_csr) 
    preds = [np.argmax(bst.predict(dmat), axis=1) for bst in boosters] 
    return np.vstack(preds).T

def mutation_notes(muts): 
    return "\n".join([f"{m} — {CROSS_EFFECTS_DETAILED.get(m, {}).get('effect', 'clinical impact unknown')}  \n_{CROSS_EFFECTS_DETAILED.get(m, {}).get('clinical', '')}_" for m in muts]) if muts else "None"

# --- Sidebar Nav ---

page = st.sidebar.selectbox("Navigate", ["New Prediction", "Dashboard", "Logout"], key="nav")

if page == "Logout": 
    st.session_state.clear() 
    st.experimental_rerun()

elif page == "Dashboard":
    st.title("Prediction History")
    user = st.session_state["user"]
    history_df = get_user_history(user)

    if history_df.empty:
        st.info("No predictions found.")
    else:
        selected_mut = st.text_input("Filter by mutation")
        if selected_mut:
            history_df = history_df[history_df['known_mutations'].str.contains(selected_mut, na=False)]

        st.dataframe(history_df.set_index("id"))

        del_id = st.number_input("Enter ID to delete", min_value=0, step=1, format="%d")
        if st.button("Delete Prediction"):
            delete_prediction(del_id)  
            st.success("Prediction deleted.")
            st.experimental_rerun()

elif page == "New Prediction":
    st.title("HIV-1 NRTI Resistance Predictor")

    demo = st.selectbox("Choose a demo sequence (or None)", ["None", "Demo 1", "Demo 2"])
    sequence = ""
    if demo == "Demo 1":
        # Inject known mutations manually for testing: M184V and F214L
        sequence = WT[:183] + "V" + WT[184:213] + "L" + WT[214:]
    elif demo == "Demo 2":
        sequence = "PISPIETVPVKLKPGMDGPKVKQWPLTEEKIKALVEICTEMEKEGKISKIGPENPYNTPVFAIKKKDSTKWRKLVDDFRELNKRTQDFWEVQLGIPHPAGLKKKKSVTVLDVGDAYFSVPLDKDFRKYTAFTIPSINNETPGIRYQYNVL"
    else:
        input_method = st.radio("Input Method", ["Paste Sequence", "Upload FASTA File"])
        if input_method == "Paste Sequence":
            sequence = st.text_area("Paste Sequence", height=150)
        else:
            fasta_file = st.file_uploader("Upload FASTA", type=["fasta", "fa", "txt"])
            if fasta_file:
                content = fasta_file.read().decode("utf-8")
                sequence = "".join(line.strip() for line in content.splitlines() if not line.startswith(">"))

    if sequence:
        clean_seq = re.sub(r"[^A-Za-z]", "", sequence.upper())
        if len(clean_seq) < 100:
            st.error("Sequence must be at least 100 amino acids.")
            st.stop()

        X = tfidf_vectorizer.transform([kmers(clean_seq)])
        preds = boosters_predict(X)[0]

        # ✅ Mutation detection
        muts = list_mutations(clean_seq)
        known = [m for m in muts if m in KNOWN_NRTI_DRMS]
        rising = [m for m in muts if m not in KNOWN_NRTI_DRMS]

        # ✅ Drug prediction filtering
        selected_drugs = st.multiselect("Select Drugs", drug_labels, default=drug_labels)
        if not selected_drugs:
            st.warning("Select at least one drug.")
            st.stop()

        drug_indices = [drug_labels.index(d) for d in selected_drugs]
        preds_filtered = [preds[i] for i in drug_indices]
        res_filtered = [res_labels[p] for p in preds_filtered]

        # ✅ Display results
        st.subheader("Resistance Predictions")
        res_table = pd.DataFrame({
            "Drug": selected_drugs,
            "Resistance": res_filtered,
            "Alternatives": [
                ", ".join([alt for alt, alt_res in zip(drug_labels, preds)
                           if alt != drug and res_labels[alt_res] == "Susceptible"]) or "None"
                for drug, p in zip(selected_drugs, preds_filtered)
            ]
        }).set_index("Drug")
       
        def color_resistance(val):
            colors = {
            "Susceptible": "green",
            "Potential Low Resistance": "yellowgreen",
            "Low Resistance": "orange",
            "Intermediate Resistance": "orangered",
            "High Resistance": "red"
    }
            color = colors.get(val, "black")
            return f"color: {color}; font-weight: bold"

        st.dataframe(res_table.style.applymap(color_resistance, subset=["Resistance"]), use_container_width=True)


        # ✅ Known Mutations
        st.subheader("Known Mutations")
        if known:
            st.markdown(mutation_notes(known))
        else:
            st.info("No known NRTI mutations detected.")

        # ✅ Rising Mutations
        st.subheader("Rising Mutations")
        if rising:
            st.markdown(f"**Top Rising Mutations:** {', '.join(rising[:4])}")
            if len(rising) > 4:
                with st.expander("View All Rising Mutations"):
                    st.markdown(", ".join(rising))
        else:
            st.info("No rising mutations detected.")

        # ✅ Save prediction
        save_prediction(
            username=st.session_state["user"],
            sequence=clean_seq,
            known=",".join(known),
            rising=",".join(rising),
            preds_dict={drug: res_labels[p] for drug, p in zip(drug_labels, preds)}
        )

        st.subheader("📌 Suggested Clinical Tests")
        st.markdown("""
        **1. CD4 Count**
        - >500: Normal  
        - 200–499: Moderate immune suppression  
        - <200: Advanced HIV

        **2. HIV Viral Load**
        - <50: Suppressed  
        - >1000: Virologic failure → resistance test

        **3. Genotypic Resistance Testing**
        - Confirms mutations
        """)
