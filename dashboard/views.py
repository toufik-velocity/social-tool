from math import ceil
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

from .forms import *
from .scrapper.fb_scrap import FacebookScrapper
from .scrapper.twitter_scrap import TwitterScrapper
from .scrapper.linkedin_scrap import LinkedinScrapper
from .scrapper.sentiments import analyze_sentiments

import datetime
from bson import BSON
import os
import uuid
import facebook_scraper
import urllib.parse
from pymongo import MongoClient
from dotenv import load_dotenv


# Connect to MongoDB
load_dotenv()
client = MongoClient(os.getenv('CLIENT'))
db = client[os.getenv('DB')]
collection = db[os.getenv('COLLECTION')]


@login_required(login_url='signin')
def main(request):
    # Retrieve data from MongoDB
    posts = list(collection.find().sort("last_updated", -1))

    paginator = Paginator(posts, 50)  # Display 5 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts
    }
    # change this to dashbase when
    return render(request, 'dashbase.html', context)


def find_related_usernames(username):
    posts = list(collection.find())
    all_usernames = []
    matching_usernames = []
    substrings = []
    split_names = username.split(",")

    for name in split_names:
        substrings.append(name.replace(" ", "_"))
        substrings.append(name.replace("_", " "))
        substrings.append(name.upper())
        substrings.append(name.lower())
        substrings.append(name.title())
        substrings.extend(name.split(" "))

    # print(f"{substrings}\n\n")
    for post in posts:
        all_usernames.append(post['username'])

    # print(f"{all_usernames}\n\n")
    for substring in substrings:
        for word in all_usernames:
            if substring in word:
                matching_usernames.append(word)

    # print(f"matching usernames: {matching_usernames}\n\n")

    return matching_usernames


@login_required(login_url='signin')
def search_results(request):
    try:
        username = request.GET.get('username')
        likes = request.GET.get('likes')
        comments = request.GET.get('comments')
        shares = request.GET.get('shares')
        post_date = request.GET.get('post_date')

        context = {}
        results = []
        query = {}
        query_conditions = []
        matching_usernames = find_related_usernames(username)
        matching_usernames = list(set(matching_usernames))

        if username:
            query_conditions.append({'username': {'$in': matching_usernames}})

        if likes:
            likes = int(likes)
            if likes > 0:
                query_conditions.append({'likes.value': {'$lte': likes}})

        if comments:
            comments = int(comments)
            if comments > 0:
                query_conditions.append(
                    {'num_comments.value': {'$lte': comments}})

        if shares:
            shares = int(shares)
            if shares > 0:
                query_conditions.append({'shares.value': {'$lte': shares}})

        if post_date:
            format_string = "%Y-%m-%d"
            date_object = datetime.datetime.strptime(post_date, format_string)
            formatted_date = date_object.strftime('%d/%m/%Y')
            query_conditions.append({'post_date': formatted_date})

        query = {"$and": query_conditions} if query_conditions else {}
        results = list(collection.find(query))

        if results:
            context = {
                'results': results
            }
            paginator = Paginator(results, 5)  # Display 5 items per page
            page = request.GET.get('page')
            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver the first page.
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)

        else:
            messages.info(
                request, "There are no results for your search query.")
            context = {}

        return render(request, 'search_post.html', context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='signin')
