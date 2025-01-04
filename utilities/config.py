import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Fetch required environment variables
def get_env_variable(var_name):
    """Get the environment variable or raise an exception."""
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

#API keys
AI_DEVS_API_KEY = get_env_variable('AI_DEVS_API_KEY')
OPEN_AI_API_KEY = get_env_variable('OPEN_AI_API_KEY')

#Task specific variables
AI_DEVS_API_ENDPOINT = get_env_variable('AI_DEVS_API_ENDPOINT')

#S00E01
S00E01_DATA_URL = get_env_variable('S00E01_DATA_URL')

#S01E01
S01E01_TASK_URL = get_env_variable('S01E01_TASK_URL')
S01E01_TASK_USERNAME = get_env_variable('S01E01_TASK_USERNAME')
S01E01_TASK_PASSWORD = get_env_variable('S01E01_TASK_PASSWORD')

#S01E02
S01E02_TASK_URL = get_env_variable('S01E02_TASK_URL')

#S01E03
S01E03_TASK_URL = get_env_variable('S01E03_TASK_URL') + AI_DEVS_API_KEY + "/json.txt"
S01E03_REPORT_URL = get_env_variable('S01E03_REPORT_URL')

#S01E05
S01E05_TASK_URL = get_env_variable('S01E05_TASK_URL') + AI_DEVS_API_KEY + "/cenzura.txt"
S01E05_REPORT_URL = get_env_variable('S01E05_REPORT_URL')

#S02E01
S02E01_TASK_URL = get_env_variable('S02E01_TASK_URL')
S02E01_REPORT_URL = get_env_variable('S02E01_REPORT_URL')

#S02E03
S02E03_TASK_URL = get_env_variable('S02E03_TASK_URL') + AI_DEVS_API_KEY + "/robotid.json"
S02E03_REPORT_URL = get_env_variable('S02E03_REPORT_URL')

#S02E04
S02E04_TASK_URL = get_env_variable('S02E04_TASK_URL')
S02E04_REPORT_URL = get_env_variable('S02E04_REPORT_URL')

#S02E05
S02E05_TASK_URL = get_env_variable('S02E05_TASK_URL') + AI_DEVS_API_KEY + "/arxiv.txt"
S02E05_DATA_URL = get_env_variable('S02E05_DATA_URL')
S02E05_REPORT_URL = get_env_variable('S02E05_REPORT_URL')

#S03E01
S03E01_TASK_URL = get_env_variable('S03E01_TASK_URL')
S03E01_REPORT_URL = get_env_variable('S03E01_REPORT_URL')

#S03E02
S03E02_TASK_URL = get_env_variable('S03E02_TASK_URL')
S03E02_REPORT_URL = get_env_variable('S03E02_REPORT_URL')

#S03E03
S03E03_TASK_URL = get_env_variable('S03E03_TASK_URL')
S03E03_REPORT_URL = get_env_variable('S03E03_REPORT_URL')

