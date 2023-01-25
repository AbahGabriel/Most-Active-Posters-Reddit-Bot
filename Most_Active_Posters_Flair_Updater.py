import praw
from prawcore.exceptions import Forbidden
import datetime
import os
import re

#  Connects to Reddit's API and creates a Reddit object
#  which allows me to perform various actions
reddit = praw.Reddit('MostActivePosters')

#Gets info
subreddit_name = input("Enter subreddit name: ")

#Creates subreddit instance of specified subreddit
subreddit = reddit.subreddit(subreddit_name)

#Retrieves all new posts from subreddit
posts = subreddit.new()
timeRange = datetime.timedelta(days=7)
filteredPosts = []
for post in posts:
    #Checks if post was created between the current time and the specified range
    post_creation_date = datetime.datetime.fromtimestamp(post.created_utc)
    if (post_creation_date > (datetime.datetime.today() - timeRange)):
        filteredPosts.append(post)
    else:
        break

#Keeps track of how many posts each user made within the specified range
dictionary = {}

#Tries to filter out users with flairs
try:
    flairsText = []
    flairs = []
    linkFlairs = []

    #Retrieves all user flairs
    for flair in subreddit.flair.templates:
        flairsText.append(flair['text'])
        flairs.append(flair)

    #Retrieves all post flairs
    for flair in subreddit.flair.link_templates:
        linkFlairs.append(flair)

    for post in filteredPosts:
        if post.author_flair_text not in flairsText:
            dictionary[post.author] = []

    #Uses list to keep track of all user's posts
    for post in filteredPosts:
        for key in dictionary:
            if (post.author == key):
                dictionary[key].append(post)

#Default approach where all users are considered
except Forbidden:

    for post in filteredPosts:
        dictionary[post.author] = []

    #Uses list to keep track of all user's posts
    for post in filteredPosts:
        for key in dictionary:
            if (post.author == key):
                dictionary[key].append(post)

#Deletes flairs from previous week
filename = "C:\\Users\\Gabriel\\source\\repos\\API_Practice\\Top_Posters_Bot\\topposters.txt"
redditors = []
flairs = []
if os.path.exists(filename) == True:
    with open(filename, 'r') as f:
        if "," in f:
            for line in f:
                line = line.split(',')
                flairs.append(line[1])

            for flair in flairs:
                subreddit.flair.templates.delete(flair['id'])
        else:
            for line in f:
                subreddit.flair.delete(line)

        #Clears file
        open(filename, "w").truncate(0)
else:
    #Creates file
    open(filename, "w").close()


#Creates weekly flairs
newFlairs = []
try:
    for i in range(1, 6):
        text = f'#{i} Poster for Week {datetime.datetime.today()}'
        text = re.sub("\..*$","",text)
        subreddit.flair.templates.add(text=text,
        allowable_content='text',
        mod_only=True,
        text_editable=False)

    #Tracks created flairs for future identification
    for flair in subreddit.flair.templates:
        if "Poster for Week" in flair['text']:
            newFlairs.append(flair)
    newFlairs.sort(key=lambda x: x['text'], reverse=False)

except Forbidden:
    print("Bot does not have authority to create flairs.")

#Prints out users and the number of their posts
sortedDict = dict(sorted(dictionary.items(), key=lambda item: len(item[1]), reverse=True))
topposters = ""
num = 1
for key in sortedDict:
    if num <= 5:
        try:
            try:
                #Sets flairs of corresponding users
                if len(newFlairs) != 0:
                    text = f'#{i} Poster for Week {datetime.datetime.today()}'
                    text = re.sub("\..*$","",text)
                    subreddit.flair.set(f"{key.name}", text=text,flair_template_id=newFlairs[num]['id'])
            except Forbidden:
                print("Bot does not have authority to set flairs.")

            topposters += f"{num}. {key.name}: {len(dictionary[key])} posts\n\n"
            #Stores names and ids in file to be deleted in the next week
            with open(filename, 'a') as f:
                if len(newFlairs) != 0:
                    f.write(f"{key},{newFlairs[num]}\n")
                else:
                    f.write(f"{key}\n")

                num += 1
        except AttributeError:
            print("Invalid user. Skipping.")
    else:
        break
    
if len(linkFlairs) != 0:
    subreddit.submit(title="Top Posters Of The Week",selftext=topposters,flair_id=linkFlairs[0]['id'])
else:
    subreddit.submit(title="Top Posters Of The Week",selftext=topposters)

""" subreddit = reddit.subreddit("RandomTest123")

 Deletes flairs based on id
for flair in subreddit.flair.templates:
    subreddit.flair.templates.delete(flair['id'])

    for flair in flairs:
                subreddit.flair.templates.delete(flair['id'])

 Removes flair from user
for post in subreddit.new():
    redditor = post.author
    subreddit.flair.delete(redditor)

for flair in subreddit.flair.templates:
    print(flair['text']) """


exit()