def new_post_manually(request):
    # Retrieve data from MongoDB
    posts = list(collection.find().sort("last_updated", -1))

    paginator = Paginator(posts, 50)  # Display 5 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
    }
    if request.method == 'POST':
        form = NewPostManuallyForm(request.POST)
        if form.is_valid():
            # Get the form data
            platform_id = form.cleaned_data['platform_id']
            post_date = form.cleaned_data['post_date']
            user_id = form.cleaned_data['user_id']
            username = form.cleaned_data['username']
            
            content_type = form.cleaned_data['content_type']
            content = form.cleaned_data['content']
            url = form.cleaned_data['url']
            post_id = form.cleaned_data['post_id']

            likes = form.cleaned_data['likes']
            shares = form.cleaned_data['shares']
            num_comments = form.cleaned_data['num_comments']
            man_comments = form.cleaned_data['comments']

            timestamp = datetime.datetime.now().isoformat()
            
            # required data
            data = {"platform_id": "",
                    "user_id": user_id,
                    "username": username,
                    "post_id": post_id,
                    "content": content,
                    "content_type": content_type,
                    "post_date": post_date.isoformat(),
                    "url": url,
                    "likes": [{"value": likes, "timestamp": datetime.datetime.now()}],
                    "shares": [{"value": shares, "timestamp": datetime.datetime.now()}],
                    "num_comments": [{"value": num_comments, "timestamp": datetime.datetime.now()}],
                    "generated_index":"",
                    "comments": [],
                    "user_provided_id": post_id,
                    "switch_status": False,
                    "likes_growth_rates": [],
                    "shares_growth_rates": [],
                    "num_comments_growth_rates": [],
                    "top_commentators": [],
                    }
            
            if platform_id == 'Facebook':
                data['platform_id'] = '1'

            elif platform_id == 'Twitter':
                data['platform_id'] = '2'
            
            elif platform_id == 'Linkedin':
                data['platform_id'] = '3'
            
            elif platform_id == 'TikTok':
                data['platform_id'] = '4'
            
            elif platform_id == 'Instagram':
                data['platform_id'] = '5'

            elif platform_id == 'Youtube':
                data['platform_id'] = '6'

            # Extract all comments and replies
            for key, value in man_comments.items():
                data['comments'].append(value)

            comments = []
            for comment in data['comments']:
                comments.append(comment['comment_text'])
            sentiment_results = analyze_sentiments(comments)

            data["positive_score"] = sentiment_results["good"]
            data["neutral_score"] = sentiment_results["neutral"]
            data["bad_score"] = sentiment_results["bad"]
           
            new_id = str(uuid.uuid4())

            data["last_updated"] = datetime.datetime.now()
            data["id"] = new_id
            collection.insert_one(data)

            messages.info(
            request, f"{data['username']}'s post metrics with ID {data['post_id']} inserted successfully.")

            return redirect('main')

    else:
        form = NewPostManuallyForm(initial={'user_id': 'None'})

    context['form'] = form

    return render(request, 'new_post_manually.html', context)

@login_required(login_url='signin')
def newPost(request):
    if request.method == 'POST':
        context = {}
        scrapped_result = None
        pid = request.POST['post_id']
        platform = request.POST['platform']
        frequency = request.POST['frequency']
        # Get the LinkedIn username if provided
        username = request.POST.get('linkedin_username', None)

        try:
            if platform == 'Facebook':
                check_existing = collection.find_one(
                    {"$and": [{"user_provided_id": pid}, {"platform_id": '1'}]})
                if check_existing:
                    scrapped_result = FacebookScrapper(pid, check_existing)
                else:
                    scrapped_result = FacebookScrapper(pid)
                scrapped_result['frequency'] = int(frequency) * 3600

            elif platform == 'Twitter':
                check_existing = collection.find_one(
                    {"$and": [{"user_provided_id": pid}, {"platform_id": '2'}]})
                if check_existing:
                    scrapped_result = TwitterScrapper(pid, check_existing)
                else:
                    scrapped_result = TwitterScrapper(pid)
                scrapped_result['frequency'] = int(frequency) * 3600

            elif platform == 'LinkedIn':
                check_existing = collection.find_one(
                    {"$and": [{"user_provided_id": pid}, {"platform_id": '3'}]})
                if check_existing:
                    scrapped_result = LinkedinScrapper(
                        pid, username, check_existing)
                else:
                    scrapped_result = LinkedinScrapper(pid, username)
                # print(scrapped_result)
                scrapped_result['frequency'] = int(frequency) * 3600

            context = {
                'scrapped_result': scrapped_result,
            }

        except facebook_scraper.exceptions.InvalidCookies as e:
            messages.info(request, f"{e} for facebook")

            return redirect('new_post')

        except facebook_scraper.exceptions.TemporarilyBanned as e:
            messages.info(request, f"{e} from facebook")

            return redirect('new_post')

        except facebook_scraper.exceptions.AccountDisabled as e:
            messages.info(request, f"{e} from facebook")

            return redirect('new_post')

        except facebook_scraper.exceptions.NotFound as e:
            messages.info(
                request, f"{e} or maybe check if you scrapped the wrong social media platform.")

            return redirect('new_post')

        except IndexError as e:
            messages.info(
                request, f"{e} or maybe check if you scrapped the wrong social media platform.")

            return redirect('new_post')
        
        if username:
            scrapped_result['linkedin_username'] = username
            
        string_scrapped_result = str(scrapped_result)
        request.session['string_scrapped_result'] = string_scrapped_result

        return render(request, 'new_post.html', context)

    return render(request, 'new_post.html')


