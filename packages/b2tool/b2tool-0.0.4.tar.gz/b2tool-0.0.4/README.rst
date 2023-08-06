======
b2tool
======

**bbtool is a command line tool to manage BitBucket**

List of commands and --options
______________________________

* auth
    * login
        * --username
        * --password

* pullrequest
   *__required options for all__*
    --owner *Organization or account on Bitbucket* 

    --repo *Repository to connect*


  * listall
  * oldest

    --id True or False

    --branch True or False

  * accept

    --id Integer

    --message String



How to use 
__________

`Commands`

::

$ b2tool command options


**Authenticate on bitbucket**
::

$ b2tool auth login --username jesuejunior --password abc123

**List all pull requests**

::

$ b2tool pullrequest listall --owner jesuejunior --repo projectA

**List oldest pull requests with ID and branch**
::

$ b2tool pullrequest oldest --owner jesuejunior --repo projectA


**Print only id of oldest pull requests**
::

$ b2tool pullrequest oldest --owner jesuejunior --repo projectA  --id True

**Print only branch of oldest pull requests**
::

$ b2tool pullrequest oldest --owner jesuejunior --repo projectA  --branch True

**Accept pull request with id 100**
::

$ b2tool pullrequest accept --owner jesuejunior --repo projectA  --id 100 --message 'Accept this pull request ok'