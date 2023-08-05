django-deploy
=============

Management command to automate deployment of django project using
distutils/setuptools.

TL;DR
=====

I used to define set of actions to be run after `git pull` to update my project
environment in various provisioning/deployment tools. However, since most of
these actions were just `manage.py` commands and since I've started to use setup
script I wanted to define these actions right there.

What this app does
------------------

Run sequence of management commands or any python callable right after project
app is installed or updated. It's intended to be used with setup script, but
can be also run separately.

What this app does not
----------------------

Restarts http server, database or other services. Although one can define tasks
which does one of these *root tasks*, this app isn't intended to do so. It's
left to other provisioning/deployment tools like Fabric, Salt or Ansible.

Usage
=====

1. Install `django-deploy-setup` and add it into your requirements.

2. Add `django_deploy` to your INSTALLED_APPS.

3. Next step depends whether your project uses `setup.py` or not:

With ``setup.py``
-----------------

Add custom install command to `cmdclass` argument in your setup.py:

```python
from django_deploy.setup import DjangoInstall as install

setup(
    ...
    cmdclass={'install': install},
)
```

`DjangoInstall` will call `deploy` management command after regular install.

*Please note:* `DJANGO_SETTINGS_MODULE` environment variable must be defined
before running `python setup.py install` when using `DjangoInstall` command.

### Problem with `install_requires`

This approach has one major flaw. In case you specify your
project requirements using `install_requires` keyword, you won't be able to
import `django_deploy` module during initial install.

One possible solution is add following import statement and install
application twice. Updates will work just fine:

```python
try:
    from django_deploy.setup import DjangoInstall as install
except ImportError:
    from distutils.command.install import install
```


Without ``setup.py``
--------------------

Simply call `manage.py deploy` after updating codebase and
installing requirements.


Default deployment tasks
========================

By default, `deploy` command will run following commands:

1. `syncdb` (if you're using Django < 1.7)
2. `migrate` (if your're using south or Django > 1.7)
3. `collectstatic` (if you're using `django.contrib.staticfiles`)
4. `compilemessages` (if you're using internationalization, `I18N = True`)

Custom deployment tasks
=======================

If you want to run custom deployment tasks, create `deploy.py` file somewhere
in your project directory and set `DEPLOY_TASKS` in settings as dotted path:

```python
DEPLOY_TASKS = 'project_name.deploy`
```

Next, create variable `tasks` as a list of `Task` instances:

```python
# project_name/deploy.py

tasks = (
    Task('syncdb', interactive=False),
    Task('collectstatic', interactive=False),
    Task('compilemessages'),
    Task('custom_management_command'),
)
```

Task definition
---------------

To define task simply pass command_name, args and kwargs as you would for
`django.core.management.call_command`.

```python
Task('syncdb', interactive=False)
```

is the same as:

```python
call_command('syncdb', interactive=False)
```

The difference is, that command defined via `Task` is executed using
`run` method.

Custom callable
---------------

If you want to use custom callable instead of default ``call_command``, pass
``custom_callable`` keyword argument:

```python
Task(custom_callable=my_command, kwarg=42)
```

Licence
=======

MIT
