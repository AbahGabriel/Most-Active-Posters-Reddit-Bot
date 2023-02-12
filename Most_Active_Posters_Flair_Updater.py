import praw
import prawcore
import datetime
import os
import re

#Ensure that this bot is a moderator, or else it won't work

#Grabs Top N Posters of the Week and awards them the flair '#{num} Poster for Week {week}' based on their
#post frequency during the week.
def main():
    #File path
    path = "flairs.txt"

    #Go to subreddit
    reddit = praw.Reddit('MostActivePosters')
    subreddit_name = 'CelebsWithPetiteTits'
    subreddit = reddit.subreddit(subreddit_name)

    #Removes flairs from previous week's flair awardees
    clearFlairsFromPreviousHolders(subreddit)

    #Deletes flairs used for previous week
    deletePreviousFlairs(subreddit, reddit, path)
    
    #Retrieve all posts made within the past week
    lastWeekPosts = getPostsMadeWithinPastWeek(subreddit)

    #Get author of each post and assign them a numberOfPosts value
    authorsAndPosts = setPostNumberForEachAuthor(lastWeekPosts)

    #Filter out authors who currently have flairs
    authorsAndPosts = removeFlairedAuthors(authorsAndPosts, lastWeekPosts)

    #Sorts dictionary in descending order
    authorsAndPosts = sortDictionaryInDescendingOrder(authorsAndPosts)

    #Keeps top N Users
    authorsAndPosts = keepTopNPosters(authorsAndPosts)

    #Create N new flairs labelled: "#{num} Poster for Week {currentDay}"
    createdFlairs = createNewFlairs(subreddit)

    #Sets user flairs
    setUserFlairs(authorsAndPosts, createdFlairs, subreddit)

    #Saves the newly created flairs
    saveNewFlairs(path, createdFlairs)

def clearFlairsFromPreviousHolders(subreddit):
    userList = []

    for flair in subreddit.flair(limit=None):
        if "Poster for Week" in flair['flair_text']:
            userList.append(flair['user'])

    subreddit.flair.update(userList)

def deletePreviousFlairs(subreddit, reddit, path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return
    
    print("Deleting flairs from past week...")
    #Deletes flairs from subreddit
    with open(path, 'r') as openFile:
        for line in openFile: #Each line is a flair
            start = line.find("id") + 4  # + 4 to account for the 'id': prefix
            end = line.find(",", start) # Finds the next ',' from the given index
            flairId = line[start:end] # Gets the text in the index region
            flairId = flairId.strip().strip('\'') # Formats it to return the id

            try:
                subreddit.flair.templates.delete(flairId)
            except prawcore.exceptions.NotFound:
                continue

    #Clears file
    with open(path, 'r+') as openFile:
        openFile.truncate(0)

def getPostsMadeWithinPastWeek(subreddit):
    #All new posts in the subreddit
    allNewPosts = subreddit.new()

    timeRange = datetime.timedelta(weeks=1)
    filteredPosts = []
    for post in allNewPosts:
        #Checks if post was created between the current time and the past week
        post_creation_date = datetime.datetime.fromtimestamp(post.created_utc)
        if (post_creation_date > (datetime.datetime.today() - timeRange)):
            filteredPosts.append(post)
        else:
            break

    return filteredPosts

def setPostNumberForEachAuthor(lastWeekPosts):
    dictionary = {}

    print("Getting posts from past week...")
    #Counts number of posts for each author
    for post in lastWeekPosts:
        if post.author is not None:
            if post.author in dictionary:
                dictionary[post.author] += 1
            else:
                dictionary[post.author] = 1
    
    return dictionary

def removeFlairedAuthors(authorDictionary, lastWeekPosts):
    #Check if any author currently has a flair
    for post in lastWeekPosts:
        if post.author_flair_text == '':
            continue

        if post.author_flair_text is not None:
            try:
                del authorDictionary[post.author] #Remove if yes
            except KeyError: #Handles duplicate posters
                continue
        
    return authorDictionary
    
def sortDictionaryInDescendingOrder(dictionary):
    print("Sorting users based on post count...")
    #Sorts dictionary according to the values (x[1])
    dictionary = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)
    return dictionary

def keepTopNPosters(authorsAndPosts):
    N = 5 #Number of users to consider
    
    # Converts dict to tuple
    authorTuple = tuple(authorsAndPosts)
    
    # Get first N items in dictionary
    topNPosters = dict(list(authorTuple)[0: N]) 

    return topNPosters

def createNewFlairs(subreddit):
    print("Creating new flairs...")
    #Creates N new flairs that can only be assigned by moderators
    N = 5
    for i in range(1, N + 1):
        text = f'#{i} Poster for Week {datetime.date.today()}'
        text = re.sub("\..*$","",text)
        subreddit.flair.templates.add(text=text,
        allowable_content='text',
        mod_only=True,
        text_editable=False)
    
    #Tracks created flairs for future identification
    newFlairs = []
    for flair in subreddit.flair.templates:
        if "Poster for Week" in flair['text']:
            newFlairs.append(flair)
    newFlairs = sorted(newFlairs, key=lambda i: i['text'])

    return newFlairs

def setUserFlairs(authorsAndPosts, createdFlairs, subreddit):
    print("Setting flairs...")
    #Sets flairs for top 5 posters, in order
    i = 0
    for author in authorsAndPosts:
        if i > 5:
            break
        subreddit.flair.set(author, text=createdFlairs[i]['text'],flair_template_id=createdFlairs[i]['id'])
        i += 1

def saveNewFlairs(path, createdFlairs):
    if not os.path.exists(path):
        open(path, "w").close()

    for flair in createdFlairs:
        with open(path, 'a') as openFile:
            openFile.write(f'{flair}\n')

main()
