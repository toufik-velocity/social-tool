from linkedin_api import Linkedin
from datetime import datetime


def LinkedinScrapper(url, profile_name, existing_metrics=None):

    # required data
    data = {"platform_id": "3",
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

    # Authenticate using any Linkedin account credentials
    api = Linkedin('xohairabbas2000@gmail.com', 'Linkedin123')
    all_posts = api.get_profile_posts(profile_name)

    objects = []
    for post in all_posts:
        if url in post["dashEntityUrn"]:
            objects.append(post)
            break

    data["post_id"] = url
    data["user_provided_id"] = url
    data["url"] = "https://www.linkedin.com/feed/update/urn:li:activity:{}".format(objects[0]["dashEntityUrn"].split(",")[0].split(":")[-1])
    data["content"] = objects[0]['commentary']['text']['text']
    data["user_id"] = objects[0]['actor']['urn'].split(":")[-1]
    data["username"] = objects[0]['actor']['name']['text']
    data["country"] = ""


    content_type = objects[0].get('content', {})

    if 'com.linkedin.voyager.feed.render.ImageComponent' in content_type:
        data["content_type"] = "Picture"
    elif 'com.linkedin.voyager.feed.render.ArticleComponent' in content_type or 'com.linkedin.voyager.feed.render.DocumentComponent' in content_type:
        data["content_type"] = "Document"
    elif 'com.linkedin.voyager.feed.render.LinkedInVideoComponent' in content_type:
        data["content_type"] = "Video"
    else:
        data["content_type"] = "Text"

    if data["platform_id"]=="3" and existing_metrics==None:
        temp_date = datetime.now()
        dt = temp_date.strftime("%Y%m%d")
        data["generated_index"] = str(data["post_id"])+"Linkedin"+dt+data["username"].replace(" ", "")

    # Convert likes to a list and extend it
    likes = [{"value": objects[0]['socialDetail']['totalSocialActivityCounts']['numLikes'], "timestamp": datetime.now()}] if isinstance(
        objects[0]['socialDetail']['totalSocialActivityCounts']['numLikes'], int) else [{"value": like, "timestamp": datetime.now()} for like in objects[0]['socialDetail']['totalSocialActivityCounts']['numLikes']]
    data["likes"].extend(likes)

    # Convert shares to a list and extend it
    shares = [{"value": objects[0]['socialDetail']['totalSocialActivityCounts']['numShares'], "timestamp": datetime.now()}] if isinstance(
        objects[0]['socialDetail']['totalSocialActivityCounts']['numShares'], int) else [{"value": share, "timestamp": datetime.now()} for share in objects[0]['socialDetail']['totalSocialActivityCounts']['numShares']]
    data["shares"].extend(shares)

    comments_num = [{"value": objects[0]['socialDetail']['totalSocialActivityCounts']['numComments'], "timestamp": datetime.now()}] if isinstance(
        objects[0]['socialDetail']['totalSocialActivityCounts']['numComments'], int) else [{"value": comment, "timestamp": datetime.now()} for comment in objects[0]['socialDetail']['totalSocialActivityCounts']['numComments']]
    data["num_comments"].extend(comments_num)

    all_comments = api.get_post_comments(url)
    for i in range(len(all_comments)):
        temp_comment = {}
        temp_comment["comment_id"] = i
        temp_comment["comment_text"] = all_comments[i]["comment"]["values"][0]['value']
        temp_comment["commentator"] = all_comments[i]["commenterForDashConversion"]["title"]["text"]
        temp_comment["replies"] = []
        data["comments"].append(temp_comment)
        if i==len(all_comments)-1:
            timestamp = all_comments[i]["createdTime"]
            date = datetime.fromtimestamp(timestamp/1000)
            data["post_date"] = date.strftime("%d/%m/%Y")

    return data