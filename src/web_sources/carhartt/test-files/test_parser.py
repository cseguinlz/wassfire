import asyncio
import re
from datetime import datetime

from bs4 import BeautifulSoup

single_product_html = """ <div
      class="small-6 large-4 columns product-cell productcell-padding display-subcat-3"
    >
      <div class="product-cell-image has-color-swatches">
        <div>
          <div>
            <a
              id="catalogEntry_imgOUT_102987"
              href="https://www.carhartt.com/es/es-es/productos/Rugged-Flex-Relaxed-Fit-Canvas-Bib-Overall-Out-102987-5"
              data-quickview-url="http://www.carhartt.com/ProductQuickView?country=ES&urlRequestType=Base&catalogId=3074457345616677219&categoryId=3074457345616696173&productId=3074457345616860672&urlLangId=-5&langId=-5&storeId=715838034&productPrefix=productos"
              title="RUGGED FLEX™ RELAXED FIT CANVAS BIB OVERALL"
              data-product-orig-id="out_102987"
              data-locale="es_ES"
              data-product-id="OUT_102987"
              data-selected-color=""
              class="catclick"
            >
              <img
                class="front"
                alt="Carhartt RUGGED FLEX™ RELAXED FIT CANVAS BIB OVERALL - front"
                data-image-name="EU_102987_211"
                data-interchange="[https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$400L2$, (default)],
									  [https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$search-product-cell-mobile$, (small)], 
							   		  [https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$search-product-cell-mobile-retina$, (smallretina)],
			                          [https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$search-product-cell-tablet$, (medium)],
			                          [https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$search-product-cell-tablet-retina$, (mediumretina)],
			                          [https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$400L2$, (large)],
			                          [https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$search-product-cell-desktop-retina$, (largeretina)]"
                src="https://imgcdn.carhartt.com/is/image/Carhartt/EU_102987_211?$400L2$"
              />
            </a>
            <span class="quickview-button button t13"
              >Vista rápida <i class="icon-plus"></i
            ></span>
            <div data-reveal="" class="quickview-modal reveal-modal"></div>
          </div>
        </div>
      </div>
      <div class="color-swatches-overlay">
        <div class="color-swatches product-cell-swatches">
          <ul style="width: auto">
            <li>
              <a
                title="DARK KHAKI"
                href="#"
                style="
                  background-image: url('https://imgcdn.carhartt.com/is/image/Carhartt//DKH_SW?$product-cell-color-swatch$');
                "
                data-main-image="EU_102987_DKH"
                data-alt-image=""
                class="attr"
                ><i class="icon-x"></i>
              </a>
            </li>

            <li>
              <a
                title="CARHARTT® BROWN"
                href="#"
                style="
                  background-image: url('https://imgcdn.carhartt.com/is/image/Carhartt//211_SW?$product-cell-color-swatch$');
                "
                data-main-image="EU_102987_211"
                data-alt-image=""
                class="attr selected"
                ><i class="icon-x"></i>
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div class="product-description">
        <a
          href="https://www.carhartt.com/es/es-es/productos/Rugged-Flex-Relaxed-Fit-Canvas-Bib-Overall-Out-102987-5"
          data-product-id="OUT-102987"
        >
          <div>
            <h5 class="t14">RUGGED FLEX™ RELAXED FIT CANVAS BIB OVERALL</h5>
            <p
              class="price t14 not-bold"
              id="product_price_3074457345616918171"
            >
              <span
                data-formatted-min-price="&euro;97.99"
                data-formatted-max-price="&euro;97.99"
                data-min-price="97.99"
                data-max-price="97.99"
                data-price-string="97.99"
                class="discounted"
              >
                97,99 €
              </span>

              <del> 119,95 € </del>
            </p>
          </div>
        </a>
      </div>
    </div>
    """


async def test_parse_page():
    country_code = "es-ES"

    products = await parse_page(single_product_html, country_code)
    for product in products:
        print(product)


BRAND = "Carhartt"
SOURCE_ID: int = 2  # Example ID, should be unique


async def parse_page(html_content: str, country_code: str):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []

    for product_cell in soup.select(".product-cell"):
        product_link_tag = product_cell.find(
            "a", id=re.compile("^catalogEntry_imgOUT_")
        )
        if product_link_tag:
            product_link = product_link_tag["href"]
        name = product_cell.select_one(".product-description h5").text.strip()
        image_url = product_cell.select_one(".product-cell-image img.front")["src"]
        price_data = product_cell.select_one(".price span")
        original_price = product_cell.select_one("del").text.strip()
        sale_price = price_data.text.strip().split("\n")[0]

        # Parsing price to float
        original_price_float = parse_float(
            re.sub("[^0-9,]", "", original_price).replace(",", ".")
        )
        sale_price_float = parse_float(
            re.sub("[^0-9,]", "", sale_price).replace(",", ".")
        )
        discount_percentage = (
            (1 - (sale_price_float / original_price_float))
            if original_price_float
            else 0
        )

        # Capturing color variations
        color_variations = [
            li.find("a")["title"]
            for li in product_cell.select(
                ".color-swatches-overlay .product-cell-swatches li"
            )
        ]

        short_url = "wass.promo/someshit"
        products.append(
            {
                "source_id": SOURCE_ID,
                "name": name,
                "country_lang": country_code,
                "brand": BRAND,
                "section": "",  # Section is not defined in the provided HTML, may need to adapt based on actual use
                "category": "",  # Similarly, category is not directly available
                "type": "",  # Type information is also not available in the HTML snippet
                "color": ", ".join(color_variations),
                "discount_percentage": discount_percentage,
                "original_price": original_price_float,
                "sale_price": sale_price_float,
                "product_link": product_link,
                "short_url": short_url,
                "image_url": image_url,
                "second_image_url": "",  # Second image URL extraction logic needs adaptation if available
                "source_published_at": datetime.now(),  # Placeholder for actual published date if available
            }
        )

    return products


def parse_float(price_str, default=None):
    try:
        return float(price_str)
    except ValueError:
        return default


""" Test: run 
`python src/web_sources/utils.py`
or as a module:
`python -m src.web_sources.utils`
 """


def main():
    asyncio.run(test_parse_page())


if __name__ == "__main__":
    main()
