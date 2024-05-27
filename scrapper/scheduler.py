import cron_job1
import time
from rich import print as printc

while True:
    # Call the main function to start scraping
    cron_job1.scrape_with_threading()
    printc("[yellow][+] Sleeping for a minute before reloading. [/yellow]")
    time.sleep(60) # Wait for 1 minute
    printc("[yellow][+] Reloading. [/yellow]\n")
    continue 