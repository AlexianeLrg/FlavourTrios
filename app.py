import pandas as pd
import streamlit as st

CSV_PATH = "TestAppliThesaurus.csv"

# ---------- Helpers ----------
def norm_hex(x):
    if pd.isna(x):
        return "#E5E7EB"
    s = str(x).strip()
    if not s:
        return "#E5E7EB"
    if not s.startswith("#"):
        s = "#" + s
    return s if len(s) in (4, 7) else "#E5E7EB"

def ideal_text_color(hex_color):
    h = str(hex_color).lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    except:
        return "#111827"
    lum = (0.299*r + 0.587*g + 0.114*b) / 255
    return "#111827" if lum > 0.62 else "#FFFFFF"

def filter_items(items, q):
    if not q:
        return items
    q = q.lower().strip()
    if not q:
        return items
    return [x for x in items if q in x.lower()]

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    for col in ["A","B","C"]:
        df[col] = df[col].astype(str).str.strip()
    for col in ["Color_A","Color_B","Color_C"]:
        if col not in df.columns:
            df[col] = "#E5E7EB"
        df[col] = df[col].apply(norm_hex)
    return df

@st.cache_data
def build_indexes(df):
    return (
        df.groupby("A")["Color_A"].first().to_dict(),
        df.groupby("A")["B"].unique().to_dict(),
        {(r.A,r.B):r.Color_B for r in df[["A","B","Color_B"]].drop_duplicates().itertuples()},
        df.groupby(["A","B"])["C"].unique().to_dict(),
        {(r.A,r.B,r.C):r.Color_C for r in df[["A","B","C","Color_C"]].drop_duplicates().itertuples()}
    )

# ---------- State ----------
st.session_state.setdefault("step", 1)
st.session_state.setdefault("a", None)
st.session_state.setdefault("b", None)
st.session_state.setdefault("show_copy_box", False)
st.session_state.setdefault("copy_text", "")

def go(step, a=None, b=None):
    st.session_state.step = step
    st.session_state.a = a
    st.session_state.b = b
    st.session_state.show_copy_box = False
    st.session_state.copy_text = ""
    st.rerun()

# ---------- UI ----------
st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container { max-width: 1100px; padding-top: 0.8rem; padding-bottom: 1rem; }

/* Boutons "tuiles" */
div[data-testid="stButton"] > button {
  width: 100%;
  min-height: 54px;
  height: auto;

  border-radius: 16px;
  font-weight: 900;
  font-size: 0.92rem;
  line-height: 1.15;

  border: 1px solid rgba(17,24,39,0.14) !important;
  background: rgba(255,255,255,0.92);
  padding: 8px 10px;

  /* ⚠️ règles IMPORTANTES */
  white-space: normal;        /* autorise retour à la ligne */
  word-break: normal;         /* NE coupe PAS les mots */
  overflow-wrap: normal;      /* pas de césure forcée */
  hyphens: none;              /* jamais de tirets automatiques */

  text-align: center;
}

div[data-testid="stButton"] > button:hover {
  background: rgba(17,24,39,0.04);
}

/* Un peu plus petit sur mobile */
@media (max-width: 520px) {
  div[data-testid="stButton"] > button {
    font-size: 0.84rem;
  }
}

/* Espacement vertical réduit */
div[data-testid="stVerticalBlock"] > div { gap: 0.2rem; }

/* Badges */
.badges { margin: 0.2rem 0 0.55rem 0; display:flex; gap:8px; flex-wrap:wrap; }
.badge {
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 900;
  border: 1px solid rgba(17,24,39,0.10);
  font-size: 0.9rem;
}

/* Badges C */
.cwrap { margin: 0.25rem 0 0.7rem 0; display:flex; gap:10px; flex-wrap:wrap; }
.cbadge {
  display:inline-block;
  padding: 7px 11px;
  border-radius: 999px;
  font-weight: 900;
  border: 1px solid rgba(17,24,39,0.10);
  font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

df = load_data()
a_color, a_to_bs, ab_color, ab_to_cs, abc_color = build_indexes(df)

GRID = 7
step = st.session_state.step
A_sel = st.session_state.a
B_sel = st.session_state.b

st.title("Flavour Trios")

# ---- Badges A/B colorés (selon étape) ----
badges = []
if step >= 2 and A_sel:
    bg = a_color.get(A_sel, "#E5E7EB")
    fg = ideal_text_color(bg)
    badges.append(f"<span class='badge' style='background:{bg};color:{fg}'>{A_sel}</span>")
if step >= 3 and B_sel:
    bg = ab_color.get((A_sel, B_sel), "#E5E7EB")
    fg = ideal_text_color(bg)
    badges.append(f"<span class='badge' style='background:{bg};color:{fg}'>{B_sel}</span>")
if badges:
    st.markdown("<div class='badges'>" + "".join(badges) + "</div>", unsafe_allow_html=True)

# ---------- PAGE 1 ----------
if step == 1:
    st.caption("Choisis ton premier ingrédient")
    q = st.text_input("Rechercher")
    items = filter_items(sorted(a_color.keys()), q)

    for i in range(0, len(items), GRID):
        cols = st.columns(GRID, gap="small")
        for col, A in zip(cols, items[i:i+GRID]):
            with col:
                if st.button(A, key=f"A_{A}", help=A, use_container_width=True):
                    go(2, a=A)

# ---------- PAGE 2 ----------
elif step == 2:
    A = A_sel
    st.caption(f"Choisis ton deuxième ingrédient pour {A}")
    q = st.text_input("Rechercher")

    if st.button("← Retour", use_container_width=True):
        go(1, a=None, b=None)

    items = filter_items(sorted(a_to_bs.get(A, [])), q)

    for i in range(0, len(items), GRID):
        cols = st.columns(GRID, gap="small")
        for col, B in zip(cols, items[i:i+GRID]):
            with col:
                if st.button(B, key=f"B_{A}_{B}", use_container_width=True):
                    go(3, a=A, b=B)

# ---------- PAGE 3 ----------
else:
    A, B = A_sel, B_sel
    st.caption(f"Trios pour {A} + {B}")

    if st.button("← Retour", use_container_width=True):
        go(2, a=A, b=None)

    cs = sorted(ab_to_cs.get((A, B), []))
    if not cs:
        st.info("Aucun trio pour cette paire.")
        st.stop()

    # ---- Badges C en haut (colorés) ----
    c_badges = []
    for C in cs:
        bg = abc_color.get((A, B, C), "#E5E7EB")
        fg = ideal_text_color(bg)
        c_badges.append(f"<span class='cbadge' style='background:{bg};color:{fg}'>{C}</span>")
    st.markdown("<div class='cwrap'>" + "".join(c_badges) + "</div>", unsafe_allow_html=True)

    # Tableau
    table_df = pd.DataFrame([{"Premier": A, "Deuxième": B, "Troisième": c} for c in cs])
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    # Copier
    left, right = st.columns([1, 2])
    with left:
        if st.button("📋 Copier", use_container_width=True):
            st.session_state.copy_text = "\n".join([f"{A}\t{B}\t{c}" for c in cs])
            st.session_state.show_copy_box = True
            st.rerun()
    with right:
        st.caption(" ")

    if st.session_state.show_copy_box:
        st.text_area("Texte à copier", value=st.session_state.copy_text, height=160)
        st.info("Sur iPhone : appui long → Sélectionner tout → Copier.")
