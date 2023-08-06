=====
Django Absolute Url Template Tag
=====

Absolute Url is an app for creating absolute urls in Django templates. It works like built-in Django ``url`` template tag but with absolute urls.

Installation
-----------

Install using PIP

``pip install django-absoluteurl``

Add "absoluteurl" to your INSTALLED_APPS setting like this:

	INSTALLED_APPS = (
		...
		'absoluteurl',
	)


Usage
-----------

First load it in Django template and use it as a tag.

	{% load absoluteurl %}

	This is simplest example:
	{% absoluteurl 'name_for_your_url' %}

	This is an absolute url for some object:
	{% absoluteurl 'your_namespace:your_view' some_id=some_object.id %}

	You can also use it with 'as' form:
	{% absoluteurl 'your_namespace:your_view' some_id=some_object.id as abs_url %}
	{{ abs_url }}


Credits
-------------
Created by Bartosz Gryszko, 2014
MIT License