Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
“Software”), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Description: ip2country
        ==========
        |travis|_ |coveralls|_ |pypibadge|_
        
        -----
        About
        -----
        Lookup country code (iso 3166) by IP address.
        
        -------
        Install
        -------
        
        .. code:: shell
        
          $ pip install ip2country
        
        Or
        
        .. code:: shell
        
          $ python setup.py install
        
        
        ----------
        How to use
        ----------
        
        First: Implement IStore Interface
        ---------------------------------
        You must implement IStore interface in ip2country/interfaces.py.
        
        There is a sample implementation in example/store.
        This implementation is stored all records on the system memory.
        
        Second: Store the records
        -------------------------
        .. code:: python
        
            store = Store()
            parser = Parser(store)
            with open(RECORD_FILE) as fp:
                parser.do(fp)
        
        See examples/lookup.py:load for more detail.
        
        Third: Lookup the IPAddress
        ---------------------------
        
        .. code:: python
        
            store = Store()
            record = store.lookup(IP_ADDRESS)
            if record is None:
                print('Record not found')
            else:
                print('{0} is allocated to {1}'.format(IP_ADDRESS, record.cc))
        
        See examples/lookup.py:main for more detail.
        
        
        -------------
        Run the tests
        -------------
        
        .. code:: shell
        
          $ tox
        
        -------
        License
        -------
        ip2country is licensed under the MIT LICENSE.  See ./LICENSE.rst.
        
        
        .. _travis: https://travis-ci.org/yosida95/ip2country
        .. |travis| image:: https://travis-ci.org/yosida95/ip2country.svg?branch=master
        
        .. _coveralls: https://coveralls.io/r/yosida95/ip2country?branch=master
        .. |coveralls| image:: https://coveralls.io/repos/yosida95/ip2country/badge.png?branch=master
        
        .. _pypibadge: http://badge.fury.io/py/ip2country
        .. |pypibadge| image:: https://badge.fury.io/py/ip2country.svg?dummy
        
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
Classifier: Topic :: Internet :: WWW/HTTP
Classifier: Topic :: Security
Classifier: Topic :: Software Development :: Libraries :: Python Modules
