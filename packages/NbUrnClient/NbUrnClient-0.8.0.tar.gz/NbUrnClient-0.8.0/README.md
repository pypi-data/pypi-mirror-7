Python Client for the URN PID service by the National Library of Norway
=======================================================================

This is a library and a set of command line tools for communicating with the SOAP ID service available at the National Library of Norway.

For more information (in Norwegian) about the service:
* Regarding URN: http://www.nb.no/idtjeneste/about_urn.jsf
* Regarding the SOAP API: http://www.nb.no/idtjeneste/about_urn_webservice.jsf

Installation
------------

The library is available as [NbUrnClient](https://pypi.python.org/pypi/NbUrnClient) on PyPI.
To install it to your desired python environment: `pip install NbUrnClient`

The command line utilities are not included. As long as you have the NbUrnClient library installed, all you need to do is to download the **bin** and **config** directories and follow the instructions under **Configuration**.

Configuration
-------------

The **config** directory contains an example of the YAML config file used by the client (**config.yml.example**). Copy this to e.g. **config.yml** and replace the dummy entries with the information you have received from the National Library.

Command Line Tools
------------------

The **bin** directory contains a set of command line tools that make use of the library.

### Usage examples:
NB: Most of these examples (except `find_urn` and `find_urns_for_url`) require a valid user account.

To reserve the next available urn in some series, use `reserve_next_urn`:
```
./bin/reserve_next_urn --series-code urn:series:code
```

The service will return information about the newly generated URN.
To add a URL to the newly generated URN (where **foo** is the new URN adress returned from the previous step), use `add_url`:

```
./bin/add_url --urn foo --url http://www.someurl.com
```

You can add more than one URL to a URN. To register one of them as the default URL for a URN, use `set_default_url`:

```
./bin/set_default_url --urn foo --url http://www.someurl.com
```

You can combine the previous steps using `create_urn`:

```
./bin/create_urn --series-code urn:series:code --url http://www.someurl.com/
```

The service will return the created URN, with the specified URL registered and set as default.

You can request information about some previously registered URN using `find_urn`:

```
./bin/find_urn --urn foo
```

You can also request information for all URNs containing a specific URL with `find_urns_for_url`:

```
./bin/find_urns_for_url --url http://www.someurl.com
```

Library
-------
The **nb_urn_client** directory contains the library for communicating with the SOAP API.
It is a thin wrapper around the SOAP API calls. To see how it's used, take a look at the commands in the **bin** directory.

### Library usage example:
The following example makes use of the library to do more or less the same as in the command line tools examples:

```python
import nb_urn_client

# Instantiate a client with some config file
c = nb_urn_client.NbUrnClient(config_file="config.yml")

# You need to login first
c.login()

# Reserve the next available URN in the given series
new_urn = c.reserve_next_urn('urn:series:code')

# Register some valid URL for the newly created URN
c.add_url(new_urn.URN, "http://www.someurl.com/")

# Register another URL for the same URN
c.add_url(new_urn.URN, "http://www.someotherurl.com/")

# Set one of the registered URLs to be the default URL
c.set_default_url(new_urn.URN, "http://www.someurl.com/")

####################################################
# ALTERNATIVE: Using create_urn:
# new_urn = c.create_urn('urn:series:code', 'http://www.someurl.com/')
# c.add_url(new_urn.URN, 'http://www.someotherurl.com/')
####################################################

# Retrieve the URN you just created and have a look
print c.find_urn(new_urn.URN)

# Retrieve all URNs containing some URL and have a look
print c.find_urns_for_url("http://www.someurl.org")

# Logout when you're done
c.logout()

```

Dependencies
------------

* [suds 0.4](https://fedorahosted.org/suds/)
* [PyYAML](https://pypi.python.org/pypi/PyYAML)
