====
Polr
====

This is a simple package for shortening urls with http://polr.cf . Example usage is like this::

    from polr import api
    
    polr = api(apikey = "yourkeyhere")
    polr.shorten("http://google.com")
    >> u'http://polr.cf/1'

