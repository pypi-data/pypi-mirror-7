
.. image:: https://travis-ci.org/mrcrgl/django_distributed_task.svg
.. image:: https://readthedocs.org/projects/django-distributed-task/badge/?version=latest


================
Distributed Task
================

Distributed Task is a lightweight module for Django to delegate different jobs to worker processes.
It is useful for environments where celery is too overengeneered.

.. toctree::
   :maxdepth: 2

Docs are available at: http://django-distributed-task.readthedocs.org/en/latest/index.html
PyPi packaged: https://pypi.python.org/pypi/django_distributed_task


Installation
============

To use distributed_task, a `Django <https://www.djangoproject.com/>` installation is required.

Requirements
------------

It's well tested with following versions:

+-----------+---------------+---------------+
| Version   | Python        | Django        |
+-----------+---------------+---------------+
| 1.0       | 2.7, 3.3, 3.4 | 1.5, 1.6, 1.7 |
+-----------+---------------+---------------+

Get the code
------------

django_distributed_task package is available on ``pip``:

.. code-block:: bash

    pip install django_distributed_task


Register app in your Django settings.py
---------------------------------------

After install, register ``distributed_task`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        ...
        "distributed_task",
    )

And finally ``sync`` your database:

.. code-block:: bash

    ./manage.py syncdb distributed_task


Overview
========

In between of `celery <https://github.com/celery/celery>`, distributed_task is extremely lightweight.
We'd decided to keep it simple with less of flexibility but straight at the needs.
Just define for each method a `task`-method using the decorator and delay it at run time.

Use case
--------

The goal is to prevent "heavy" tasks to be executed between a web request and it's response.

Examples for those tasks are:

* Sending e-mails.
* Generation of pdf/csv/... files.
* Rendering of images, videos.


Usage
=====

The default call scheme is:
    Task.delay -> Broker -> Worker -> Execution


Tasks
-----

distributed_task will check in every installed app (``INSTALLED_APPS``) for a ``tasks.py`` file.

Define your first task
----------------------

Create a ``tasks.py`` file in your desired app of choice::

    from distributed_task import register_task

    @register_task
    def my_heavy_task_method():
        pass


Call your task
--------------

The decorator adds a ``delay`` method to your task. You can decide in runtime if you'd like to
execute the task delayed or immediately.

Execute delayed in a worker process::

    my_heavy_task_method.delay(*args, **kwargs)


Default method execution (bypasses task distribution)::

    my_heavy_task_method(*args, **kwargs)


Arguments
---------

You can pass all args/kwargs to the ``my_heavy_task_method.delay`` method as you would call it normally.
The serializer is also able to handle Django model instances but not QuerySets.

This works fine::

    instance = User.objects.first()

    my_heavy_task_method.delay('arg 1', user=instance, some_other_arg=False, some_float=12.5212)

Response / Return values
------------------------

Method return values are not available. Maybe in a further version.


Upcoming versions
=================

These features/changes are in plan:

Version 1.1
-----------

* enhance worker process handling
* worker support for cron execution
* worker daemon support
* worker multiprocessing support
* database broker support (for testing and those environments without RabbitMQ or other messaging system)
