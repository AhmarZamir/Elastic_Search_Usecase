from bs4 import BeautifulSoup
import requests
import streamlit as st
import sqlite3
import time

# Connect to or create the database
conn = sqlite3.connect('amazon_products.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    price TEXT,
    bought TEXT,
    shipping TEXT,
    img_url TEXT,
    genre TEXT,
    page INTEGER
)
""")

conn.commit()

def save_product_to_db(title, price, bought, shipping, img_url, genre, page):
    cursor.execute("""
        INSERT OR IGNORE INTO products (title, price, bought, shipping, img_url, genre, page)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, price, bought, shipping, img_url, genre, page))
    conn.commit()

def get_products_from_db(genre, page):
    cursor.execute("""
        SELECT title, price, bought, shipping, img_url FROM products
        WHERE genre = ? AND page = ?
    """, (genre, page))
    return cursor.fetchall()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# Initialize session state variables
if "rerun_flag" not in st.session_state:
    st.session_state.rerun_flag = False

if "genre" not in st.session_state:
    st.session_state.genre = "Men"    
    st.session_state.current_page = 1

if "prev_genre" not in st.session_state:
    st.session_state.prev_genre = "Men"

if "auto_fetch" not in st.session_state:
    st.session_state.auto_fetch = False

if "current_fetch_genre" not in st.session_state:
    st.session_state.current_fetch_genre = "Men"

if "current_fetch_page" not in st.session_state:
    st.session_state.current_fetch_page = 1

