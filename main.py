from bs4 import  BeautifulSoup
import requests
import streamlit as st 


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

try:
    data = requests.get("http://api.scraperapi.com", params={
        'api_key': st.secrets["SCRAPER_API_KEY"],
        'url': 'https://www.amazon.com/s?i=fashion-mens-intl-ship&rh=n%3A16225019011%2Cp_n_feature_thirty-two_browse-bin%3A121075132011&dc&fs=true&page=2&brr=1&crid=298MAW5KNLF6K&qid=1751026708&rd=1&rnid=121075130011&sprefix=%2Cfashion-mens-intl-ship%2C472&xpid=UAvkucKu_X1eB&ref=sr_pg_1'
    }, headers=headers,timeout=100000)

    data.raise_for_status()
    soup = BeautifulSoup(data.text, 'html.parser')
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()


# to get a multiple products
products = soup.find_all("div",class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20")

# in each product there is first span in which there is a image tag
cols = st.columns(5)

for key,product in enumerate(products):
    # products_span = product.find("span",class_="s-product-image")
    # if not products_span:
    #     continue

    img = product.find("img", class_="s-image")

    h2 = product.find("h2",class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
    product_detail = h2.find("span").text.strip()



    if not img:
        continue
    img_url = img.get("src")

    col = cols[key%5]


    if (img_url):
        with col:
            
          st.markdown(f"""
                <div style="
                    border: 1px solid #000;
                    border-radius: 10px;
                    padding: 30px;
                    background-color: grey;
                    height: 200px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    align-items: center;
                    overflow: hidden;
                    text-align: center;
                ">
                    <img src="{img_url}" style="max-height: 150px; object-fit: contain; width: 100%;" />
                    <p style="margin-top: 10px; font-size: 13px; font-weight: bold; color: #333;">
                        {product_detail[:100]}{'...' if len(product_detail) > 100 else ''}
                    </p>
                </div>
            """, unsafe_allow_html=True)