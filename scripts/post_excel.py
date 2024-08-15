import pandas as pd
import json

# Sample data
comments = json.dumps([
    {
        "comment_id": 0,
        "comment_text": "I would love one too",
        "commentator": "Angela White",
        "replies": [
            {
                "reply_id": 0,
                "replier": "Dihan Rahman",
                "reply": "Angela White ore mathar cod ......"
            },
            {
                "reply_id": 1,
                "replier": "Kiloa Zoldik",
                "reply": "Angela White Oui 🤣❤️"
            },
        ]
    }
])

data = {
    "csrfmiddlewaretoken": "your_csrf_token_here",  # Replace with actual CSRF token
    "platform_id": "Facebook",
    "post_date": "2024-07-24",
    "user_id": "12345",
    "username": "john_doe",
    "content_type": "Text",
    "content": "This is a sample post content.",
    "url": "https://example.com/sample-post",
    "post_id": "post123",
    "likes": 100,
    "shares": 10,
    "num_comments": 5,
    "comments": comments,
}

# Convert comments JSON to a list of dictionaries
comments_list = json.loads(data['comments'])

# Create main DataFrame
main_df = pd.DataFrame([{
    "platform_id": data["platform_id"],
    "post_date": data["post_date"],
    "user_id": data["user_id"],
    "username": data["username"],
    "content_type": data["content_type"],
    "content": data["content"],
    "url": data["url"],
    "post_id": data["post_id"],
    "likes": data["likes"],
    "shares": data["shares"],
    "num_comments": data["num_comments"]
}])

# Create comments DataFrame
comments_data = []
replies_data = []

for comment in comments_list:
    comment_id = comment["comment_id"]
    comment_text = comment["comment_text"]
    commentator = comment["commentator"]
    comments_data.append({
        "comment_id": comment_id,
        "comment_text": comment_text,
        "commentator": commentator
    })
    for reply in comment["replies"]:
        replies_data.append({
            "comment_id": comment_id,
            "reply_id": reply["reply_id"],
            "replier": reply["replier"],
            "reply": reply["reply"]
        })

comments_df = pd.DataFrame(comments_data)
replies_df = pd.DataFrame(replies_data)

# Write DataFrames to Excel file
with pd.ExcelWriter("post_data.xlsx") as writer:
    main_df.to_excel(writer, sheet_name="Post", index=False)
    comments_df.to_excel(writer, sheet_name="Comments", index=False)
    replies_df.to_excel(writer, sheet_name="Replies", index=False)

print("Data written to post_data.xlsx successfully.")
