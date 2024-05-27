import stweet as st
from datetime import datetime
import json


def TwitterScrapper(url, existing_metrics=None):

    # required data
    data = {"platform_id": "2",
        "user_id": "",
        "username": "",
        "post_id": "",
        "content": "",
        "content_type": "",
        "post_date": "",
        "url": "",
        "country": "",
        "likes": [],
        "shares": [],
        "num_comments": [],
        "generated_index":"",
        "comments": [],
        "positive_score":"",
        "neutral_score":"",
        "bad_score":"",
        "user_provided_id": "",
        "switch_status": False,
        "likes_growth_rates": [],
        "shares_growth_rates": [],
        "num_comments_growth_rates": [],
        "top_commentators": [],
        }

    if existing_metrics:
        data = existing_metrics
        data["comments"] = []

    id_task = st.TweetsByIdTask(url)
    output_print = st.CollectorRawOutput()
    st.TweetsByIdRunner(tweets_by_id_task=id_task, raw_data_outputs=[output_print]).run()
    objects = []
    counter = 0
    for tweet in output_print.get_raw_list():
        if counter > 101:
            break
        tweet_dict = json.loads(tweet.raw_value)
        objects.append(tweet_dict)
        counter+=1

    data["post_id"] = objects[0]['rest_id']
    data["user_provided_id"] = objects[0]['rest_id']
    data["url"] = "https://twitter.com/{}/status/{}".format(objects[0]['core']['user_results']['result']['legacy']['screen_name'],objects[0]['rest_id'])
    data["content"] = objects[0]['legacy']['full_text']
    date_string = str(objects[0]['legacy']['created_at'])
    date_format = "%a %b %d %H:%M:%S %z %Y"
    data["post_date"] = datetime.strptime(date_string, date_format).strftime("%d/%m/%Y")
    data["user_id"] = objects[0]['legacy']['user_id_str']
    data["username"] = objects[0]['core']['user_results']['result']['legacy']['name']
    data["country"] = objects[0]['core']['user_results']['result']['legacy']['location']

    if len(objects[0]['legacy']['entities'])<5:
        data["content_type"] = "Text"
    elif "photo" in objects[0]['legacy']['entities']['media'][0]['expanded_url']:
        data["content_type"] = "Picture"
    elif "video" in objects[0]['legacy']['entities']['media'][0]['expanded_url']:
        data["content_type"] = "Video"

    if data["platform_id"]=="2" and existing_metrics==None:
        temp_date = datetime.now()
        dt = temp_date.strftime("%Y%m%d")
        data["generated_index"] = str(data["post_id"])+"Twitter"+dt+data["username"].replace(" ", "")

    # Convert likes to a list and extend it
    likes = [{"value": objects[0]['legacy']['favorite_count'], "timestamp": datetime.now()}] if isinstance(
        objects[0]['legacy']['favorite_count'], int) else [{"value": like, "timestamp": datetime.now()} for like in objects[0]['legacy']['favorite_count']]
    data["likes"].extend(likes)

    # Convert shares to a list and extend it
    shares = [{"value": objects[0]['legacy']['quote_count']+objects[0]['legacy']['retweet_count'], "timestamp": datetime.now()}] if isinstance(
        objects[0]['legacy']['quote_count']+objects[0]['legacy']['retweet_count'], int) else [{"value": share, "timestamp": datetime.now()} for share in objects[0]['legacy']['quote_count']+objects[0]['legacy']['retweet_count']]
    data["shares"].extend(shares)

    comments_num = [{"value": objects[0]['legacy']['reply_count'], "timestamp": datetime.now()}] if isinstance(
        objects[0]['legacy']['reply_count'], int) else [{"value": comment, "timestamp": datetime.now()} for comment in objects[0]['legacy']['reply_count']]
    data["num_comments"].extend(comments_num)

    
    for i in range(1,len(objects)):
        temp_comment = {}
        temp_comment["comment_id"] = i
        temp_comment["comment_text"] = objects[i]['legacy']['full_text']
        temp_comment["commentator"] = objects[i]['core']['user_results']['result']['legacy']['name']
        temp_comment["replies"] = []
        data["comments"].append(temp_comment)

    return data