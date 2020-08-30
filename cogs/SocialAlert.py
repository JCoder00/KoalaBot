#!/usr/bin/env python

"""
Koala Bot Cog prividing Social Feed updates
Commented using reStructuredText (reST)
TODO: - FB GraphAPI Wrapper
      - Page Access Tokens
      - Display top item in feed
      - similar structure for Instagram + Twitter

"""
# Futures

# Built-in/Generic Imports
import os
import time
import asyncio
import concurrent.futures

# Libs
import discord
import facebook
import tweepy
from discord.ext import commands
from dotenv import load_dotenv
from tweepy import StreamListener
import requests

# Own modules
import KoalaBot

# Constants
load_dotenv()


# Variables

class TwitterAPIHandler:
    """
    A wrapper to interact with the Twitter Streaming API
    """

    def __init__(self, client_id: str, client_secret: str, access_token: str, token_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.token_secret = token_secret
        self.api = self.authenticate()

    def authenticate(self):
        """
        Authenticates with Twitter using the tweepy handler
        :return: Twitter API object
        """
        auth = tweepy.OAuthHandler(self.client_id, self.client_secret)
        auth.set_access_token(self.access_token, self.token_secret)
        return tweepy.API(auth)


class TweetStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        return status.text

    def on_error(self, status_code):
        if status_code == 420:
            # Stops the stream
            return False


class SocialAlert(commands.Cog):
    """
        A discord.py cog for providing social feed updates from Facebook, Instagram and Twitter
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="twitterAdd", aliases='add_user_to_twitter_alert')
    @commands.check(KoalaBot.is_admin)
    async def add_user_to_twitter_alert(self, ctx, raw_channel_id, twitter_username=None):
        """

        :param ctx:
        :param raw_channel_id:
        :param twitter_username:
        :return:
        """
        pass
    @commands.Cog.listener()
    async def on_ready(self):
        """

        :return:
        """
        self.post_tweets()

    def post_tweets(self):
        my_stream_listener = TweetStreamListener()
        auth = TwitterAPIHandler("yeet", "me", "from", "here").authenticate()
        tweet_stream = tweepy.Stream(auth=auth, listener=my_stream_listener)
        current_text = tweet_stream.filter(follow=["12345"], is_async=True)
        tweet_embed = create_social_embed("twitter", "template_user", current_text)
        channel = self.bot.get_channel("channel_id")
        await channel.send(embed=tweet_embed)


def create_social_embed(platform, user_info, post_info):
    """
    Creates an embed for social notifications
    :param platform: Social platform
    :param user_info: User information from API calls
    :param post_info: Post information from API calls
    :return: Created embed
    """
    embed = discord.Embed
    embed.title = platform + "New post from" + user_info

    embed.description = post_info
    # TODO:Make it more fancy with icons etc

    return embed


class FacebookGraphAPIHandler:
    """
    A wrapper to interact with the Facebook GraphAPI
    """

    def __init__(self, client_id: str, client_secret: str, short_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.short_token = short_token
        self.oauth_token = self.get_new_facebook_oauth()
        self.graph = facebook.GraphAPI(self.oauth_token)

    def get_new_facebook_oauth(self):
        """
        Get a new long-lived access token from Facebook
        :return: New long-lived access token
        """
        access_token_url = "https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={}&client_secret={}&fb_exchange_token={}".format(
            self.client_id, self.client_secret, self.short_token)
        return requests.get(access_token_url).json()['access_token']

    def get_post_info(self, page_id):
        """
        Gets default fields for the most recent post on a page feed
        :param page_id: ID of the page
        :return: Dictionary with the post's data
        """
        return self.graph.get_connections(page_id, connection_name="feed", limit=1)

    def get_page_info(self, page_id):
        """
        Gets default fields (name and id) for a specified page
        :param page_id: ID of the page
        :return: Dictionary with the page's data
        """
        return self.graph.get_object(page_id)


def setup(bot: KoalaBot) -> None:
    """
    Load this cog to the KoalaBot.
    :param bot: the bot client for KoalaBot
    """
    bot.add_cog(SocialAlert(bot))
