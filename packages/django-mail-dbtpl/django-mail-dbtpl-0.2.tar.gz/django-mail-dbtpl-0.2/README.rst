=================
django-mail-dbtpl
=================

The application allows you to store email templates in the database. The application also allows you to edit templates in the database data using ``ckeditor``. More details about the settings available ``ckeditor <https://github.com/shaunsephton/django-ckeditor>`_.

Installing
==========
Install the application using pip.
::

    > pip install django-mail-dbtpl

Add application settings Django project
::

    INSTALLED_APPS = (
    ...
    'django_mail_dbtpl',
    ...
    )

Apply migration
::

    python ./manage.py migrate django_mail_dbtpl


Usage
=====
After installation, you must create a letter template in the database via the administration panel by url ``http://127.0.0.1:8000/admin/django_mail_dbtpl/emailtemplate/``, it is necessary for the template specify `` slug ``. `` slug `` will be used for both identifier template. The templates can be determined context variables `` {{var}} ``. For example, you create a template with `` slug = 'welcome.tpl' ``, `` subject = 'Welcome, {{username}}' ``, `` body = 'Welcome to the {{site}}.'. The following is the code that shows how to use the template stored in the database
::

    from django_mail_dbtpl.utils import EmailWrapper
    context = {
        'username': 'Example User',
        'site': 'example.com'
    }
    msg = EmailWrapper('welcome.tpl', context)
    msg.from_email = 'from_email@example.com'
    msg.to = ['to_email@example.com']
    msg.send()