st.markdown("""
    <style>
    label[data-testid="stSelectboxLabel"] {
        color: black !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)    

genre_list = [  "Boys"]
selected_genre = st.selectbox("Product Genre", genre_list)

if selected_genre != st.session_state.prev_genre:
    st.session_state.current_page = 1
    st.session_state.genre = selected_genre
    st.session_state.prev_genre = selected_genre
    st.session_state.rerun_flag = not st.session_state.rerun_flag    

# Define URLs for each genre
genre_urls = {
    "Men": 'https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121075132011&dc&fs=true&brr=1&crid=298MAW5KNLF6K&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{page}',
    "Boys": "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121075136011&dc&fs=true&brr=1&crid=298MAW5KNLF6K&qid=1751232193&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{page}",
    "Babies": "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121833111011&dc&fs=true&brr=1&crid=298MAW5KNLF6K&qid=1751241903&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{page}",
    "Girls": "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121075133011&dc&fs=true&brr=1&crid=298MAW5KNLF6K&qid=1751242817&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{page}"
}

genre_page_urls = {
    "Men": "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A1210776011%2Cp_n_feature_thirty-two_browse-bin%3A121075132011&dc&fs=true&page={pg_no}&brr=1&crid=298MAW5KNLF6K&qid=1751166017&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{pg_no}",
    "Boys": "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121075136011&dc&fs=true&page={pg_no}&brr=1&crid=298MAW5KNLF6K&qid=1751232152&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{pg_no}",
    "Babies": "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121833111011&dc&fs=true&page={pg_no}&brr=1&crid=298MAW5KNLF6K&qid=1751241929&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{pg_no}",
    "Girls": "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121075133011&dc&fs=true&page={pg_no}&brr=1&crid=298MAW5KNLF6K&qid=1751242832&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{pg_no}"
}

BASE_URL = genre_urls.get(st.session_state.genre, genre_urls["Men"])

try:
    data = requests.get("https://api.scraperapi.com", params={
        'api_key': st.secrets["SCRAPER_API_KEY"],
        'url': BASE_URL.format(page=1),
        'keep_headers': 'true',
        'country_code': 'pk'
    }, headers=headers, timeout=50)
    data.raise_for_status()
    soup = BeautifulSoup(data.text, 'html.parser')
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

st.markdown("""
    <style>
        /* Whole Page Background */
        [data-testid="stAppViewContainer"] {
            background-color: #E0E0E0;
        }
    </style>""", unsafe_allow_html=True)

try:
    last_page = int(soup.find_all("span", class_="s-pagination-item")[-1].text.strip())
except:
    last_page = 1

def go_next():
    if st.session_state.current_page < last_page:
        st.session_state.current_page += 1

def go_prev():
    if st.session_state.current_page > 1:
        st.session_state.current_page -= 1

def fetch_products(url):
    try:
        data = requests.get(
            "https://api.scraperapi.com",
            params={
                'api_key': st.secrets["SCRAPER_API_KEY"],
                'url': url,
                'keep_headers': 'true',
                'country_code': 'pk'
            },
            headers=headers,
            timeout=50
        )
        data.raise_for_status()
        soup = BeautifulSoup(data.text, 'html.parser')
        return soup.find_all("div", class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20")
    except Exception as e:
        st.error(f"Failed to fetch page: {e}")
        return None

def fetch_and_save_products(genre, page):
    url = genre_urls[genre].format(page=1) if page == 1 else genre_page_urls[genre].format(pg_no=page)
    products = fetch_products(url)
    
    if products:
        for product in products:
            img = product.find("img", class_="s-image")
            h2 = product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
            price_tag = product.find("span", class_="a-offscreen")
            price = price_tag.text.strip() if price_tag else "N/A"
            no_bought = product.find("span", class_="a-size-base a-color-secondary")
            ship = product.find("span", class_="a-size-small a-color-base")

            if not img or not h2:
                continue

            span = h2.find("span")
            if not span:
                continue

            img_url = img.get("src")
            product_detail = span.text.strip()
            save_product_to_db(
                product_detail,
                price,
                no_bought.text.strip() if no_bought else "No sales data",
                ship.text.strip() if ship else "Shipping info N/A",
                img_url,
                genre,
                page
            )

def auto_fetch_all_genres():
    for genre in genre_list:
        st.session_state.current_fetch_genre = st.session_state.genre
        st.session_state.current_fetch_page = 190
        
        # Get last page for this genre

        try:
            url = genre_urls[genre].format(page=1)
            data = requests.get("https://api.scraperapi.com", params={
                'api_key': st.secrets["SCRAPER_API_KEY"],
                'url': url,
                'keep_headers': 'true',
                'country_code': 'pk'
            }, headers=headers, timeout=50)
            data.raise_for_status()
            soup = BeautifulSoup(data.text, 'html.parser')
            try:
                last_pg = int(soup.find_all("span", class_="s-pagination-item")[-1].text.strip())
            except:
                last_pg = 1
        except:
            last_pg = 1
        
        for page in range(190, last_pg + 1):
            st.session_state.current_fetch_page = page
            fetch_and_save_products(genre, page)
            time.sleep(2)  # Add delay to avoid rate limiting
            
            # Update progress
            progress = (genre_list.index(genre) / len(genre_list)) + (page / last_pg) / len(genre_list)
            progress_bar.progress(progress)
            
            # Check if we should stop
            if not st.session_state.auto_fetch:
                return

# Sidebar controls
with st.sidebar:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.button("Prev", on_click=go_prev, disabled=st.session_state.current_page == 1)
    with col3:
        st.button("Next", on_click=go_next, disabled=st.session_state.current_page == last_page)
    
    page_input = st.number_input(
        "Go to page:",
        min_value=1,
        max_value=last_page,
        value=st.session_state.current_page,
        step=1,
        key="jump_page"
    )
    if page_input != st.session_state.current_page:
        st.session_state.current_page = page_input
    
    # Auto-fetch controls
    st.markdown("---")
    if st.button("Start Auto-Fetch All Genres"):
        st.session_state.auto_fetch = True
        progress_bar = st.progress(0)
    
    if st.button("Stop Auto-Fetch"):
        st.session_state.auto_fetch = False
    
    if st.session_state.auto_fetch:
        st.write(f"Fetching: {st.session_state.current_fetch_genre} - Page {st.session_state.current_fetch_page}")
        auto_fetch_all_genres()
        st.session_state.auto_fetch = False
        st.success("Auto-fetch completed!")

# Main content
pg_no = st.session_state.current_page
current_genre = st.session_state.genre
new_url = genre_urls[current_genre].format(page=pg_no) if pg_no == 1 else genre_page_urls[current_genre].format(pg_no=pg_no)

with col2:      
    st.write(f"Page {st.session_state.current_page}")  

with st.spinner(f"Loading Page {pg_no}..."):         
    try:
        data = requests.get(
            "https://api.scraperapi.com",
            params={
                'api_key': st.secrets["SCRAPER_API_KEY"],
                'url': new_url,
                'keep_headers': 'true',
                'country_code': 'pk'
            },
            headers=headers,
            timeout=50
        )
        data.raise_for_status()
        soup = BeautifulSoup(data.text, 'html.parser')

        products = soup.find_all(
            "div", class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"
        )
        st.markdown(f"<h2 style='color:#084954;'> Showing Page {pg_no}</h2>", unsafe_allow_html=True)

        cols = st.columns(5)     
        prod_from_db = get_products_from_db(st.session_state.genre, st.session_state.current_page)
            
        if not prod_from_db:
            # Save products to DB if not already there
            for product in products:
                img = product.find("img", class_="s-image")
                h2 = product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
                price_tag = product.find("span", class_="a-offscreen")
                price = price_tag.text.strip() if price_tag else "N/A"
                no_bought = product.find("span", class_="a-size-base a-color-secondary")
                ship = product.find("span", class_="a-size-small a-color-base")

                if not img or not h2:
                    continue

                span = h2.find("span")
                if not span:
                    continue

                img_url = img.get("src")
                product_detail = span.text.strip()
                save_product_to_db(
                    product_detail,
                    price,
                    no_bought.text.strip() if no_bought else "No sales data",
                    ship.text.strip() if ship else "Shipping info N/A",
                    img_url,
                    st.session_state.genre,
                    st.session_state.current_page
                )
            
            # Get from DB again after saving
            prod_from_db = get_products_from_db(st.session_state.genre, st.session_state.current_page)

        if prod_from_db:
            for index, p in enumerate(prod_from_db):
                col = cols[index % 5]
                with col:
                    st.markdown(f"""
<div style="
    border: 1px solid #ccc;
    border-radius: 1px;
    padding: 5px;
    background-color: #f5f5f5;
    height: 350px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    overflow: hidden;
    margin:auto;
">
    <div style="
        height: 140px;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 5px;
    ">
        <img src="{p[4]}" style="max-height: 100%; max-width: 100%; object-fit: contain;" />
    </div>
    <div style="
        flex-grow: 1;
        width: 100%;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
        text-overflow: ellipsis;
        margin-bottom: 5px;
    ">
        <p style="margin: 0; font-size: 13px; font-weight: bold; color: #333;">
            {p[0]}
        </p>
    </div>
    <div style="
        width: 100%;
        text-align: center;
    ">
       <h2 style="margin: 0; font-size: 14px; font-weight: bold; color: green;">
            {p[1]}
        </h2>
         <p style="margin: 0; font-size: 11px; color: #007185;">
            {p[2]}
        </p>
        <p style="margin: 0; font-size: 11px; color: #b12704;">
            {p[3]}
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Failed to fetch page {pg_no}: {e}")

import pandas as pd

if st.checkbox("View Database as Table"):
    conn = sqlite3.connect('amazon_products.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    st.dataframe(df)