@login_required(login_url='signin')
def savePost(request, post_id):
    string_scrapped_result = request.session.get('string_scrapped_result')
    if '_id' == string_scrapped_result[2:5]:
        scrapped_result = eval(
            string_scrapped_result[0]+string_scrapped_result[46:])
    else:
        scrapped_result = eval(string_scrapped_result)
    # Check if the post with the given post_id already exists in the database
    existing_post = collection.find_one({"user_provided_id": post_id})
    if existing_post:
        scrapped_result["last_updated"] = datetime.datetime.now()
        collection.update_one({"user_provided_id": post_id}, {
                              "$set": scrapped_result})
        messages.info(
            request, f"{scrapped_result['username']}'s post metrics with ID {post_id} updated successfully.")

    else:
        new_id = str(uuid.uuid4())
        scrapped_result["last_updated"] = datetime.datetime.now()
        scrapped_result["id"] = new_id
        collection.insert_one(scrapped_result)
        messages.info(
            request, f"{scrapped_result['username']}'s post metrics with ID {post_id} inserted successfully.")

    post = collection.find_one({"user_provided_id": post_id})

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
    collection.update_one({"user_provided_id": post_id}, {"$set": post})

    del request.session['string_scrapped_result']

    return redirect('main')

def post_life_span(post_id):
    post = list(collection.find({'post_id': post_id}))[0]
    likes_growth_rates = post['likes_growth_rates']
    shares_growth_rates = post['shares_growth_rates']
    num_comments_growth_rates = post['num_comments_growth_rates']
    likes_all_rates = []
    shares_all_rates = []
    num_comments_all_rates = []
    likes_count = 0
    shares_count = 0
    num_comments_count = 0

    if 'frequency' in post:
        frequency = post['frequency']
    else:
        frequency = 0
    # Last 4 likes growth rate count if 0
    for rate in likes_growth_rates:
        likes_all_rates.append(rate['growth_rate'])
    
    for rate in likes_all_rates[-4:]:
        if rate == 0:
            likes_count += 1

    # Last 4 shares growth rate count if 0
    for rate in shares_growth_rates:
        shares_all_rates.append(rate['growth_rate'])
    
    for rate in shares_all_rates[-4:]:
        if rate == 0:
            shares_count += 1
        
    # Last 4 num_comments growth rate count if 0
    for rate in num_comments_growth_rates:
        num_comments_all_rates.append(rate['growth_rate'])
    
    for rate in num_comments_all_rates[-4:]:
        if rate == 0:
            num_comments_count += 1
    
    if likes_count == 4 and shares_count == 4 and num_comments_count == 4:
        near_death = True
        life_span = ceil((frequency / 3600) * 4)
    else:
        near_death = False
        life_span = None

    return near_death, life_span

def  post_detail(request, post_id):
    # Retrieve data from MongoDB
    posts = list(collection.find().sort("last_updated", -1))

    paginator = Paginator(posts, 50)  # Display 5 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    result = list(collection.find({'post_id': post_id}))[0]
    context = {
        'result': result,
        'posts': posts,
        }
    
    near_death, life_span = post_life_span(post_id)
    context['near_death'] = near_death
    context['life_span'] = life_span
    
    if 'frequency' in result:
        context['frequency'] = ceil(result['frequency'] / 3600)

    username = list(collection.find({'post_id': post_id}))[0]['username']
    optimal_start_time, optimal_end_time = optimal_time(username)
    context['optimal_start_time'] = optimal_start_time
    context['optimal_end_time'] = optimal_end_time

    return context

