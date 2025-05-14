# Mitrah-HRMS

To create virual env
```
	python -m venv .venv
```

To activate environment
```
	.venv\Scripts\activate
```

To install all required libriaries for this app
```
	pip install -r requirements.txt
```

To create a django project
```
	django-admin startproject main .
```

To create an app,
```
	python manage.py startapp users
```

If any changes in db or model files, need to migrate
```
	python manage.py makemigrations
	python manage.py migrate
```

Create new python file in the name of `settings_local.py` under `main` directory. In this file, we can overwrite the configurations which are configured in `settings.py`.

For example, we need to replaced default database credential by our local postgreSQL database credential. Just put below code in `settings_local.py`

```
	DATABASES = {
		"default": {
			"ENGINE": "django.db.backends.postgresql",
			"NAME": "hrms", # your database name
			"USER":"postgres", # your username
			"PASSWORD":"postgresql@123", # your password
			"HOST":"localhost", # your host name
			"PORT":5433 # your port
		}
	}
```
Run below command to create company initially,

```
	python singleton.py
```

```
*NOTE:* Please make sure that a employee has been created in the employee table in your database.
```

To run this app
```
	python manage.py runserver
```