   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Description: |Build Status| |Coverage Status| |PyPI badge| |Installs badge| |Wheel badge|
        
        |Logo|
        
        Description
        -----------
        
        Free Open Source, Django based document management system with custom metadata
        indexing, file serving integration, tagging, digital signature verification,
        text parsing and OCR capabilities.
        
        `Website`_
        
        `Video demostration`_
        
        `Documentation`_
        
        `Translations`_
        
        `Mailing list (via Google Groups)`_
        
        
        License
        -------
        
        This project is open sourced under `Apache 2.0 License`_.
        
        Installation
        ------------
        
        To install **Mayan EDMS**, simply do:
        
        .. code-block:: bash
        
            $ virtualenv venv
            $ source venv/bin/activate
            $ pip install mayan-edms==1.0.rc2
        
        Instead of using the usual ./manage.py use the alias mayan-edms.py:
        
        .. code-block:: bash
        
            $ mayan-edms.py initialsetup
            $ mayan-edms.py runserver
        
        Point your browser to 127.0.0.1:8000 and use the automatically created admin
        account.
        
        Contribute
        ----------
        
        - Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
        - Fork `the repository`_ on GitHub to start making your changes to the **master** branch (or branch off of it).
        - Write a test which shows that the bug was fixed or that the feature works as expected.
        - Make sure to add yourself to the `contributors file`_.
        - Send a pull request
        
        
        .. _Website: http://www.mayan-edms.com
        .. _Video demostration: http://bit.ly/pADNXv
        .. _Documentation: http://readthedocs.org/docs/mayan/en/latest/
        .. _Translations: https://www.transifex.com/projects/p/mayan-edms/
        .. _Mailing list (via Google Groups): http://groups.google.com/group/mayan-edms
        .. _Apache 2.0 License: https://www.apache.org/licenses/LICENSE-2.0.txt
        .. _`the repository`: http://github.com/mayan-edms/mayan-edms
        .. _`contributors file`: https://github.com/mayan-edms/mayan-edms/blob/master/docs/credits/contributors.rst
        
        .. |Build Status| image:: http://img.shields.io/travis/mayan-edms/mayan-edms/master.svg?style=flat
           :target: https://travis-ci.org/mayan-edms/mayan-edms
        .. |Coverage Status| image:: http://img.shields.io/coveralls/mayan-edms/mayan-edms/master.svg?style=flat
           :target: https://coveralls.io/r/mayan-edms/mayan-edms?branch=master
        .. |Logo| image:: https://github.com/mayan-edms/mayan-edms/raw/master/docs/_static/mayan_logo.png
        .. |Installs badge| image:: http://img.shields.io/pypi/dm/mayan-edms.svg?style=flat
           :target: https://crate.io/packages/mayan-edms/
        .. |PyPI badge| image:: http://img.shields.io/pypi/v/mayan-edms.svg?style=flat
           :target: http://badge.fury.io/py/mayan-edms
        .. |Wheel badge| image:: http://img.shields.io/badge/wheel-yes-green.svg?style=flat
        
        
        1.0 (2014-07-??)
        ================
        
        - New home @ https://github.com/mayan-edms/mayan-edms
        - Updated to use Django 1.6
        - Translation updates
        - Custom model properties removal
        - Source code improvements
        - Removal of included 3rd party modules
        - Automatic testing and code coverage check
        - Update of required modules and libraries versions
        - Database connection leaks fixes
        - Support for deletion of detached signatures
        - Removal of Fabric based installations script
        - Pluggable OCR backends
        - OCR improvements
        - License change, Mayan EDMS in now licensed under the Apache 2.0 License
        - PyPI package, Mayan EDMS in now available on PyPI: https://pypi.python.org/pypi/mayan-edms/
        - New REST API
        
        For a full changelog and release notes go to: http://mayan.readthedocs.org/en/latest/releases/1.0.html
        
Platform: any
Classifier: Development Status :: 5 - Production/Stable
Classifier: Environment :: Web Environment
Classifier: Framework :: Django
Classifier: Intended Audience :: Education
Classifier: Intended Audience :: Developers
Classifier: Intended Audience :: Information Technology
Classifier: License :: OSI Approved :: Apache Software License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Topic :: Internet :: WWW/HTTP
Classifier: Topic :: Internet :: WWW/HTTP :: WSGI :: Application
Classifier: Topic :: Communications :: File Sharing
