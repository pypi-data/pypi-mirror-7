=====
PARTY
=====

Description
===========
Lightweight client for the Artifactory API. Simplifies the gathering of artifact properties, and also the setting of custom properties on artifacts in Artifactory.

CI plugins for Artifactory aren't always flexible about setting specific metadata on uploaded artifacts. In addition, it can be cumbersome to programmatically retrieve an artifact's location (or properties on that artifact) in an automated fashion. Party serves this need as "glue" between your completed builds and beginning deployments.

Usage
=====
**Key Points**

* Ensure party.py is in your PYTHONPATH. The included example can be run like this: ``PYTHONPATH=$PYTHONPATH:.. python lookup.py``
* Ensure to change the search criteria ("file_props" in the example below).
* Configuration is pre-loaded from party_config.py, but can be overridden at runtime.
* Any properties returned from using a "find" or "get" method are assigned to the class instance.
* Wildcards can be used in properties passed in as search criteria, but is not recommended for fast performance.

**Example**

Example code (lookup.py) is available in the party/example directory. Here is a similar snippet:

::
    
    from party import *
    artifact = Party()
    file_props = {
        "build.number": 999,
        "rpm.version": "1.0.0.999",
        "build.name": "UI*"
    }

    result = artifact.find_artifact_by_properties(file_props)
    result = artifact.get_properties(artifact)

    for k in artifact.properties:
        for v in artifact.properties[k]:
            print "%s: %s" % (k, v)

Configuration
=============

Party class instances load in the values from ```party_config.py```. However, those values can be overridden directly in the file, or at runtime using:
::

    artifact = Party()
    artifact.CONFIG_KEY = "new value"

The following is a list of config keys (CONFIG_KEY above) and descriptions of their purposes:
::
    
    artifactory_url - Base URL to your Artifactory instance.
        search_prop - Artifactory API endpoint used for the property search.
        search_name - Artifactory API endpoint to access quick search.
           username - Username credential to use to connect to the Artifactory instance.
           password - Base64 encoded password credential used to connect to the Artifactory instance.
            headers - JSON (Python dict) of headers to send in the Artifactory queries. 

Methods
=======
* All methods return ```None``` if the query returns an empty result, and ``OK`` if there were results. Successfully retrieved values are accessible as members of the class instance. 
* When specifying multiple properties, all successfully found properties will become members of the class instance. Missing properties are discarded, unless all queried properties don't exist, in which case ```None``` is returned.

**find**

* **Description:** Find an artifact by filename.
* **Produces:** (String) Class instance members "uri" and "name".
* **Usage:** ``find(String)``
* **Sample Output:**

::
    
    {
        u'results': [ {
            u'uri': u'http://my-server/artifactory/api/storage/libs-snapshot-local/com/mycompany/api/my-artifact/1.0.0-SNAPSHOT/my-artifact-1.0.0.999-1.noarch.rpm'
        } ]
    }


**find_by_properties**

* **Description:** Find an artifact by its properties.
* **Produces:** (String) Class instance members "uri" and "name".
* **Usage:** ``find_by_properties(Dict)``. Any number of properties can be specified within the dict.
* **Sample Output:**

::

    {
        u'results': [ {
            u'uri': u'http://my-server/artifactory/api/storage/libs-snapshot-local/com/mycompany/api/my-artifact/1.0.0-SNAPSHOT/my-artifact-1.0.0.999-1.noarch.rpm'
        } ]
    }

**get_properties**

* **Description:** Get specific properties from an artifact.
* **Produces:** Class instance members of any found properties, referenced by specified keys.
* **Usage:** ``get_properties(String, Dict)``. Any number of properties can be specified within the dict. Designed to be used in conjunction with the find methods to produce the filename.
* **Sample Output:**

::

    {
        u'properties': { 
            u'build.number': [u'537'], 
            u'rpm.version': [u'4.2.1.537']
        }, 
        u'uri': u'http://my-server/artifactory/api/storage/libs-snapshot-local/com/mycompany/api/my-artifact/1.0.0-SNAPSHOT/my-artifact-1.0.0.999-1.noarch.rpm/'
    }

**set_properties**

* **Description:** Set specific properties on an artifact. **NOTE:** This will not set properties on your current class instance. Properties set using this method must be subsequently retrieved using the ``get_properties`` method.
* **Produces:** HTTP status code. Return code of 200 or 204 is successful.
* **Usage:** ``set_properties(String, Dict)``. Any number of properties can be specified within the dict. Please refer to http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html for a description of status codes.
* **Sample Output:**

::

    200

