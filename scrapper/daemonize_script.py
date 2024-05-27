from daemonize import Daemonize
import os

# Function that will be executed as a daemon
def main():
    log_file = '../../cron_job.log'
    with open(log_file, 'a') as f:
        os.system('python3 /home/lab/Social_Listener/scrapper/cron_job.py >> {}'.format(f))

# Path to the PID file
pid = '/tmp/cron_job.pid'

# Create the daemon
daemon = Daemonize(app='cron_job', pid=pid, action=main)

# Start the daemon
daemon.start()
