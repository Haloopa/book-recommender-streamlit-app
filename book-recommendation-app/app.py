# import library
import streamlit as st
import pandas as pd
import os

# setting judul page dan bikin tampilan halamannya wide
st.set_page_config(
    page_title="Book Recommendation System",
    page_icon="📚",
    layout="wide"
)

# memanggil file style.css
def load_css(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, filename)

    if not os.path.exists(css_path):
        st.error(f"CSS file NOT FOUND: {css_path}")
        return

    with open(css_path, "r") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css("style.css")

load_css("style.css")

# load dataset recommendations hasil collaborative filtering
@st.cache_data
def load_data():
    df = pd.read_csv("recommendations.csv")

    # menghapus beberapa line yang tidak memiliki metadata buku 
    df = df[
        df["Book-Title"].notna() &
        df["Book-Author"].notna() &
        df["Image-URL-L"].notna()
    ]

    return df

df = load_data()


# fallback recommendation/rekomendasi cadangan untuk user yang punya rekomendasi > 5
global_popular_books = (
    df.groupby(
        ["isbn", "Book-Title", "Book-Author", "Image-URL-L"],
        as_index=False
    )
    .agg(avg_rating=("predicted_rating", "mean"))
    .sort_values("avg_rating", ascending=False)
)

#fungsi untuk selalu menampilkan 5 rekomendasi buku 
def get_5_recommendations(df, user_id):
    final_books = []
    used_isbn = set()

    # hasil rekomendasi user based
    user_recs = (
        df[df["user_indexed"] == user_id]
        .sort_values("predicted_rating", ascending=False)
    )

    for _, row in user_recs.iterrows():
        if row["isbn"] not in used_isbn:
            final_books.append(row)
            used_isbn.add(row["isbn"])
        if len(final_books) == 5:
            return pd.DataFrame(final_books)

    # fallback recommendation (jika hasil rekomendasi buku user > 5 )
    for _, row in global_popular_books.iterrows():
        if row["isbn"] not in used_isbn:
            final_books.append(row)
            used_isbn.add(row["isbn"])
        if len(final_books) == 5:
            break

    return pd.DataFrame(final_books).head(5)

# header
st.markdown("""
<div class="app-header">
    <h1>Book Recommendation System</h1>
    <p>Rekomendasi Buku Personal Berbasis Collaborative Filtering (User-Based)</p>
</div>
""", unsafe_allow_html=True)

# input id user
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(
        """
        <div style="text-align:center; font-size:18px; font-weight:700; margin-bottom:12px;">
            Pilih ID Pembaca
        </div>
        """,
        unsafe_allow_html=True
    )

    user_ids = sorted(df["user_indexed"].unique())

    selected_user = st.selectbox(
        label="Pilih Pengguna", 
        options=user_ids,
        label_visibility="collapsed" 
    )

    #button search 
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    search = st.button(
        "🔍 Tampilkan Rekomendasi",
        use_container_width=True
    )

# menampilkan hasil rekomendasi
if search:
    st.markdown(
        '<h2 class="center-title">Rekomendasi Buku Untukmu</h2>',
        unsafe_allow_html=True
    )

    user_recs = get_5_recommendations(df, selected_user)
    cols = st.columns(5)

    for idx, (_, row) in enumerate(user_recs.iterrows()):

        # ambil rating
        if "predicted_rating" in row and not pd.isna(row["predicted_rating"]):
            raw_rating = row["predicted_rating"]
        elif "avg_rating" in row and not pd.isna(row["avg_rating"]):
            raw_rating = row["avg_rating"]
        else:
            raw_rating = 0.0

        rating = round((raw_rating / 40) * 5, 2)
        rating_percent = min((rating / 5) * 100, 100)

        #menampilkan metadata buku yang direkomendasikan
        html = f"""
<div class="book-card">
<img src="{row['Image-URL-L']}" class="book-cover">
<div class="book-title">{row['Book-Title']}</div>
<div class="book-author">{row['Book-Author']}</div>

<div class="rating-row">
<span class="rating-value">{rating}</span>
<div class="rating-bar-bg">
<div class="rating-bar-fill" style="width:{rating_percent}%"></div>
</div>
</div>
</div>
"""

        with cols[idx]:
            st.markdown(html, unsafe_allow_html=True)

# footer
st.markdown("---")
st.markdown("""
<div class="app-footer">
    UAS Big Data · Book Recommendation System
</div>
""", unsafe_allow_html=True)
