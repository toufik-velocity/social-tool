from math import ceil
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

from .utils import get_social_media_platform
from .models import Post  # Import your Post model
from .forms import *
from .scrapper.fb_scrap import FacebookScrapper
from .scrapper.twitter_scrap import TwitterScrapper
from .scrapper.linkedin_scrap import LinkedinScrapper
from .scrapper.sentiments import analyze_sentiments

import datetime
import uuid
import facebook_scraper
import urllib.parse

@login_required(login_url='signin')
def main(request):
    # Retrieve data from PostgreSQL using Django ORM
    posts = Post.objects.all().order_by('-last_updated')

    paginator = Paginator(posts, 50)  # Display 50 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver the last page of results.
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts
    }
    return render(request, 'dashbase.html', context)

def find_related_usernames(username):
    posts = Post.objects.all()
    all_usernames = [post.username for post in posts]
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

    for substring in substrings:
        for word in all_usernames:
            if substring in word:
                matching_usernames.append(word)

    return matching_usernames

@login_required(login_url='signin')
def search_results(request):
    try:
        username = request.GET.get('username')
        likes = request.GET.get('likes')
        comments = request.GET.get('comments')
        shares = request.GET.get('shares')
        post_date = request.GET.get('post_date')

        query = Post.objects.all()
        matching_usernames = find_related_usernames(username)
        matching_usernames = list(set(matching_usernames))

        if username:
            query = query.filter(username__in=matching_usernames)
        
        if likes:
            likes = int(likes)
            if likes > 0:
                query = query.filter(likes__value__lte=likes)
        
        if comments:
            comments = int(comments)
            if comments > 0:
                query = query.filter(num_comments__value__lte=comments)
        
        if shares:
            shares = int(shares)
            if shares > 0:
                query = query.filter(shares__value__lte=shares)
        
        if post_date:
            query = query.filter(post_date=datetime.strptime(post_date, '%Y-%m-%d').date())

        results = query
        context = {'results': results}
        paginator = Paginator(results, 5)  # Display 5 items per page
        page = request.GET.get('page')
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        if not results:
            messages.info(request, "There are no results for your search query.")

        return render(request, 'search_post.html', context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='signin')
def new_post_manually(request):
    posts = Post.objects.all().order_by('-last_updated')
    paginator = Paginator(posts, 50)  # Display 50 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {'posts': posts}
    if request.method == 'POST':
        form = NewPostManuallyForm(request.POST)
        if form.is_valid():
            post_data = form.cleaned_data
            platform = get_social_media_platform(post_data['platform_id'])
            comments = []
            for comment in post_data['comments']:
                comments.append(comment['comment_text'])

            sentiment_results = analyze_sentiments(comments)
            now_str = datetime.datetime.now().isoformat()

            new_post = Post(
                id=uuid.uuid4(),
                platform=platform,
                username=post_data['username'],
                post_id=post_data['post_id'],
                likes=[{'value': post_data['likes'], 'timestamp': now_str}],
                num_comments=[{'value': post_data['num_comments'], 'timestamp': now_str}],
                shares=[{'value': post_data['shares'], 'timestamp': now_str}],
                post_date=post_data['post_date'],
                content=post_data['content'],
                user_provided_id=post_data['post_id'],
                comments=post_data['comments'],
                likes_growth_rates=[],
                shares_growth_rates=[],
                num_comments_growth_rates=[],
                positive_score=sentiment_results["good"],
                neutral_score=sentiment_results["neutral"],
                bad_score=sentiment_results["bad"],
                frequency=0,
                switch_status=False,
            )
            new_post.save()

            messages.info(request, f"{new_post.username}'s post metrics with ID {new_post.post_id} inserted successfully.")
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
        username = request.POST.get('linkedin_username', None)

        try:
            if platform == 'Facebook':
                check_existing = Post.objects.filter(user_provided_id=pid, platform_id='1').first()
                scrapped_result = FacebookScrapper(pid, check_existing) if check_existing else FacebookScrapper(pid)
                scrapped_result['frequency'] = int(frequency) * 3600

            elif platform == 'Twitter':
                check_existing = Post.objects.filter(user_provided_id=pid, platform_id='2').first()
                scrapped_result = TwitterScrapper(pid, check_existing) if check_existing else TwitterScrapper(pid)
                scrapped_result['frequency'] = int(frequency) * 3600

            elif platform == 'LinkedIn':
                check_existing = Post.objects.filter(user_provided_id=pid, platform_id='3').first()
                scrapped_result = LinkedinScrapper(pid, username, check_existing) if check_existing else LinkedinScrapper(pid, username)
                scrapped_result['frequency'] = int(frequency) * 3600

            context = {'scrapped_result': scrapped_result}

        except facebook_scraper.exceptions.InvalidCookies as e:
            messages.info(request, f"{e} for Facebook")
            return redirect('new_post')

        except facebook_scraper.exceptions.TemporarilyBanned as e:
            messages.info(request, f"{e} from Facebook")
            return redirect('new_post')

        except facebook_scraper.exceptions.AccountDisabled as e:
            messages.info(request, f"{e} from Facebook")
            return redirect('new_post')

        except facebook_scraper.exceptions.NotFound as e:
            messages.info(request, f"{e} or maybe check if you scrapped the wrong social media platform.")
            return redirect('new_post')

        except IndexError as e:
            messages.info(request, f"{e} or maybe check if you scrapped the wrong social media platform.")
            return redirect('new_post')

        if username:
            scrapped_result['linkedin_username'] = username

        request.session['scrapped_result'] = scrapped_result

        return render(request, 'new_post.html', context)

    return render(request, 'new_post.html')

