import praw
import re
import wget
import tweepy
import time

def main():

	#set directory image downloads from subreddit
	cdir = input('Enter a directory to save images in: ')

	#create list to iterate titles
	d = []

	#create function that scrapes from subreddit 'soccer' 
	def scrape_soccer(cdir, d):

		# set default # of posts
		num_of_posts=3

		# setup praw reddit object and subreddit 
		my_client_id = 'my_client_id'
		my_client_secret = 'my_client_secret'
		my_user_agent = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64):app_version1.0 (by /u/user))'
		reddit = praw.Reddit(client_id=my_client_id, client_secret=my_client_secret, user_agent=my_user_agent)
		soccer_rising = reddit.subreddit('soccer').rising(limit=num_of_posts)

	    #keywords to check against in post strings to find and capture images
		check_words = ['i.imgur.com',  'jpg', 'png', 'gif', 'gfycat.com', 'webm',]

		#display attempt to post for user
		print('Attempting to post...')

	    #for loop on each post rising in soccer sub
		for submission in soccer_rising:
			title = submission.title
			url = submission.url
			has_image = False
			image_path = 'none'

			# if/else to ensure not re-posting same post
			if title not in d:
				#grabs any image files on the url
				has_domain = any(string in url for string in check_words)
				if has_domain:
					wget.download(url, cdir + "\\" + ''.join(url.split('/')[-1:]))
					has_image = True
					image_path = cdir + '\\' + ''.join(url.split('/')[-1:])
				# append title to list 'd' to ensure it doesn't repost
				d.append(title)
				# run function to tweet out scraped data from reddit
				tweetIt(title, url, image_path)
			
	#create function for posting fed information to twitter
	def tweetIt(title, url, image):

		#twitter API credentials for posting
		consumer_key = 'consumer_key'
		consumer_secret = 'consumer_secret'
		access_token = 'access_token'
		access_secret = 'access_secret'
		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_secret)
		api = tweepy.API(auth)

		#create title + url string for posting
		title_URL = title + ' ' + url

		try:
			# checks character lengths to ensure twitter post-able
			if (len(title) + len(url)) < 280:
				# checks for image attachment
				if image == 'none':
					#ignores 'Daily' posts 
					if re.search(r'Daily', title):
						pass
					#ignores i.reddit URLs from posting
					elif re.search(r'i.reddit',url):
						api.update_status(title)
						print('Post successful')
					else:
						api.update_status(title_URL)
						print('Post successful')
				elif re.search(r'Daily', title):
					pass
				elif re.search(r'i.reddit', url):
					api.update_with_media(image, title)
					print('Post successful')
				else:
					api.update_with_media(image, title_URL)
					print('Post successful')
			elif len(title) < 280:
				if image == 'none':
					api.update_status(title)
					print('Post successful')
				api.update_with_media(image, title)
				print('Post successful.')
			else:
				pass
		except:
			pass

	#continuous loop that runs every 6min
	while True:
		# runs function to again scrape reddit and then post on twitter
		scrape_soccer(cdir, d)

		#sleeps loop for 6min before attempting another post
		time.sleep(900)	


if __name__ == '__main__':
	main()