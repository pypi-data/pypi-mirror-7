# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import patch


class TestSocial(BotTestCase):

    config = dict(
        includes=['irc3.plugins.social'],
        twitter=dict(key='', secret='', token='', token_secret=''),
    )

    def test_get_conn(self):
        bot = self.callFTU()
        conn = bot.get_social_connection(network='twitter')
        self.assertTrue(hasattr(conn, 'conn'))

    def test_conns(self):
        bot = self.callFTU()
        plugin = bot.get_plugin('irc3.plugins.social.Social')
        self.assertIn('twitter', plugin.conns)

    @patch('twitter.api.TwitterCall.__call__', return_value=dict(id='yy'))
    def test_tweet(self, c):
        bot = self.callFTU()
        bot.dispatch(':bar!a@b PRIVMSG irc3 :!tweet yo')
        self.assertSent(['PRIVMSG bar :twitter success'])

        bot.dispatch(':bar!a@b PRIVMSG irc3 :!tweet --net=twitter yo')
        self.assertSent(['PRIVMSG bar :twitter success'])

        bot.dispatch(':bar!a@b PRIVMSG irc3 :!tweet --net=tw yo')
        self.assertSent(['PRIVMSG bar :tw is an invalid network. Use twitter'])

    @patch('twitter.api.TwitterCall.__call__', return_value=dict(error='fail'))
    def test_tweet_fail(self, c):
        bot = self.callFTU()
        bot.dispatch(':bar!a@b PRIVMSG irc3 :!tweet yo')
        self.assertSent(['PRIVMSG bar :twitter fail'])

    @patch('twitter.api.TwitterCall.__call__',
           return_value=dict(id='yy', text='yo!',
                             user=dict(screen_name='foo')))
    def test_retweet(self, c):
        bot = self.callFTU()
        bot.dispatch(':bar!a@b PRIVMSG irc3 :!retweet 123')
        self.assertSent(['PRIVMSG bar :@foo: yo!'])

        bot.dispatch(':bar!a@b PRIVMSG irc3 :!retweet --net=twitter 123')
        self.assertSent(['PRIVMSG bar :@foo: yo!'])

        bot.dispatch(':bar!a@b PRIVMSG irc3 :!retweet --net=tw 123')
        self.assertSent(['PRIVMSG bar :tw is an invalid network. Use twitter'])

    @patch('twitter.api.TwitterCall.__call__', return_value='fail')
    def test_retweet_fail(self, c):
        bot = self.callFTU()
        bot.dispatch(':bar!a@b PRIVMSG irc3 :!retweet 123')
        self.assertSent(['PRIVMSG bar :twitter: fail'])

    @patch('twitter.api.TwitterCall.__call__',
           return_value=dict(statuses=['blah']))
    def test_search(self, c):
        bot = self.callFTU()
        self.assertTrue(bot.search_tweets(q='foo'), ['blah'])

    @patch('twitter.api.TwitterCall.__call__',
           side_effect=KeyError())
    def test_search_raise(self, c):
        bot = self.callFTU()
        self.assertEqual(bot.search_tweets(q='foo'), [])
