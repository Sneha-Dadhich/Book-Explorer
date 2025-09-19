import requests
from bs4 import BeautifulSoup

def scrape_books():
    """
    Scrapes book data from http://books.toscrape.com/ and yields dictionaries for each book.
    """
    base_url = 'http://books.toscrape.com/'
    url = base_url
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an exception for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all book articles on the current page
            books = soup.find_all('article', class_='product_pod')

            for book in books:
                # Extract Title
                title = book.h3.a['title']

                # Extract Price
                price_text = book.find('p', class_='price_color').text
                price = float(price_text.strip('£'))

                # Extract Stock Availability
                stock_availability = book.find('p', class_='instock').text.strip()

                # Extract Rating
                rating_class = book.find('p', class_='star-rating')['class'][-1].lower()
                rating_map = {
                    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5
                }
                rating = rating_map.get(rating_class)

                # Extract Book Detail Page URL
                book_detail_url = base_url + book.h3.a['href']

                # Extract Thumbnail Image URL
                thumbnail_url = base_url + book.find('div', class_='image_container').a.img['src']

                yield {
                    'title': title,
                    'price': price,
                    'stock_availability': stock_availability,
                    'rating': rating,
                    'book_detail_page_url': book_detail_url,
                    'thumbnail_image_url': thumbnail_url,
                }

            # Find the link to the next page
            next_button = soup.find('li', class_='next')
            if next_button:
                url = base_url + next_button.a['href']
            else:
                break  # Exit the loop if there's no next page
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            break

if __name__ == '__main__':
    for book_data in scrape_books():
        print(book_data)