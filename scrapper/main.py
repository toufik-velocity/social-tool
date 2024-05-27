from pymongo import MongoClient
from datetime import datetime
from fb_scrap import FacebookScrapper
from twitter_scrap import TwitterScrapper
from sentiments import analyze_sentiments
import uuid

# connect to the MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['SocialListening']
collection = db['dashboard_post']

def facebook_scraping(pid):
    # video
    # pids = ["3254964768150836","641399861360467","641341061366347","641051054728681","640846891415764","640722598094860","640664981433955","640619858105134","640510258116094","640257744808012","640210974812689","640003041500149","639918311508622","639869191513534","639718584861928","639529344880852","639423834891403","639386951561758","639247548242365"]
    

    # Check if the post with the given post_id already exists in the database
    existing_post = collection.find_one({"user_provided_id": pid})

    if existing_post:
        existing_metrics = existing_post
        metrics = FacebookScrapper(pid, existing_metrics)
        metrics["last_updated"] = datetime.now()
        collection.update_one({"user_provided_id": pid}, {"$set": metrics})

        print("Metrics updated successfully.")
        
    else:
        new_id = str(uuid.uuid4())
        metrics = FacebookScrapper(pid)
        metrics["last_updated"] = datetime.now()
        metrics["id"] = new_id
        collection.insert_one(metrics)
        print(f"Inserted metrics with ID {new_id}")
        
        
    post = collection.find_one({"post_id": metrics['post_id']})

    # Extract all comments and replies
    comments = []
    for comment in post["comments"]:
        comments.append(comment['comment_text'])
        for reply in comment["replies"]:
            comments.append(reply["reply"])
    sentiment_results = analyze_sentiments(comments)

    post["positive_score"] = sentiment_results["good"]
    post["neutral_score"] = sentiment_results["neutral"]
    post["bad_score"] = sentiment_results["bad"]
    collection.update_one({"post_id": metrics['post_id']}, {"$set": post})

def twitter_scrapping(pid):
    # pids = ["1660498047015727104","1663244096503160833","1663944001224081408"]
    # pids = ["1660498047015727104", "1665979021539291137"]

    # Check if the post with the given post_id already exists in the database
    existing_post = collection.find_one({"user_provided_id": pid})

    if existing_post:
        existing_metrics = existing_post
        metrics = TwitterScrapper(pid, existing_metrics)
        metrics["last_updated"] = datetime.now()
        collection.update_one({"user_provided_id": pid}, {"$set": metrics})
        print("Metrics updated successfully.")
        
    else:
        new_id = str(uuid.uuid4())
        metrics = TwitterScrapper(pid)
        metrics["last_updated"] = datetime.now()
        metrics["id"] = new_id
        collection.insert_one(metrics)
        print(f"Inserted metrics with ID {new_id}")
        

    post = collection.find_one({"post_id": metrics['post_id']})

    # Extract all comments and replies
    comments = []
    for comment in post["comments"]:
        comments.append(comment['comment_text'])
    sentiment_results = analyze_sentiments(comments)

    post["positive_score"] = sentiment_results["good"]
    post["neutral_score"] = sentiment_results["neutral"]
    post["bad_score"] = sentiment_results["bad"]
    collection.update_one({"post_id": metrics['post_id']}, {"$set": post})

# def main():
#     parser = argparse.ArgumentParser(description="Scraping Facebook and Twitter data.")
#     parser.add_argument("-facebook", action="store_true", help="Scrape Facebook data.")
#     parser.add_argument("-twitter", action="store_true", help="Scrape Twitter data.")

#     args = parser.parse_args()

#     if args.facebook:
#         facebook_scraping()
#     elif args.twitter:
#         twitter_scrapping()
#     else:
#         print("Please provide a flag for Facebook or Twitter using -facebook or -twitter.")

# if __name__ == "__main__":
#     main()



