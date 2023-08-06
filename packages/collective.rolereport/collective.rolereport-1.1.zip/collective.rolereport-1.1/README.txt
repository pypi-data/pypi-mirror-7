Introduction
============

This module can generate a report on all roles and all users for each role. 
It generates an HTML report with userid, fullname and email.

Go to http://<plonesite>/@@role-report

DO NOT GIVE THAT URL TO AN END USER!

The report will be generated to the file system. This is because on the site
where this is being used, the report runs longer than the Apache timeout.
It also tends to block a lot of the site, so it becomes unusable.

Tested with Plone 3. Should work in Plone 4.
