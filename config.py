from dotenv import load_dotenv
load_dotenv()

import os

consumerKey = os.getenv('APIKey')
consumerKeySecret = os.getenv('APIKeySecret')
accessToken = os.getenv('accessToken')
accessTokenSecret = os.getenv('accessTokenSecret')
