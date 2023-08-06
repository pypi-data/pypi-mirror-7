Dynamo3
=======
:Build: |build|_ |coverage|_
:0.2 Build: |build-0.2|_ |coverage-0.2|_
:Downloads: http://pypi.python.org/pypi/dynamo3
:Source: https://github.com/stevearc/dynamo3

.. |build| image:: https://travis-ci.org/stevearc/dynamo3.png?branch=master
.. _build: https://travis-ci.org/stevearc/dynamo3
.. |coverage| image:: https://coveralls.io/repos/stevearc/dynamo3/badge.png?branch=master
.. _coverage: https://coveralls.io/r/stevearc/dynamo3?branch=master

.. |build-0.2| image:: https://travis-ci.org/stevearc/dynamo3.png?branch=0.2
.. _build-0.2: https://travis-ci.org/stevearc/dynamo3
.. |coverage-0.2| image:: https://coveralls.io/repos/stevearc/dynamo3/badge.png?branch=0.2
.. _coverage-0.2: https://coveralls.io/r/stevearc/dynamo3?branch=0.2

This is a stop-gap measure while `boto3 <http://github.com/boto/boto3>`_ is
under development. I have kept the API mostly similar to boto (with a few
improvements). This should only be used if you need to connect to DynamoDB
using Python 3. It was created for `dql <http://github.com/mathcamp/dql>`_ and
`flywheel <http://github.com/mathcamp/flywheel>`_.


Changelog
=========
0.2.0
-----
* Feature: More expressive 'expected' conditionals
* Feature: Queries can filter on non-indexed fields
* Feature: Filter constraints may be OR'd together
Features thanks to DynamoDB upgrades: http://aws.amazon.com/blogs/aws/improved-queries-and-updates-for-dynamodb/

0.1.3
-----
* Bug fix: sometimes crash after deleting table
* Bug fix: DynamoDB Local nose plugin fails

0.1.2
-----
* Bug fix: serializing ints fails

0.1.1
-----
* Feature: Allow ``access_key`` and ``secret_key`` to be passed to the ``DynamoDBConnection.connect_to_*`` methods

0.1.0
-----
* First public release


