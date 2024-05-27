import cron_job1
import unittest
import time
from datetime import datetime


class CronJobTest(unittest.TestCase):
    # def test_scrap_post(self):
    #     # pids = [{'platform_id': '1', 'user_provided_id': 'pfbid0MSmNtvDLtKdZDJDi6rQ5jaFpjhhrZPFtHHaXx3GbuLY9KWgHRP9ZjwE4fsAvYg2Dl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02bPFGtoyeLQ6qA8q3ihXHty558Br3c5K9piFmHWcmEM3iVc5q2DMryDtZ1yvG1kfwl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0sCirjt3YqdwhQstJGtLh2VjPKdgcuqXP39DpafkgieTB4MWWyLbyWNmv4j5p5r5pl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0zTwnnLRBiuFc5JQHGfMtsdMB3YKMJcGNARuLmyABW7X39MYpUY68DgkpcVxF7Pjal'},
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02jM6aD8PeFXgn9xP5QnXPRVLWaJ5h4w7qqaj5ZvmX289VkwW7H5LwGQo8j9G5xVAml'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02i8z11nDEQ5npUEswrEZDXYsDeJbeFSfsKN6sJGMdtY4Sx9yAEcien9UomsvcQpdhl'},
                
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02rKGGLZoPxCYhkBy4MaxQjsAcFXswga8otZoGHZg1MuuAPrWCqMFnQEJtRBvVFV5l'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02BUw91P1dTCVftnrNUbMqwayf7bdrw4npEP1byUwJjpr5EcLiytPcFA96X7SxCaC8l'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0Tb7pzDux9zXF5nWWsWqRwz9jAFjdLyp5FehUk8CRj8q52dGb3MobxKbkssQTkDLxl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0g9zBpq1p6VkVrkJn2qhyG7vsCKtRpZLcBP55EsXKvKvAjtUGooZDTCHtwwW3HEMUl'},
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0Mxaay1ciVctvLpXNjDud3Li6YE1XqpNEk4GLp1tgT5nPSGLXK7vSvYiAfy9Fv1BRl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02gYhcYXTfvd1iiy6CdiALqmJtAsgbrbcfvLFEaRXVykZME2h2FAUoRGEEGdKw2QMRl'},
                
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid05J539QDGRXBkfPKJeUYxpUypGx58wCpJceUykFBFeUTuj5XBHaKsZFnHJkkkhY7Xl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0sNYuktLAZ5uxSax8zPoHpXM7ozxaepNXF4Pz1fAY9H7qkaoXMULn6Qr1Dkfq8pkBl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02q9aBCK6AiXbfXJADQVHe8HMZRSSa5mB2RkTvCC6Ed2KYz89UPKBUnZwaJn3rirgWl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02f5jcirH1eyKRLCgLskvBJdSbrFFwVpyktcWT8TaRuSGB9utEPqT4PeTn5g5c8FZ5l'},
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02NFj22qrGeuswFkmkfoEhtp6zRUjMnr5Ya6TxEBN7kaXH3iq26btrcaNF7dDvCTbDl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid035dWQM2kpoiqdxpzt6aprde36VgwVDRCkZLE2Y9d6mHDeEHvcFUvdCk7agQZWVf9xl'},
                
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0APvMARnjNdh4xVvT7wAbsLBKgC3XQwfESofHRPdnQH8R9XxnbPuTUgBhZXFMVqeEl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid0wjvDs5KJNT6oGLsvQcuC1pBFcrYqnwcY2pLP5cnbCzHNmjuF73eRYEXAGV7JzmZul'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid02o1wsrtjHoYxwyFU6jAPtMSKgDQQUqcNZexhmkQHjnsj3X42xuenQjoQR3RMX5UUTl'}, 
    #     #         {'platform_id': '1', 'user_provided_id': 'pfbid03wsnVXTjYkHZnxHFLCMVpHGs9iHDi4hfctN84jtvs6DZPVN3tkXT5F91LrQGXS8Pl'},]
    #     cron = cron_job1.CronJob()
    #     cron.scrape_with_threading()
    #     # Add your assertions here to validate the scraping process

    def test_check_time_difference(self):
        timestamp = datetime('2023-07-10T16:53:38.808+00:00')
        cron = cron_job1.CronJob()
        cron.check_time_difference(timestamp)
        # Add your assertions here to validate the check_time_difference method

    # Add more test methods for other functionalities if needed


if __name__ == '__main__':
    unittest.main()
