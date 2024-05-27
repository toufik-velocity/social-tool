from textblob import TextBlob
import re

def pre_process(text):
    # Remove links
    text = re.sub('http://\S+|https://\S+', '', text)
    text = re.sub('http[s]?://\S+', '', text)
    text = re.sub(r"http\S+", "", text)

    # Convert HTML references
    text = re.sub('&amp', 'and', text)
    text = re.sub('&lt', '<', text)
    text = re.sub('&gt', '>', text)
    text = text.replace('\xa0', ' ')

    # Remove new line characters
    text = re.sub('[\r\n]+', ' ', text)
    
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)

    # Remove multiple space characters
    text = re.sub('\s+',' ', text)
    
    # Convert to lowercase
    text = text.lower()
    return text

def get_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "positive"
    elif sentiment == 0:
        return "neutral"
    else:
        return "negative"

def analyze_sentiments(comments):
    preprocessed_comments = [pre_process(comment) for comment in comments]
    # Perform sentiment analysis on each comment
    sentiments = []
    for comment in preprocessed_comments:
        sentiment = get_sentiment(comment)
        sentiments.append(sentiment)

    results = {}
    total_comments = len(sentiments)
    good_comments = sentiments.count("positive")
    neutral_comments = sentiments.count("neutral")
    bad_comments = sentiments.count("negative")

    if total_comments == 0:
        good_percentage = 0
        neutral_percentage = 0
        bad_percentage = 0

    else:
        good_percentage = (good_comments / total_comments) * 100
        neutral_percentage = (neutral_comments / total_comments) * 100
        bad_percentage = (bad_comments / total_comments) * 100

    results["good"] = round(good_percentage,2)
    results["neutral"] = round(neutral_percentage,2)
    results["bad"] = round(bad_percentage,2)
    return results