manifest_generator - a HTML5 application cache manifest generator
=================================================================
Copyright 2014 by Kevin Dahlhausen (kpd@powertwenty.com)


Overview
--------
This package contains a utility to generate the HTML5 application cache manifest file.   Running it multiple times only changes the manifest if the manifest contents or contents of files listed in the cache change. 

License
-------
This software is licensed under the GNU GPL.  Please see the file 'LICENSE.txt' for details.  Note that this license requires any software using this library to make source code available. 

Should you not wish to use the software under the GNU GPL license, please contact Kevin Dahlhausen (kpd@powertwenty.com) to discuss alternative licensing.
 

Requires
--------
glob2 - https://github.com/miracle2k/python-glob2/



Usage
-----

some exaples:

    manifest_gen --output cache.manifest --cache "js/**/*.js" --cache "css/**/*" --nocache dontcache.js --network counter.html --fallback fallback.html 

    manifest_gen -o cache.manifest -c "js/**/*.js" -c "css/**/*" -nc dontcache.js -n counter.html -f fallback.html

    manifest_gen -h

    manifest_gen --doc_root C:/Users/p20/projects/rc_flug_log_client/android/workspace/rc_flug_log_phonegap/assets/www --cache "C:/Users/p20/projects/rc_flug_log_client/android/workspace/rc_flug_log_phonegap/assets/www/**/*" --url /static/mobile 

Tests
-----
To run the unit tests (python >= 2.7):
    python -m unittest discover

