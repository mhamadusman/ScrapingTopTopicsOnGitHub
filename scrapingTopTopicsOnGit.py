import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://github.com"
url = "https://github.com/topics"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract all topics
all_topics = soup.find_all('p', class_="f3 lh-condensed mb-0 mt-1 Link--primary")

topics = []
for topic in all_topics:
    topics.append(topic.text.strip())  # Strip to remove extra spaces/newlines

# Extract all topic descriptions
all_topics_description = soup.find_all('p', class_="f5 color-fg-muted mb-0 mt-1")

description = []
for des in all_topics_description:
    description.append(des.text.strip())  # Strip to remove extra spaces/newlines

# Extract all topic links
all_topics_links = soup.find_all('a', class_="no-underline flex-1 d-flex flex-column")

links = []
for link in all_topics_links:
    links.append(base_url + link.get('href'))

# Create a list of dictionaries to structure the data for each topic
my_dictionary = {
    'title' : topics,
    'description'  : description,
    'links'  :links
}

# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(my_dictionary)

# Write to CSV
df.to_csv('output.csv', index=False)

print("CSV file has been created successfully!")
