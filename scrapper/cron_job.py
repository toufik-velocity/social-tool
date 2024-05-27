import main
import time
import threading
from datetime import datetime, timedelta
from pymongo import MongoClient
from rich import print as printc

# connect to the MongoDB database
client = MongoClient('mongodb://localhost:27017/')
db = client['SocialListening']
collection = db['dashboard_post']

def checkPosts():
    pids = []
    posts = list(collection.find())

    printc("[yellow][+] Check for pids started. [/yellow]")

    for post in posts:
        timestamp = post['likes'][-1]['timestamp']
        current_time = datetime.now()
        time_difference = current_time - timestamp
        print(time_difference)

        time_duration = str(time_difference)
        # Split the time duration into days and hours:minutes:seconds
        time_parts = time_duration.split(", ")
        if len(time_parts)>1:
            days = int(time_parts[0].split()[0])
            time = time_parts[1]
        else:
            time = time_parts[0]
        # Split hours:minutes:seconds into separate components
        time_components = time.split(":")
        hours = int(time_components[0])
        minutes = int(time_components[1])

        # Split seconds into seconds and milliseconds
        seconds_with_milliseconds = float(time_components[2])
        seconds = int(seconds_with_milliseconds)
        milliseconds = int((seconds_with_milliseconds - seconds) * 1000)

        # Convert to timedelta
        if len(time_parts)>1:
            time_diff = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

        else:
            time_diff = timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

        # Convert the timedelta to the total number of seconds
        total_seconds = int(time_diff.total_seconds())
        
        if 'frequency' in post:
            if total_seconds >= post['frequency'] and post['switch_status'] == False:

                pids.append(
                    {'platform_id': post['platform_id'], 'user_provided_id': post['user_provided_id']})

    # pids = [{'platform_id': '1', 'user_provided_id': 'pfbid0MSmNtvDLtKdZDJDi6rQ5jaFpjhhrZPFtHHaXx3GbuLY9KWgHRP9ZjwE4fsAvYg2Dl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02bPFGtoyeLQ6qA8q3ihXHty558Br3c5K9piFmHWcmEM3iVc5q2DMryDtZ1yvG1kfwl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0sCirjt3YqdwhQstJGtLh2VjPKdgcuqXP39DpafkgieTB4MWWyLbyWNmv4j5p5r5pl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0zTwnnLRBiuFc5JQHGfMtsdMB3YKMJcGNARuLmyABW7X39MYpUY68DgkpcVxF7Pjal'},
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02jM6aD8PeFXgn9xP5QnXPRVLWaJ5h4w7qqaj5ZvmX289VkwW7H5LwGQo8j9G5xVAml'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02i8z11nDEQ5npUEswrEZDXYsDeJbeFSfsKN6sJGMdtY4Sx9yAEcien9UomsvcQpdhl'},
            
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02rKGGLZoPxCYhkBy4MaxQjsAcFXswga8otZoGHZg1MuuAPrWCqMFnQEJtRBvVFV5l'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02BUw91P1dTCVftnrNUbMqwayf7bdrw4npEP1byUwJjpr5EcLiytPcFA96X7SxCaC8l'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0Tb7pzDux9zXF5nWWsWqRwz9jAFjdLyp5FehUk8CRj8q52dGb3MobxKbkssQTkDLxl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0g9zBpq1p6VkVrkJn2qhyG7vsCKtRpZLcBP55EsXKvKvAjtUGooZDTCHtwwW3HEMUl'},
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0Mxaay1ciVctvLpXNjDud3Li6YE1XqpNEk4GLp1tgT5nPSGLXK7vSvYiAfy9Fv1BRl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02gYhcYXTfvd1iiy6CdiALqmJtAsgbrbcfvLFEaRXVykZME2h2FAUoRGEEGdKw2QMRl'},
            
    #         {'platform_id': '1', 'user_provided_id': 'pfbid05J539QDGRXBkfPKJeUYxpUypGx58wCpJceUykFBFeUTuj5XBHaKsZFnHJkkkhY7Xl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0sNYuktLAZ5uxSax8zPoHpXM7ozxaepNXF4Pz1fAY9H7qkaoXMULn6Qr1Dkfq8pkBl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02q9aBCK6AiXbfXJADQVHe8HMZRSSa5mB2RkTvCC6Ed2KYz89UPKBUnZwaJn3rirgWl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02f5jcirH1eyKRLCgLskvBJdSbrFFwVpyktcWT8TaRuSGB9utEPqT4PeTn5g5c8FZ5l'},
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02NFj22qrGeuswFkmkfoEhtp6zRUjMnr5Ya6TxEBN7kaXH3iq26btrcaNF7dDvCTbDl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid035dWQM2kpoiqdxpzt6aprde36VgwVDRCkZLE2Y9d6mHDeEHvcFUvdCk7agQZWVf9xl'},
            
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0APvMARnjNdh4xVvT7wAbsLBKgC3XQwfESofHRPdnQH8R9XxnbPuTUgBhZXFMVqeEl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid0wjvDs5KJNT6oGLsvQcuC1pBFcrYqnwcY2pLP5cnbCzHNmjuF73eRYEXAGV7JzmZul'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid02o1wsrtjHoYxwyFU6jAPtMSKgDQQUqcNZexhmkQHjnsj3X42xuenQjoQR3RMX5UUTl'}, 
    #         {'platform_id': '1', 'user_provided_id': 'pfbid03wsnVXTjYkHZnxHFLCMVpHGs9iHDi4hfctN84jtvs6DZPVN3tkXT5F91LrQGXS8Pl'},]
    print(pids)
    printc("[green][+] Check for pids completed. [/green]")

    if len(pids) != 0:
        printc("[green][+] There are some pids to scrap. [/green]\n")

    else:
        printc("[red][!] There are no pids to scrap. [/red]\n")

    return pids


