.. image:: https://raw.githubusercontent.com/blacktop/shadow-server-api/master/doc/logo.png

shadow-server-api
*****************

.. |travisci| image:: https://travis-ci.org/blacktop/shadow-server-api.svg?branch=master
    :target: https://travis-ci.org/blacktop/shadow-server-api

.. |version| image:: https://badge.fury.io/py/shadow-server-api.png
    :target: http://badge.fury.io/py/shadow-server-api

.. |downloads| image:: https://pypip.in/d/shadow-server-api/badge.png
        :target: https://crate.io/shadow-server-api/requests/

.. |tip| image:: http://img.shields.io/gittip/blacktop.svg
        :target: https://www.gittip.com/blacktop/

Shadow Server - Binary Whitelist and MD5/SHA1 AV Service API

https://www.shadowserver.org

Installation
============
.. code-block:: bash

    $ pip install shadow-server-api


Usage
=====
MD5/SHA1 AV Service
-------------------
.. code-block:: python

    import json
    from shadowserver.shadow_server_api import ShadowServerApi

    ss = ShadowServerApi()

    response =  ss.get_av('039ea049f6d0f36f55ec064b3b371c46')
    print json.dumps(response, sort_keys=False, indent=4)


Output:
-------
.. code-block:: json

    {
        "sha1": "ada0f47d8a52d664a5548bf67aa4a28c1d7dbf15",
        "last_seen_date_utc": "2013-12-12 15:11:38",
        "file_type": "exe",
        "response_code": 200,
        "av": {
            "DrWeb": "BackDoor.Kuluoz.4",
            "FSecure": "Suspicious:W32/Malware!Online",
            "Clam": "PUA.Win32.Packer.Upx-53",
            "Symantec": "Trojan.Fakeavlock",
            "TrendMicro": "TROJ_SPNR.11LC13",
            "Avast": "Win32:Malware-gen",
            "GData": "Trojan.GenericKD.1449455",
            "Kaspersky": "Trojan-Downloader.Win32.Dofoil.rmy",
            "BitDefender": "Trojan.GenericKD.1449455",
            "McAfee": "RDN/Downloader.a!og",
            "Eset": "Win32/Kryptik.BQYU",
            "Avira": "TR/Crypt.ZPACK.Gen8",
            "Sunbelt": "Trojan.Win32.Dofoil.qtz",
            "K7": "Trojan ( 004912141 )",
            "Fortinet": "W32/DOFOIL.LF!tr",
            "Microsoft": "TrojanDownloader:Win32/Kuluoz.D",
            "AVG": "Generic_r.DHD",
            "K7GW": "Trojan ( 004912141 )",
            "Emsisoft": "Trojan.GenericKD.1449455",
            "QuickHeal": "TrojanDownloader.Kuluoz.aob",
            "Comodo": "UnclassifiedMalware"
        },
        "ssdeep": "",
        "first_seen_date_utc": "2013-12-12 15:11:38",
        "md5": "039ea049f6d0f36f55ec064b3b371c46"
    }


Binary Whitelist
================
.. code-block:: python

    import json
    from shadowserver.shadow_server_api import ShadowServerApi

    ss = ShadowServerApi()

    response =  ss.get_bintest('5e28284f9b5f9097640d58a73d38ad4c')
    print json.dumps(response, sort_keys=False, indent=4)


Output:
-------
.. code-block:: json

    {
        "response_code": 200,
        "results": {
            "os_mfg": "Microsoft Corporation",
            "fileversion": "5.1.2600.5512",
            "reference": "os_patches_all",
            "application_type": "exe",
            "filetimestamp": "04/14/2008 12:00:00",
            "sig_timestamp": "04/14/2008 02:07:47",
            "language_code": "1033",
            "source_version": "1.6",
            "dirname": "c:\\WINDOWS\\system32",
            "binary": "1",
            "source": "AppInfo",
            "product_version": "5.1.2600.5512",
            "mfg_name": "Microsoft Corporation",
            "filename": "notepad.exe",
            "os_version": "5.1",
            "sig_trustfile": "C:\\WINDOWS\\system32\\CatRoot\\{F750E6C3-38EE-11D1-85E5-00C04FC295EE}\\NT5.CAT",
            "filesize": "69120",
            "sha256": "865F34FE7BA81E9622DDBDFC511547D190367BBF3DAD21CEB6DA3EEC621044F5",
            "sha512": "CB7218CFEA8813AE8C7ACF6F7511AECBEB9D697986E0EB8538065BF9E3E9C6CED9C29270EB677F5ACF08D2E94B21018D8C4A376AA646FA73CE831FC87D448934",
            "product_name": "Microsoft Windows Operating System",
            "os_name": "Microsoft Windows XP Professional Service Pack 3 (build 2600)",
            "description": "Notepad",
            "trusted_signature": "1",
            "crc32": "877EA041",
            "bit": "32",
            "md5": "5E28284F9B5F9097640D58A73D38AD4C",
            "sha1": "7A90F8B051BC82CC9CADBCC9BA345CED02891A6C",
            "language": "English",
            "signer": "Microsoft Windows Component Publisher",
            "strongname_signed": "0"
        }
    }


Testing
-------

To run the tests:

    $ ./tests

Contributing
------------

1. Fork it.
2. Create a branch (`git checkout -b my_shadow_server_api`)
3. Commit your changes (`git commit -am "Added Something Cool"`)
4. Push to the branch (`git push origin my_shadow_server_api`)
5. Open a [Pull Request](https://github.com/blacktop/shadow-server-api/pulls)
6. Wait for me to figure out what the heck a pull request is...
