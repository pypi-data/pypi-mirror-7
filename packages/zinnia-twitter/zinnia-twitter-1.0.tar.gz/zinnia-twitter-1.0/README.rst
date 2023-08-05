==============
Zinnia-twitter
==============

Zinnia-twitter is a package putting your entries on `Twitter`_.

Installation
============

* Install the package on your system: ::

  $ pip install zinnia-twitter

  `Tweepy`_ will also be installed as a dependency.

* Register the ``'zinnia_twitter'`` in your ``INSTALLED_APPS`` after the
  ``'zinnia'`` application.

* Define these following settings with your credentials:

  * ``TWITTER_CONSUMER_KEY``
  * ``TWITTER_CONSUMER_SECRET``
  * ``TWITTER_ACCESS_KEY``
  * ``TWITTER_ACCESS_SECRET``

Note that the authentification for Twitter has changed since
September 2010. The actual authentification system is based on
oAuth. That’s why now you need to set these 4 settings. If you don’t know
how to get these information, follow this excellent tutorial at:

http://talkfast.org/2010/05/31/twitter-from-the-command-line-in-python-using-oauth/

You can replace the script mentionned in the step 3 of the tutorial by the
``get_twitter_access`` management command provided by the application, once
you have your CONSUMER_KEY and CONSUMER_SECRET.

Now in the admin, you can post an update containing your entry’s title and
the shortened URL of your entry.

.. _Twitter: https://twitter.com
.. _Tweepy: http://www.tweepy.org/
