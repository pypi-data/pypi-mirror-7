Welcome
*******

Django visits is to be used as a hit-counter application for Django-powered web apps.

You have two ways of how to use this app; first is to count requested urls (CounterMiddleware), the second is to count object visits (aka models)

Configuration
*************

You settings file should contain the following settings 

* MIN_TIME_BETWEEN_VISITS: (number)  the minimum allowed time between visits for the user to update counter
* IGNORE_URLS: (list) urls to ignore e.g. static urls etc. **NOTE** : only ignores by not incrementing the hit-counter for the request whose META.PATH_INFO starts with any string in this list. The visit is still logged though. Same thing happnes for IGNORE_USER_AGENTS and BOTS_USER_AGENTS settings below.
* IGNORE_USER_AGENTS: (list) this is used to define what user agents to ignore. Regexes are supported
* BOTS_USER_AGENTS: (list) this is used to define whether user is real or bot is user by BotVisitorMiddleware. Regexes are supported
* REQUEST_FIELDS_FOR_HASH: (list) used to generate unique identifier for visitor
* URI_WITH_GET_PARAMS: (bool) use get params to identify diferents uris
* VISITS_OBJECTS_AS_COUNTERS: (bool) enable or disable the behavior of visits objects as counters (on False, every diferent visits is counted in a diferent object)

BOTS_USER_AGENTS by default will have the following values

::

    [
        "Teoma", "alexa", "froogle", "Gigabot", "inktomi", "looksmart", "URL_Spider_SQL", "Firefly",
        "NationalDirectory", "Ask Jeeves", "TECNOSEEK", "InfoSeek", "WebFindBot", "girafabot", "crawler",
        "www.galaxy.com", "Googlebot", "Googlebot/2.1", "Google", "Webmaster", "Scooter", "James Bond",
        "Slurp", "msnbot", "appie", "FAST", "WebBug", "Spade", "ZyBorg", "rabaz", "Baiduspider",
        "Feedfetcher-Google", "TechnoratiSnoop", "Rankivabot", "Mediapartners-Google", "Sogou web spider",
        "WebAlta Crawler", "MJ12bot", "Yandex/", "YaDirectBot", "StackRambler", "DotBot", "dotbot"
    ]

Usage
*****

* Add visits to INSTALLED_APPS

::

	INSTALLED_APPS = (
	    # ...
	    "visits",
	)

* If you want to filter some type of user agents you can define IGNORE_USER_AGENTS in your settings.py

::

    IGNORE_USER_AGENTS = ["Wget/", "curl/"]


* If you want to filter bots from real users then in MIDDLEWARE_CLASSES set 

::

	MIDDLEWARE_CLASSES = (
	    # ...
	    "visits.middleware.BotVisitorMiddleware",
	)

* If you want to count visits automatically per url the you should add CounterMiddleware to MIDDLEWARE_CLASSES

::

	MIDDLEWARE_CLASSES = (
	    # ...
	    "visits.middleware.CounterMiddleware",
	)

* If you want to count visits automatically per url with get params you should add URI_WITH_GET_PARAMS=True to your settings.py

* If you want count url visit manually you can do it the way below

::

	from visits.models import Visits

	def some_object_view(request, pk):
	    Visit.objects.add_uri_visit(request, request.META["PATH_INFO"], APP_LABEL)
	    #...
	    #...

* If you want count visits per object then it's similar to the example above

::

	from visits.models import Visits

	def some_object_view(request, pk):
	    some_obj = get_object_or_404(SOME_MODEL, pk=pk)
	    Visit.objects.add_object_visit(request, obj=some_obj)
	    #...
	    #...

* From inside of a template you can get

 * object visits using get_visits

 * url visits using get_visits templatetag

::

	{% load visits_tags %}

	{% get_visits some_model_instance as visits %}
	{% get_visits some_request_instance as visits %}
	{% get_visits some_uri_regex as visits %}

Note: to get uri visits using get_visits templatetag you should add the following to TEMPLATE_CONTEXT_PROCESSORS

::

    TEMPLATE_CONTEXT_PROCESSORS = (
        #...
        "visits.context_processors.request_meta",
    )

Have fun!
