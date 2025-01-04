import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

# Base configuration
BASE_URL = "https://github.com"
TOPICS_URL = "https://github.com/topics"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to handle requests with retries and exponential backoff
def fetch_with_retries(url, retries=5):
    for attempt in range(retries):
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Too many requests. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"Unexpected status code {response.status_code}. Retrying...")
            time.sleep(2)
    print("Max retries reached. Exiting...")
    return None

# Function to extract links to topics
def get_links(my_soup):
    all_topics_links = my_soup.find_all('a', class_="no-underline flex-1 d-flex flex-column")
    links = [BASE_URL + link.get('href') for link in all_topics_links]
    return links

# Function to fetch repository details for a specific topic
def fetch_data_of_topics(topic_url):
    response = fetch_with_retries(topic_url)
    if not response:
        return [], [], []

    soup = BeautifulSoup(response.content, 'html.parser')
    blocks = soup.find_all('h3', class_="f3 color-fg-muted text-normal lh-condensed")

    user_names = []
    repo_links = []
    ratings = []

    # Extract repository owner and repo links
    for block in blocks:
        links = block.find_all('a')
        if len(links) >= 2:
            user_names.append(links[0].text.strip())
            repo_links.append(BASE_URL + links[1].get('href'))

    # Extract repository star ratings
    star_elements = soup.find_all('span', class_="Counter js-social-count")
    for star in star_elements:
        stars = star.text.strip().replace(',', '')
        if 'k' in stars:
            stars = float(stars.replace('k', '')) * 1000
        ratings.append(float(stars))
    
    return user_names, repo_links, ratings

# Main function to fetch topics and details
def start_from_here():
    # Fetch the main topics page
    response = fetch_with_retries(TOPICS_URL)
    if not response:
        print("Failed to fetch topics.")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract topic titles, descriptions, and links
    topics = [topic.text.strip() for topic in soup.find_all('p', class_="f3 lh-condensed mb-0 mt-1 Link--primary")]
    descriptions = [desc.text.strip() for desc in soup.find_all('p', class_="f5 color-fg-muted mb-0 mt-1")]
    links = get_links(soup)

    if not topics:
        print("No topics found. Check your selectors.")
        return

    # Save topics data to a DataFrame
    data = {
        'title': topics,
        'description': descriptions,
        'links': links
    }
    topics_df = pd.DataFrame(data)

    owners_dictionary = []
    # Fetch details for each topic
    for topic_link in links[:1]:  # Limit to 1 topic for testing
        print(f"Fetching data for topic: {topic_link}")
        owners, repo_links, ratings = fetch_data_of_topics(topic_link)

        # Append each row of data to the owners_dictionary
        for owner, repo_link, rating in zip(owners, repo_links, ratings):
            topic_data = {
                'username': owner,
                'repo_links': repo_link,
                'rating': rating
            }
            owners_dictionary.append(topic_data)

    # Create a DataFrame from the list of dictionaries
    repo_details_df = pd.DataFrame(owners_dictionary)

    # Save both DataFrames to the same Excel file in different sheets
    with pd.ExcelWriter('topics_and_repos.xlsx', engine='openpyxl') as writer:
        topics_df.to_excel(writer, sheet_name='Topics', index=False)
        repo_details_df.to_excel(writer, sheet_name='Repo Details', index=False)

    print("Excel file with multiple sheets created successfully!")

# Run the script
if __name__ == "__main__":
    start_from_here()
