dir2json
========

This tool creates a json tree structure from the file hierarchy of a directory.

usage
::

    dir2json --pretty test/

in a directory like this
::

    test
    ├── bar
    │   └── symlink.png -> ../foo/test.png
    └── foo
        ├── test.jpg
        └── test.pn

Yields the following json output
::
    
    {
        "type": "directory", 
        "path": "", 
        "index": [
            {
                "type": "directory", 
                "path": "foo", 
                "index": [
                    {
                        "type": "image/jpeg", 
                        "path": "foo/test.jpg"
                    }, 
                    {
                        "type": "image/png", 
                        "path": "foo/test.png"
                    }
                ]
            }, 
            {
                "type": "directory", 
                "path": "bar", 
                "index": [
                    {
                        "type": "image/png", 
                        "link": "foo/test.png", 
                        "path": "bar/symlink.png"
                    }
                ]
            }
        ]
    }   
