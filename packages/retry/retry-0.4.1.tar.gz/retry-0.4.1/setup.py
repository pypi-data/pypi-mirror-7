"""
retry
-----

retry is a decorator for isolating retrying logic, with logging intergraton.


API
```

.. code:: python

    retry(exceptions=Exception, tries=float('inf'), delay=0, backoff=1)

various retrying logic can be achieved by combination of arguments.


Examples
````````

.. code:: python

    from retry import retry

    # Retry until succeed
    @retry()
    def make_trouble():
        ...

    # Retry on ZeroDivisionError, fail after 3 attmpts, sleep 2 seconds per
    # attmpt
    @retry(ZeroDivisionError, tries=3, delay=2)
    def make_trouble():
        ...

    # Retry on ValueError and TypeError, sleep 1, 2, 4, 8, etc.. seconds
    @retry((ValueError, TypeError), delay=1, backoff=2)
    def make_trouble():
        ...

    # If you enable logging, you can get warnings like 'ValueError, retrying in
    # 1 seconds'
    if __name__ == '__main__':
        import logging
        logging.basicConfig()
        make_trouble()

"""
from setuptools import setup


setup(
    name='retry',
    version='0.4.1',
    description='retry decorator',
    long_description=__doc__,
    packages=['retry'],
    license='Apache License 2.0',
    install_requires=[
        'decorator',
    ]
)
