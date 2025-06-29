from bs4 import BeautifulSoup
import requests
import streamlit as st

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
BASE_URL = 'https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121075132011&dc&fs=true&brr=1&crid=298MAW5KNLF6K&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{page}'

try:

    data = requests.get("https://api.scraperapi.com", params={
        'api_key': st.secrets["SCRAPER_API_KEY"],
        'url': BASE_URL.format(page=1),
        'keep_headers': 'true',
    }, headers=headers, timeout=20)

    data.raise_for_status()
    soup = BeautifulSoup(data.text, 'html.parser')
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()



st.markdown("""
    <style>
        /* Whole Page Background */
        [data-testid="stAppViewContainer"] {
            background-color: #E0E0E0;
        }
    </style>    """,unsafe_allow_html=True)

try:
    last_page = int(soup.find_all("span", class_="s-pagination-item")[-1].text.strip())
except:
    last_page = 1

# st.write(pagination)

page_url = "https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A1210776011%2Cp_n_feature_thirty-two_browse-bin%3A121075132011&dc&fs=true&page={pg_no}&brr=1&crid=298MAW5KNLF6K&qid=1751166017&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_{pg_no}"
def show_data(products):
    cols = st.columns(5)

    for key, product in enumerate(products):
        img = product.find("img", class_="s-image")
        h2 = product.find("h2", class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
        # green
        price_tag = product.find("span", class_="a-offscreen")
        price = price_tag.text.strip() if price_tag else "N/A"

        # yellow
        no_bought = product.find("span",class_="a-size-base a-color-secondary")

        ship = product.find("span",class_="a-size-small a-color-base")



        if not img or not h2: # Removed price, no_bought, ship from this check as they might not always be present for every product and should not block display of other details
            continue

        span = h2.find("span")
        if not span:
            continue

        img_url = img.get("src")
        product_detail = span.text.strip()

        col = cols[key % 5]
        with col:
            st.markdown(f"""
    <div style="
        border: 1px solid #ccc;
        border-radius: 1px;
        padding: 5px; /* Increased padding for better spacing */
        background-color: #f5f5f5;
        height: 350px; /* Increased height to accommodate more lines of title */
        display: flex; /* Use flexbox for better vertical alignment */
        flex-direction: column; /* Stack items vertically */
        justify-content: space-between; /* Distribute space between items */
        text-align: center;
        overflow: hidden;
        margin:auto;
    ">
        <div style="
            height: 140px; /* Fixed height for image container */
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center; /* Center image vertically */
            margin-bottom: 5px;
        ">
            <img src="{img_url}" style="max-height: 100%; max-width: 100%; object-fit: contain;" />
        </div>
        <div style="
            flex-grow: 1; /* Allow this div to take up available space */
            width: 100%;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 4; /* Display up to 4 lines of text */
            -webkit-box-orient: vertical;
            text-overflow: ellipsis; /* Add ellipsis for overflowed text */
            margin-bottom: 5px; /* Space between title and price */
        ">
            <p style="margin: 0; font-size: 13px; font-weight: bold; color: #333;">
                {product_detail}
            </p>
        </div>
        <div style="
            width: 100%;
            text-align: center;
        ">
           <h2 style="margin: 0; font-size: 14px; font-weight: bold; color: green;">
                {price}
            </h2>
             <p style="margin: 0; font-size: 11px; color: #555;">
                {no_bought.text.strip() if no_bought else "No sales data"}
            </p>
            <p style="margin: 0; font-size: 11px; color: #555;">
                {ship.text.strip() if ship else "Shipping info N/A"}
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)


for page_num in range(1, last_page + 1):
    if(page_num==1):
        new_url = BASE_URL.format(page=page_num)
    else :

        new_url = page_url.format(pg_no=page_num)
        st.write(f"Fetching page {page_num}...")

    try:
        data = requests.get(
            "https://api.scraperapi.com",
            params={
                'api_key': st.secrets["SCRAPER_API_KEY"],
                'url': new_url,
                'keep_headers': 'true',
            },
            headers=headers,
            timeout=20
        )
        data.raise_for_status()
        soup = BeautifulSoup(data.text, 'html.parser')

        products = soup.find_all(
            "div", class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20"
        )
        show_data(products)

    except Exception as e:
        st.warning(f"Failed to fetch page {page_num}: {e}")
        continue