def optimal_time(username):
    likes, comments, shares = [], [], []
    posts = list(collection.find({'username': username}))
    for post in posts:
        likes.append(post['likes'])
        comments.append(post['num_comments'])
        shares.append(post['shares'])
    
    engagement_data = [{"likes": like, "shares": share, "comments": comment} for like, share, comment in zip(likes, shares, comments)]
    

    time_ranges = [
        {"start": datetime.time(0, 0), "end": datetime.time(3, 59)},
        {"start": datetime.time(4, 0), "end": datetime.time(7, 59)},
        {"start": datetime.time(8, 0), "end": datetime.time(11, 59)},
        {"start": datetime.time(12, 0), "end": datetime.time(15, 59)},
        {"start": datetime.time(16, 0), "end": datetime.time(19, 59)},
        {"start": datetime.time(20, 0), "end": datetime.time(23, 59)},
    ]

    engagement_rates = []

    for time_range in time_ranges:
        total_likes = 0
        total_comments = 0
        total_shares = 0
        count = 0
        for data in engagement_data:
            likes = data['likes']
            comments = data['comments']
            shares = data['shares']
            for i in range(len(likes)):
                timestamp = likes[i]["timestamp"]
                if time_range["start"] <= timestamp.time() <= time_range["end"]:
                    total_likes += likes[i]["value"]
                    total_comments += comments[i]["value"]
                    total_shares += shares[i]["value"]
                    count += 1

        average_likes = total_likes / count if count > 0 else 0
        average_comments = total_comments / count if count > 0 else 0
        average_shares = total_shares / count if count > 0 else 0
        average_engagement = (average_likes + average_comments + average_shares) / 3

        engagement_rates.append({"time_range": time_range, "average_engagement": average_engagement})

    engagement_rates.sort(key=lambda x: x["average_engagement"], reverse=True)

    optimal_time_range = engagement_rates[0]["time_range"]

    return optimal_time_range['start'], optimal_time_range['end']

@login_required(login_url='signin')
def postDetail(request, post_id):
    context = post_detail(request, post_id)

    return render(request, 'post_detail.html', context)


@login_required(login_url='signin')
def addPost(request, post_id):
    # Retrieve data from MongoDB
    posts = list(collection.find().sort("last_updated", -1))

    paginator = Paginator(posts, 50)  # Display 5 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    result = list(collection.find({'post_id': post_id}))[0]
    context = {
        'result': result,
        'posts': posts

    }
    post_details = list(collection.find({'post_id': post_id}))
    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            # Get the form data
            platform_id = form.cleaned_data['platform_id']
            user_id = form.cleaned_data['user_id']
            username = form.cleaned_data['username']
            content_type = form.cleaned_data['content_type']
            content = form.cleaned_data['content']
            url = form.cleaned_data['url']
            post_id1 = form.cleaned_data['post_id']
            likes = form.cleaned_data['likes']
            shares = form.cleaned_data['shares']
            num_comments = form.cleaned_data['num_comments']

            last_updated = datetime.datetime.now()
            timestamp = datetime.datetime.now()

            updated_likes = {"value": likes, "timestamp": timestamp}
            existing_likes = post_details[0]['likes']
            existing_likes.append(updated_likes)

            updated_shares = {"value": shares, "timestamp": timestamp}
            existing_shares = post_details[0]['shares']
            existing_shares.append(updated_shares)

            updated_num_comments = {
                "value": num_comments, "timestamp": timestamp}
            existing_num_comments = post_details[0]['num_comments']
            existing_num_comments.append(updated_num_comments)

            data = {
                    "user_id": user_id,
                    "username": username,
                    "post_id": post_id1,
                    "content": content,
                    "content_type": content_type,
                    "url": url,
                    "user_provided_id": post_id1,
                    'likes': existing_likes,
                    'shares': existing_shares,
                    'num_comments': existing_num_comments,
                    'last_updated': last_updated,
                }

            if platform_id == 'Facebook':
                data['platform_id'] = '1'

            elif platform_id == 'Twitter':
                data['platform_id'] = '2'
            
            elif platform_id == 'Linkedin':
                data['platform_id'] = '3'
            
            elif platform_id == 'TikTok':
                data['platform_id'] = '4'
            
            elif platform_id == 'Instagram':
                data['platform_id'] = '5'

            elif platform_id == 'Youtube':
                data['platform_id'] = '6'

            # Identify the documents you want to update
            document_filter = {"post_id": post_id}

            # # Define the update operation
            update_operation = {"$set": data}

            # Perform the update
            collection.update_many(document_filter, update_operation)

            client.close()
            messages.info(
                request, f"{post_details[0]['username']}'s post metrics with ID {post_id} added successfully.")

            context = post_detail(request, post_id1)

            return render(request, 'post_detail.html', context)

    else:
        form = AddForm(initial={'platform_id': post_details[0]['platform_id'], 'user_id': post_details[0]['user_id'], 'username': post_details[0]['username'], 'content_type': post_details[0]['content_type'], 'content': post_details[0]['content'],
                       'url': post_details[0]['url'], 'post_id': post_details[0]['post_id'], 'likes': post_details[0]['likes'][-1]['value'], 'shares': post_details[0]['shares'][-1]['value'], 'num_comments': post_details[0]['num_comments'][-1]['value']})

    context['form'] = form

    return render(request, 'add_post.html', context)

