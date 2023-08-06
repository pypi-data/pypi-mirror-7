Copyright (c) 2014 Mike Taylor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Description: ninka
        =====
        
        認可 ninka - permission, license
        
        Python package to help working with IndieAuth.
        
        Roadmap
        =======
        Working
        * IndieAuth tools
        
        Pending
        * MicroPub support
        
        See the examples/ directory for sample command line tools.
        
        Contributors
        ============
        * bear (Mike Taylor)
        
        IndieAuth
        =========
        discoverAuthEndpoints()
        -----------------------
        Find the authorization or redirect_uri endpoints for the given authDomain.
        
        validateAuthCode()
        ------------------
        Call authorization endpoint to validate given auth code.
        
        Requires
        ========
        Python v2.6+ but see requirements.txt for a full list
        
        Installing the latest version of Requests and it's OAuth plugin now requires
        pyOpenSSL which will require compiling of source libs. You may need to have
        installed the -dev package for the version of Python you are working with.
        
        For testing we use [httmock](https://pypi.python.org/pypi/httmock/) to mock
        the web calls.
        
Platform: UNKNOWN
