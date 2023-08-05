import os
from dotenv import load_dotenv


load_dotenv()

DEBUG = os.getenv("DEBUG") is not None
DAY_DURATION_SECONDS = os.getenv("DAY_DURATION_SECONDS", 300)
NIGHT_DURATION_SECONDS = os.getenv("NIGHT_DURATION_SECONDS", 120)
