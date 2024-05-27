import facebook_scraper as fs
import time
import requests.exceptions
from datetime import datetime
from collections import Counter


def FacebookScrapper(url, existing_metrics=None):
    POST_ID = url
    # number of comments to download -- set this to True to download all comments
    MAX_COMMENTS = 100
    # maximum number of attempts
    MAX_ATTEMPTS = 5
    # delay between attempts in seconds
    DELAY_SECONDS = 3
    # attempt counter
    attempt = 0

    # required data
    data = {"platform_id": "1",
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

    while True:
        try:
            # attempt to get the posts
            gen = fs.get_posts(
                post_urls=[POST_ID],
                options={"comments": MAX_COMMENTS, "progress": True}
            )

            # take 1st element of the generator which is the post we requested
            post = next(gen)
            data["post_id"] = str(post["post_id"])
            data["user_provided_id"] = post["original_request_url"]
            data["url"] = post["post_url"]
            data["content"] = post["post_text"]
            data["post_date"] = post["time"].strftime('%d/%m/%Y')
            data["user_id"] = str(post["user_id"])
            data["username"] = post["username"]

            if post["post_text"] and post["image"] is None and post["video"] is None:
                data["content_type"] = "Text"
            elif post["image"] and post["video"] is None:
                data["content_type"] = "Picture"
            elif post["image"] is None and post["video"]:
                data["content_type"] = "Video"

            if data["platform_id"]=="1" and existing_metrics==None:
                temp_date = datetime.now()
                dt = temp_date.strftime("%Y%m%d")
                data["generated_index"] = str(post["post_id"])+"FB"+dt+post["username"].replace(" ", "")

            # Convert likes to a list and extend it
            likes = [{"value": post["likes"], "timestamp": datetime.now()}] if isinstance(
                post["likes"], int) else [{"value": like, "timestamp": datetime.now()} for like in post["likes"]]
            data["likes"].extend(likes)

            # Convert shares to a list and extend it
            shares = [{"value": post["shares"], "timestamp": datetime.now()}] if isinstance(
                post["shares"], int) else [{"value": share, "timestamp": datetime.now()} for share in post["shares"]]
            data["shares"].extend(shares)

            comments_num = [{"value": post["comments"], "timestamp": datetime.now()}] if isinstance(
                post["comments"], int) else [{"value": comment, "timestamp": datetime.now()} for comment in post["comments"]]
            data["num_comments"].extend(comments_num)

            # extract the comments part
            comments = post['comments_full']

            for index, comment in enumerate(comments):
                temp, replies = {}, []
                temp["comment_id"] = index
                temp["comment_text"] = comment['comment_text']
                temp["commentator"] = comment["commenter_name"]

                # e.g. ...get the replies for them
                for index, reply in enumerate(comment['replies']):
                    replies.append(
                        {"reply_id": index, "replier": reply["commenter_name"], "reply": reply['comment_text']})

                temp["replies"] = replies
                data["comments"].append(temp)

            commentator_counts = Counter()

            for comment in data["comments"]:
                commentator_counts[comment["commentator"]] += 1
                for reply in comment["replies"]:
                    commentator_counts[reply["replier"]] += 1

            top_commentators = commentator_counts.most_common(3)
            formatted_top_commentators = [{"name": commentator, "value": count} for commentator, count in top_commentators]


            data["top_commentators"].append(formatted_top_commentators)

            # if no exception is raised, exit the loop
            # json_data = json.dumps(data)
            # return json_data


            return data
            break

        except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
            # if the exception is one of the specified types
            attempt += 1
            if attempt >= MAX_ATTEMPTS:
                # if the maximum number of attempts is reached, raise the exception
                raise e
            else:
                # if not, wait for a few seconds and try again
                print(f"Exception occurred: {e}")
                print(f"Retrying in {DELAY_SECONDS} seconds...")
                time.sleep(DELAY_SECONDS)