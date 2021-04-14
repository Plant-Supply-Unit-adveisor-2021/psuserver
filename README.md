# PSU - Server
The task of the PSU-Server in our Plant Supply Unit project is to coordinate all PSUs and store their data to present it.
The server software is based on django ([djangoproject.com](https://djangoproject.com)) and therefore is mainly a website with some additional tweaks to control the PSUs.

# Development Installation
For getting started you have to install python ([python.org](https://python.org)). After installing python, it is highly recommended installing virtualenv. You can do this by running the following command (given python is added to your PATH):

    python -m pip install virtualenv

Afterwards you should clone this repository and run `init_python_venv.bat` if you are running windows. By doing so you will end up with a local python environment for this project. If you are running another OS, you will have to run the following commands in the folder of the cloned repository.

    virtualenv .venv
    source ./.venv/bin/activate
    python -m pip install -r requirements.txt

In order to develop you must be able to create the django translation files. These are created using a tool called [GNU gettext](https://www.gnu.org/software/gettext/). Please also install this piece of software to start developing.

Moving on you should create a file named `.env` in the parent directory of your project directory with the line `DJANGO_DEBUG="True"`.
Next up you will need to run some initial commands to initialize the django app. On windows you can simply run `django_migrate_n_compile.bat`. If you are not running windows, you can use the following commands:

    source ./.venv/bin/activate
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic
    django-admin makemessages -l de
    django-admin compilemessages -l de

Now your installation should be complete.

# Using the Development Server
To get started you should be familiar with the concept of the virtual environment which is created in the section above. When using the command line to start the development server, to do migrations, etc. You have to activate the virtual environment first. On Windows use `.\.venv\Scripts\activate` to do so. On Linux/MacOS you will achieve the same by typing `source ./.venv/bin/activate`. You can always see that your environment is active via the `(.venv)` tag which is displayed above/beside the current path on the command line. To start your development server you first have to create a superuser via the following command:

    python manage.py createsuperuser

Afterwards you can start your server through the runserver command:
    
    python manage.py runserver

Now you can head over to [localhost:8000](http://127.0.0.1:8000/) to take a glance at the website. The admin panel will be accessible at [localhost:8000/admin](http://127.0.0.1:8000/admin)