@login_required(login_url='signin')
def savePost(request, post_id):
    scrapped_result = request.session.get('scrapped_result')
    existing_post = Post.objects.filter(user_provided_id=post_id).first()
    
    if existing_post:
        for key, value in scrapped_result.items():
            setattr(existing_post, key, value)
        existing_post.last_updated = datetime.now()
        existing_post.save()
        messages.info(request, f"{existing_post.username}'s post metrics with ID {post_id} updated successfully.")
    else:
        new_post = Post(**scrapped_result)
        new_post.id = uuid.uuid4()
        new_post.last_updated = datetime.now()
        new_post.save()
        messages.info(request, f"{new_post.username}'s post metrics with ID {post_id} inserted successfully.")
    
    comments = [comment['comment_text'] for comment in new_post.comments]
    sentiment_results = analyze_sentiments(comments)
    new_post.positive_score = sentiment_results['good']
    new_post.neutral_score = sentiment_results['neutral']
    new_post.bad_score = sentiment_results['bad']
    new_post.save()

    del request.session['scrapped_result']
    return redirect('main')

def post_life_span(post_id):
    post = Post.objects.filter(post_id=post_id).first()
    likes_growth_rates = post.likes_growth_rates
    shares_growth_rates = post.shares_growth_rates
    num_comments_growth_rates = post.num_comments_growth_rates
    likes_count = sum(1 for rate in likes_growth_rates[-4:] if rate == 0)
    shares_count = sum(1 for rate in shares_growth_rates[-4:] if rate == 0)
    num_comments_count = sum(1 for rate in num_comments_growth_rates[-4:] if rate == 0)

    near_death = likes_count == 4 and shares_count == 4 and num_comments_count == 4
    life_span = ceil((post.frequency / 3600) * 4) if near_death else None

    return near_death, life_span

def post_detail(request, post_id):
    posts = Post.objects.all().order_by('-last_updated')
    paginator = Paginator(posts, 50)  # Display 50 items per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    
    post = Post.objects.filter(post_id=post_id).first()
    context = {'result': post, 'posts': posts}
    near_death, life_span = post_life_span(post_id)
    context['near_death'] = near_death
    context['life_span'] = life_span
    context['frequency'] = ceil(post.frequency / 3600) if post.frequency else None

    username = post.username
    optimal_start_time, optimal_end_time = optimal_time(username)
    context['optimal_start_time'] = optimal_start_time
    context['optimal_end_time'] = optimal_end_time

    return render(request, 'post_detail.html', context)

def optimal_time(username):
    likes, comments, shares = [], [], []
    posts = Post.objects.filter(username=username)

    for post in posts:
        likes.append(post.likes)
        comments.append(post.num_comments)
        shares.append(post.shares)
    
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
                timestamp_str = likes[i]["timestamp"]
                timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
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
    post = get_object_or_404(Post, id=post_id)
    context = {'post': post}
    return render(request, 'post_detail.html', context)

@login_required(login_url='signin')
def addPost(request, post_id):
    posts = Post.objects.all().order_by('-last_updated')

    paginator = Paginator(posts, 50)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = AddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.info(request, "Post added successfully.")
            return redirect('post_detail', post_id=form.instance.id)
    else:
        form = AddForm()

    context = {'form': form, 'posts': posts}
    return render(request, 'add_post.html', context)

@login_required(login_url='signin')
def refresh(request, user_provided_id):
    post = get_object_or_404(Post, user_provided_id=user_provided_id)
    platform = post.platform_id
    post_id = post.post_id

    if 'linkedin_username' in post:
        username = post.linkedin_username

    try:
        if platform == '1':
            scrapped_result = FacebookScrapper(user_provided_id, post)
        elif platform == '2':
            scrapped_result = TwitterScrapper(user_provided_id, post)
        elif platform == '3':
            scrapped_result = LinkedinScrapper(user_provided_id, username, post)

    except Exception as e:
        messages.info(request, f"Error from {platform}: {e}")
        return redirect('post_detail', post_id=post_id)
    
    scrapped_result.last_updated = datetime.datetime.now()
    scrapped_result.save()

    # Extract all comments and replies
    comments = [comment['comment_text'] for comment in post.comments]
    for comment in post.comments:
        comments.extend(reply['reply'] for reply in comment["replies"])
    sentiment_results = analyze_sentiments(comments)

    post.positive_score = sentiment_results["good"]
    post.neutral_score = sentiment_results["neutral"]
    post.bad_score = sentiment_results["bad"]
    post.save()

    messages.info(request, f"{post.username}'s post metrics with ID {post_id} updated successfully.")
    return redirect('post_detail', post_id=post_id)