@login_required(login_url='signin')
def refresh(request, user_provided_id):
    pid = user_provided_id
    post = list(collection.find({"user_provided_id": pid}))[0]
    platform = post['platform_id']
    post_id = post['post_id']
    context = post_detail(request, post_id)

    if 'linkedin_username' in post:
        username = post['linkedin_username']

    try:
        if platform == '1':
            check_existing = collection.find_one(
                {"$and": [{"user_provided_id": pid}, {"platform_id": '1'}]})
            if check_existing:
                scrapped_result = FacebookScrapper(pid, check_existing)
            else:
                scrapped_result = FacebookScrapper(pid)

        elif platform == '2':
            check_existing = collection.find_one(
                {"$and": [{"user_provided_id": pid}, {"platform_id": '2'}]})
            if check_existing:
                scrapped_result = TwitterScrapper(pid, check_existing)
            else:
                scrapped_result = TwitterScrapper(pid)

        elif platform == '3':
            check_existing = collection.find_one(
                {"$and": [{"user_provided_id": pid}, {"platform_id": '3'}]})
            if check_existing:
                scrapped_result = LinkedinScrapper(
                    pid, username, check_existing)
            else:
                scrapped_result = LinkedinScrapper(pid, username)
            
        string_scrapped_result = str(scrapped_result)

    except facebook_scraper.exceptions.InvalidCookies as e:
        messages.info(request, f"{e} for facebook")

        return render(request, 'post_detail.html', context)

    except facebook_scraper.exceptions.TemporarilyBanned as e:
        messages.info(request, f"{e} from facebook")

        return render(request, 'post_detail.html', context)

    except facebook_scraper.exceptions.AccountDisabled as e:
        messages.info(request, f"{e} from facebook")

        return render(request, 'post_detail.html', context)
    

    if '_id' == string_scrapped_result[2:5]:
        scrapped_result = eval(
            string_scrapped_result[0]+string_scrapped_result[46:])
    else:
        scrapped_result = eval(string_scrapped_result)
    
    
    scrapped_result["last_updated"] = datetime.datetime.now()
    collection.update_one({"user_provided_id": user_provided_id}, {
                            "$set": scrapped_result})
    messages.info(
        request, f"{scrapped_result['username']}'s post metrics with ID {post_id} updated successfully.")


    post = collection.find_one({"user_provided_id": user_provided_id})

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
    collection.update_one({"user_provided_id": user_provided_id}, {"$set": post})

    return render(request, 'post_detail.html', context)


@login_required(login_url='signin')
def deletePost(request, post_id):
    # Delete a single document
    result = list(collection.find({'post_id': post_id}))
    collection.delete_one({'post_id': post_id})
    messages.info(
        request, f"Successfully deleted {result[0]['username']}'s post with ID {post_id}.")

    # Close the MongoDB connection
    client.close()
    return redirect('main')

@login_required(login_url='signin')
def editPost(request, post_id):
    post_details = list(collection.find({'post_id': post_id}))

    # Retrieve data from MongoDB
    posts = list(collection.find().sort("last_updated", -1))

    paginator = Paginator(posts, 50)  # Display 5 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts
    }

    if request.method == 'POST':
        frequency = request.POST['frequency']
        last_updated = datetime.datetime.now()

        data = {
            'frequency': (int(frequency) * 3600),
            'last_updated': last_updated,
        }

        # Identify the documents you want to update
        document_filter = {"post_id": post_id}

        # # Define the update operation
        update_operation = {"$set": data}

        # Perform the update
        collection.update_many(document_filter, update_operation)

        client.close()
        messages.info(
            request, f"{post_details[0]['username']}'s post frequency with ID {post_id} updated successfully.")

        context = post_detail(request, post_id)

        return render(request, 'post_detail.html', context)

    return render(request, 'edit_post.html', context)

