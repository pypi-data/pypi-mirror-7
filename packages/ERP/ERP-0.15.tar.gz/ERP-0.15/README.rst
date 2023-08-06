===
ERP
===

ERO is resourse planning system. This is very early version not for using.

Package is being developed in general for modeling and expected to be used
as advanced task management solution at the current stage.

First beta will roll out late july and will contain all to work with
enterprise material and technical base. After beta release work over finance
component would be done.

Detailed documentation would appear in the "docs" directory with beta release.

Quick start
-----------

1. Add package apps to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'rest_framework',
        'enterprise',
        'planning',
    )

2. Include the polls URLconf in your project urls.py like this::

    url(r'^pm/', include('planning.urls')),
    url(r'^structure/', include('enterprise.urls')),
    url(r'^resource/$', planning.views.ResListView.as_view()),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/reg/$', 'enterprise.views.register'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

3. Add custom auth app to your project settings.py like this:

    AUTH_USER_MODEL = 'enterprise.CorpUser'

4. Run `python manage.py migrate` to create models.

5. Run 'django-admin.py collectstatic' to collect all js code.

5. Visit http://127.0.0.1:8000/ to get started.