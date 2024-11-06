import nltk
from nltk.corpus import wordnet, stopwords

# Ensure you download the necessary resources
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
def get_synonyms(word):
    synonyms = []

    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())

    return set(synonyms)

def process_query(query):
    stop_words = set(stopwords.words('english'))

    # Ensure punkt is available for tokenization
    words = nltk.word_tokenize(query)

    filtered_words = [word.lower() for word in words if word.lower() not in stop_words]
    # print(filtered_words)
    final_list = []

    for word in filtered_words:
        final_list.append(word)

        synonyms = get_synonyms(word)
        itrator =synonyms.copy()
        for syn in itrator:
            if syn == word:
                synonyms.remove(syn)
        final_list.extend(list(synonyms)[:5])
    print(final_list)
    return final_list


async def clean_data(data):
    """
    Cleans the data by removing duplicates if an item's 'content' appears more than once.

    Parameters:
    data (list): A list of dictionaries, each containing 'content', 'chapter', and 'number'.

    Returns:
    list: A list of unique dictionaries based on 'content'.
    """
    seen = set()
    unique_data = []

    for item in data:
        item_content = item['content'].lower()
        if item_content not in seen:
            seen.add(item_content)
            unique_data.append(item)

    print(seen)
    return unique_data