@login_required(login_url='signin')
def kill_switch(request, post_id):
    if request.method == 'GET':
        switch_status = request.GET.get('switch_status')

        if switch_status == 'on':
            document_filter = {'post_id': post_id}
            update_operation = {'switch_status': True}
            collection.update_one(document_filter, {"$set": update_operation})
        
        if switch_status == None:
            document_filter = {'post_id': post_id}
            update_operation = {'switch_status': False}
            collection.update_one(document_filter, {"$set": update_operation})

    context = post_detail(request, post_id)
    context['switch_status'] = switch_status

    return render(request, 'post_detail.html', context)

@login_required(login_url='signin')
def graphAnaylsis(request, post_id):
    post = list(collection.find({'post_id': post_id}))

    # Likes anaylsis
    likes = post[0]['likes']
    # likes_list = [0]
    likes_list = []
    likes_timeframes = []
    likes_growth_rates_list = [0]
    likes_growth_rates = []
    likes_first_time = likes[0]['timestamp']

    for like in likes:
        likes_list.append(like['value'])
        likes_first_time = like['timestamp']
        likes_timeframes.append(likes_first_time)

    for data in likes:
        data['timestamp'] = parse_datetime(str(data['timestamp']))

    likes.sort(key=lambda x: x['timestamp'])
    for i in range(1, len(likes)):
        old_value = likes[i - 1]['value']
        new_value = likes[i]['value']
        timestamp = likes[i]['timestamp']

        if old_value != 0:
            growth_rate = round(((new_value - old_value) / old_value) * 100, 2)
        else:
            growth_rate = 0

        likes_growth_rates.append(
            {"growth_rate": growth_rate, "timestamp": timestamp})
        likes_growth_rates_exists = collection.find({'post_id': post_id})

        if likes_growth_rates_exists:
            collection.update_one({"post_id": post_id}, {
                                  "$set": {"likes_growth_rates": likes_growth_rates}})

        else:
            collection.insert_one({"post_id": post_id}, {
                                  "$set": {"likes_growth_rates": likes_growth_rates}})
        likes_growth_rates_list.append(growth_rate)

    # Shares anaylsis
    shares = post[0]['shares']
    shares_growth_rates_list = [0]
    shares_growth_rates = []
    shares_first_time = shares[0]['timestamp']
    shares_list = []
    shares_timeframes = []

    for share in post[0]['shares']:
        shares_list.append(share['value'])
        shares_first_time = share['timestamp']
        shares_timeframes.append(shares_first_time)

    for data in shares:
        data['timestamp'] = parse_datetime(str(data['timestamp']))

    shares.sort(key=lambda x: x['timestamp'])
    for i in range(1, len(shares)):
        old_value = shares[i - 1]['value']
        new_value = shares[i]['value']
        timestamp = shares[i]['timestamp']

        if old_value != 0:
            growth_rate = round((new_value - old_value) / old_value * 100, 2)
        else:
            growth_rate = 0

        shares_growth_rates.append(
            {"growth_rate": growth_rate, "timestamp": timestamp})
        shares_growth_rates_exists = collection.find({'post_id': post_id})

        if shares_growth_rates_exists:
            collection.update_one({"post_id": post_id}, {
                                  "$set": {"shares_growth_rates": shares_growth_rates}})

        else:
            collection.insert_one({"post_id": post_id}, {
                                  "$set": {"shares_growth_rates": shares_growth_rates}})
        shares_growth_rates_list.append(growth_rate)

    # Number comments anaylsis
    num_comments = post[0]['num_comments']
    num_comments_growth_rates_list = [0]
    num_comments_growth_rates = []
    num_comments_list = []
    num_comments_timeframes = []
    num_comments_first_time = num_comments[0]['timestamp']

    for num_comment in post[0]['num_comments']:
        num_comments_list.append(num_comment['value'])
        num_comments_first_time = num_comment['timestamp']
        num_comments_timeframes.append(num_comments_first_time)

    for data in num_comments:
        data['timestamp'] = parse_datetime(str(data['timestamp']))

    num_comments.sort(key=lambda x: x['timestamp'])
    for i in range(1, len(num_comments)):
        old_value = num_comments[i - 1]['value']
        new_value = num_comments[i]['value']
        timestamp = num_comments[i]['timestamp']

        if old_value != 0:
            growth_rate = round((new_value - old_value) / old_value * 100, 2)
        else:
            growth_rate = 0
        num_comments_growth_rates.append(
            {"growth_rate": growth_rate, "timestamp": timestamp})
        num_comments_growth_rates_exists = collection.find(
            {'post_id': post_id})

        if num_comments_growth_rates_exists:
            collection.update_one({"post_id": post_id}, {
                                  "$set": {"num_comments_growth_rates": num_comments_growth_rates}})

        else:
            collection.insert_one({"post_id": post_id}, {
                                  "$set": {"num_comments_growth_rates": num_comments_growth_rates}})
        num_comments_growth_rates_list.append(growth_rate)

    # Sentiments
    positive_score = post[0]['positive_score']
    bad_score = post[0]['bad_score']
    neutral_score = post[0]['neutral_score']

    bad_score = post[0]['bad_score']
    sentiment_anaylsis = [positive_score, neutral_score, bad_score]

    whole_data = {
        'likes_list': likes_list,
        'likes_timeframes': likes_timeframes,
        'likes_growth_rates_list': likes_growth_rates_list,
        'shares_list': shares_list,
        'shares_timeframes': shares_timeframes,
        'shares_growth_rates_list': shares_growth_rates_list,
        'num_comments_list': num_comments_list,
        'num_comments_timeframes': num_comments_timeframes,
        'num_comments_growth_rates_list': num_comments_growth_rates_list,
        'sentiment_anaylsis': sentiment_anaylsis,
    }

    return JsonResponse(whole_data)