@login_required(login_url='signin')
def deletePost(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    post.delete()
    messages.info(request, f"Successfully deleted {post.username}'s post with ID {post_id}.")
    return redirect('main')

@login_required(login_url='signin')
def editPost(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    posts = Post.objects.all().order_by('-last_updated')

    paginator = Paginator(posts, 50)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            post = Post.objects.filter(post_id=post_id).first()
            print(post)
            data = form.cleaned_data
            print(data)
            frequency = data['frequency']
            print(frequency)
            post.frequency = frequency
            print(post.frequency)
            post.save()

            messages.info(request, f"{post.username}'s post frequency with ID {post_id} updated successfully.")
            return redirect('post_detail', post_id=post_id)
    else:
        form = EditForm()

    context = {'form': form, 'posts': posts}
    return render(request, 'edit_post.html', context)

@login_required(login_url='signin')
def kill_switch(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    switch_status = request.GET.get('switch_status') == 'on'
    post.switch_status = switch_status
    post.save()
    
    context = {'post': post, 'switch_status': switch_status}
    return render(request, 'post_detail.html', context)

@login_required(login_url='signin')
def graphAnalysis(request, post_id):
    try:
        post = Post.objects.get(post_id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    def process_metrics(metrics):
        metrics = sorted(metrics, key=lambda x: parse_datetime(str(x['timestamp'])))
        values, timeframes, growth_rates = [], [], [0]
        for i in range(1, len(metrics)):
            old_value = metrics[i - 1]['value']
            new_value = metrics[i]['value']
            timestamp = metrics[i]['timestamp']
            growth_rate = round(((new_value - old_value) / old_value) * 100, 2) if old_value != 0 else 0
            growth_rates.append(growth_rate)
            values.append(new_value)
            timeframes.append(timestamp)
        return values, timeframes, growth_rates

    # Process likes
    likes_list, likes_timeframes, likes_growth_rates_list = process_metrics(post.likes)

    # Update likes growth rates in the database
    post.likes_growth_rates = [{'growth_rate': gr, 'timestamp': tf} for gr, tf in zip(likes_growth_rates_list, likes_timeframes)]
    post.save()

    # Process shares
    shares_list, shares_timeframes, shares_growth_rates_list = process_metrics(post.shares)

    # Update shares growth rates in the database
    post.shares_growth_rates = [{'growth_rate': gr, 'timestamp': tf} for gr, tf in zip(shares_growth_rates_list, shares_timeframes)]
    post.save()

    # Process number of comments
    num_comments_list, num_comments_timeframes, num_comments_growth_rates_list = process_metrics(post.num_comments)

    # Update number of comments growth rates in the database
    post.num_comments_growth_rates = [{'growth_rate': gr, 'timestamp': tf} for gr, tf in zip(num_comments_growth_rates_list, num_comments_timeframes)]
    post.save()

    # Sentiments
    positive_score = post.positive_score
    neutral_score = post.neutral_score
    bad_score = post.bad_score
    sentiment_analysis = [positive_score, neutral_score, bad_score]

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
        'sentiment_analysis': sentiment_analysis,
    }

    return JsonResponse(whole_data)

def help(request):
    return render(request, 'help.html')

def export_data_json(request):
    data = list(Post.objects.all().values())

    # Return data as JSON
    return JsonResponse(data, safe=False)

@login_required(login_url='signin')
def usersComparison(request):
    all_usernames = Post.objects.values_list('username', flat=True).distinct()

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

    posts_first_user = Post.objects.filter(username=first_name)
    posts_second_user = Post.objects.filter(username=second_name)

    def calculate_averages(posts):
        likes_sum, comments_sum, shares_sum, post_count = 0, 0, 0, 0
        for post in posts:
            if post.likes:
                likes_sum += post.likes[-1]['value']
            if post.num_comments:
                comments_sum += post.num_comments[-1]['value']
            if post.shares:
                shares_sum += post.shares[-1]['value']
            post_count += 1
        average_likes = likes_sum / post_count if post_count > 0 else 0
        average_comments = comments_sum / post_count if post_count > 0 else 0
        average_shares = shares_sum / post_count if post_count > 0 else 0
        return average_likes, average_comments, average_shares

    average_first_user_likes, average_first_user_comments, average_first_user_shares = calculate_averages(posts_first_user)
    average_second_user_likes, average_second_user_comments, average_second_user_shares = calculate_averages(posts_second_user)

    response_data = [
        {
            "user_name": first_name,
            "user_average_likes": average_first_user_likes,
            "user_average_comments": average_first_user_comments,
            "user_average_shares": average_first_user_shares
        },
        {
            "user_name": second_name,
            "user_average_likes": average_second_user_likes,
            "user_average_comments": average_second_user_comments,
            "user_average_shares": average_second_user_shares
        }
    ]

    return JsonResponse(response_data, safe=False)
