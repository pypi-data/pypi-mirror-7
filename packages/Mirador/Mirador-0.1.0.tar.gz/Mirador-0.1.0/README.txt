===========
Mirador-Py
===========

The Mirador client to our Image Moderation API provides functionality for the simple moderation of image files and publically-accessible image URLs, along with integration into popular web and application frameworks. Basic usage::

    #!/usr/bin/env python
    from mirador import MiradorClient

    client = MiradorClient('your_api_key')
    for result in client.classify_files('my_pic.jpg', open('another_picture', 'rb')):
        print "{name}: {safe}, {value}".format(**result.__dict__)

Integrations
============

This package includes integrations into popular python frameworks and image management solutions. Please submit an issue on github or email support@mirador.im to request additional integrations or support with unique systems.