def help(request):
    return render(request, 'help.html')

def export_data_json(request):
    data = list(collection.find())

    # Convert MongoDB ObjectId to string
    for item in data:
        item['_id'] = str(item['_id'])

    # Return data as JSON
    return JsonResponse(data, safe=False)

@login_required(login_url='signin')
def usersComparison(request):
    posts = list(collection.find())
    all_usernames = []

    for post in posts:
        if 'username' in post and post['username'] not in all_usernames:
            all_usernames.append(post['username'])

    if request.method == 'POST':
        first_username = request.POST['username1']
        second_username = request.POST['username2']
        data = {
            'first_username': first_username,
            'second_username': second_username,
        }

        base_url = 'http://192.168.32.30:9000/'
        query_params = urllib.parse.urlencode(data)
        url = f'{base_url}?{query_params}'

        return HttpResponseRedirect(url)

    context = {
        'all_usernames': all_usernames,
    }

    return render(request, 'comparison.html', context)


def compare_users(request):
    first_name = request.GET.get('first_username')
    second_name = request.GET.get('second_username')

    posts_first_user = collection.find({'username': first_name}, {
                                       'likes': 1, 'num_comments': 1, 'shares': 1})
    posts_second_user = collection.find({'username': second_name}, {
                                        'likes': 1, 'num_comments': 1, 'shares': 1})

    likes_sum_first = 0
    comments_sum_first = 0
    shares_sum_first = 0
    post_count_first = 0
    for post in posts_first_user:
        likes_sum_first += post['likes'][-1]['value']
        comments_sum_first += post['num_comments'][-1]['value']
        shares_sum_first += post['shares'][-1]['value']
        post_count_first += 1

    likes_sum_second = 0
    comments_sum_second = 0
    shares_sum_second = 0
    post_count_second = 0
    for post in posts_second_user:
        likes_sum_second += post['likes'][-1]['value']
        comments_sum_second += post['num_comments'][-1]['value']
        shares_sum_second += post['shares'][-1]['value']
        post_count_second += 1

    average_first_user_likes = likes_sum_first / \
        post_count_first if post_count_first > 0 else 0
    average_first_user_comments = comments_sum_first / \
        post_count_first if post_count_first > 0 else 0
    average_first_user_shares = shares_sum_first / \
        post_count_first if post_count_first > 0 else 0

    average_second_user_likes = likes_sum_second / \
        post_count_second if post_count_second > 0 else 0
    average_second_user_comments = comments_sum_second / \
        post_count_second if post_count_second > 0 else 0
    average_second_user_shares = shares_sum_second / \
        post_count_second if post_count_second > 0 else 0

    response_data = [{
        "user_name": first_name,
        "user_average_likes": average_first_user_likes,
        "user_average_comments": average_first_user_comments,
        "user_average_shares": average_first_user_shares},
        {"user_name": second_name,
         "user_average_likes": average_second_user_likes,
         "user_average_comments": average_second_user_comments,
         "user_average_shares": average_second_user_shares
         }]
    print(response_data)

    return JsonResponse(response_data, safe=False)
