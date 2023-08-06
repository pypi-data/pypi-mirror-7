===========
Mirador-Py
===========

The Mirador client to our Image Moderation API provides functionality for the simple moderation of image files and publically-accessible image URLs, along with integration into popular web and application frameworks. Basic usage::

    #!/usr/bin/env python
    from mirador import MiradorClient

    client = MiradorClient('your_api_key')

    for id, result in client.classify_files({ 'nsfw': 'nsfw.jpg', 'sfw': 'sfw.jpg'}):
        print "{id}: {safe}, {value}".format(**result.__dict__)

    # you can classify a single file or url
    result = client.classify_url('http://static.mirador.im/nsfw.jpg')
    other = client.classify_file('images/test.png')

    # if you have a buffer (e.g., from a file upload), you can work directly with that:
    res = client.classify_buffers(open('test.jpg', 'r').read(), open('mypix.jpg', 'r').read())

    # you can also classify data URIs
    data_uri = client.classify_data_uri(my_uri='data:image/jpg;base64,faefae3ro3irhreafer30024rfafe==')

    # kwargs lets you set IDs for request/results
    data_uri = client.classify_data_uri(another_example=request['data_uri'])

    print data_uri.id # "another_example"


Full Documentation/More Info
============================

For more information please see the github: http://github.com/mirador-cv/mirador-py
And our website: http://mirador.im/documentation
