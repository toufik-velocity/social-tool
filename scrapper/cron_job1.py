import main
import threading
import time
from rich import print as printc
from datetime import datetime, timedelta
from pymongo import MongoClient

class CronJob:
    def __init__(self):
        pass

    def check_time_difference(self, timestamp):
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

        return total_seconds

    def check_posts(self):
        # connect to the MongoDB database
        client = MongoClient('mongodb://localhost:27017/')
        db = client['SocialListening']
        collection = db['dashboard_post']
        pids = []
        posts = list(collection.find())
        client.close()
        
        # Check time difference and schedule scraping tasks if necessary
        printc("[yellow][+] Check for pids started. [/yellow]")

        for post in posts:
            timestamp = post['likes'][-1]['timestamp']
            total_seconds = self.check_time_difference(timestamp)
            if 'frequency' in post:
                if total_seconds >= post['frequency'] and post['switch_status'] == False:

                    pids.append(
                        {'platform_id': post['platform_id'], 'user_provided_id': post['user_provided_id']})
        print(pids)
        printc("[green][+] Check for pids completed. [/green]")

        if len(pids) != 0:
            printc("[green][+] There are some pids to scrap. [/green]\n")

        else:
            printc("[red][!] There are no pids to scrap. [/red]\n")

        return pids
    
    def pids_lister(self):
        pids = self.check_posts()

        if pids:        
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
            return temp_pids
        else:
            printc("[red][!] There is nothing to scrap. [/red]\n")
    
    def worker_thread(self, pid, temp_pid, threads):
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

        return threads

    def threading(self, threads):
        # Start worker threads
        printc("[yellow][+] Wait for all threads to complete. [/yellow]\n")
        for thread in threads:
            thread.join()

        printc("[yellow][+] Threading completed. [/yellow]\n")
        time.sleep(15) 

    def scrape_with_threading(self):
        temp_pids = self.pids_lister()
        if temp_pids:
            threads = []
            for temp_pid in temp_pids:
                for pid in temp_pid:
                    threads = self.worker_thread(pid, temp_pid, threads)
                
                threading(self, threads)

            printc("[green][+] Scrapping completed. [/green]\n")