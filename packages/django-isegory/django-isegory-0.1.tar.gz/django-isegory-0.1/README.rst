=======
Isegory
=======

Isegory is a simple Django app to declare the provenance of a dataset. A dataset
can be built extracting the data manually or it can be created by a script.
A working example in Spanish language can be found at http://kelsenproject.org/

Quick start
-----------

1. Add "isegory" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'isegory',
      )

2. Include the isegory URLconf in your project urls.py like this::

      url(r'^isegory/', include('isegory.urls')),

3. Run `python manage.py syncdb` to create the isegory models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create the app (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/isegory/