def scrape_with_threading():
    pids = checkPosts()

    if pids:        
        threads = []
        temp_pids = []
        rem_pids = []
        temp_dict = {'1': [], '2': []}

        for pid in pids:   
            temp_dict[pid['platform_id']].append(pid)
                
        # Create sublists of length 3
        while len(temp_dict['2']) >= 2 and len(temp_dict['1']) >= 1:
            sublist = temp_dict['2'][:2] + temp_dict['1'][:1]
            temp_pids.append(sublist)
            del temp_dict['2'][:2]
            del temp_dict['1'][:1]

        # Check remaining elements in temp_dict['2']
        if len(temp_dict['2']) > 0:
            for pid in temp_dict['2']:
                rem_pids.append(pid)

                if len(rem_pids)==3:
                    temp_pids.append(rem_pids)
                    rem_pids = []


        # Check remaining elements in temp_dict['1']
        if len(temp_dict['1']) > 0:
            for pid in temp_dict['1']:
                rem_pids.append(pid)

                # if len(rem_pids)==3:
                temp_pids.append(rem_pids)
                rem_pids = []

        if rem_pids:
            temp_pids.append(rem_pids)
        printc(f"[yellow][!] The list of grouped temporary pids: [green]{temp_pids}[/green]. [/yellow]\n")

        # printc(f"[green][!] The list of grouped temporary pids: {list_temp_pids}. [/green]\n")

        for temp_pid in temp_pids:
            for pid in temp_pid:
                # Number of posts to scrape concurrently
                concurrent_posts = len(temp_pid)

                # Create a semaphore to limit concurrent thread access
                semaphore = threading.BoundedSemaphore(concurrent_posts)
                
                # Acquire the semaphore to limit concurrent threads
                semaphore.acquire()

                if pid['platform_id'] == '1':
                    thread = threading.Thread(target=main.facebook_scraping, args=(pid['user_provided_id'],))
                    printc(f"[green][+] Scrapping facebook with pid {pid['user_provided_id']}. [/green]")
                    
                if pid['platform_id'] == '2':
                    thread = threading.Thread(target=main.twitter_scrapping, args=(pid['user_provided_id'],))
                    printc(f"[green][+] Scrapping twitter with pid {pid['user_provided_id']}. [/green]")

                thread.start()
                printc("[yellow][+] Thread started. [/yellow]\n")
                threads.append(thread)

            printc("[yellow][+] Wait for all threads to complete. [/yellow]\n")
            for thread in threads:
                thread.join()

            printc("[yellow][+] Threading completed. [/yellow]\n")
            time.sleep(5)

        printc("[green][+] Scrapping completed. [/green]\n")
    else:
        printc("[red][!] There is nothing to scrap. [/red]\n")

    
while True:
    # Call the main function to start scraping
    scrape_with_threading()
    printc("[yellow][+] Sleeping for a minute before reloading. [/yellow]")
    time.sleep(60)
    printc("[yellow][+] Reloading. [/yellow]\n")
    continue 

