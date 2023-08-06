django-grunt
============

Managing Grunt with runserver and Grunt initialization for your project.
Inspired to [Brandon Konkle's post](http://lincolnloop.com/blog/simplifying-your-django-frontend-tasks-grunt/)

Installation
----------
From command line

```
pip install grunt-django
```

In your settings.py:

```python
INSTALLED_APPS = (
    ...,
    'grunt'
)
```
optional:
```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
GRUNTFILE_ROOT = os.path.join(BASE_DIR, 'MY_GRUNTFILE_DIR')
```

Usage 
----
django-grunt provide 2 management commands:

1. 
```
manage.py gruntinit
``` 
which creates a package.json and Gruntfile.js

2.
```
manage.py gruntserver
``` 
Run this command instead of ```manage.py runserver``` for running django server along with grunt. This is helpful when you use livereload and watch.



