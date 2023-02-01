# Most-Active-Posters-Reddit-Bot
Retrieves the most active users in a subreddit within a period of time.

## Most_Active_Posters.py
This script gets the most active users and sends their names as a PM to a specified user.  
The account that runs this script does not have to be a moderator in the subreddit.

## Most_Active_Posters_Flair_Updater.py
This script gets the most active users and assigns them flairs which are numbered based on their activity levels.  
The account that runs this script must be a moderator in the subreddit, and must have the permission to manage and assign flairs.

### Instructions
- Ensure you have Python installed on your system. You can download it here https://www.python.org/downloads/
- Install the PRAW package ```pip install praw```
- Create a Reddit (script) app at https://www.reddit.com/prefs/apps/ and get your keys
- Edit the praw.ini file with your details
- For the Most_Active_Posters.py file:
  - Open the python file and change the ```subreddit_name``` value to your desired subreddit.
  - Change the ```userName``` value to the user who is to receive the PM with the names.
- For the Most_Active_Posters_Flair_Updater.py file:
  - Open the python file and change the ```subreddit_name``` value to your desired subreddit.
- Run the script ```python Most_Active_Posters.py``` or ```python Most_Active_Posters_Flair_Updater.py```, based on whichever fulfils your requirements
