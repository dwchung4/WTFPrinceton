import psycopg2
import urlparse
import os

def connect():
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	if 'WTFPrinceton' in BASE_DIR:
		conn = psycopg2.connect(
	    database='d8qajk44a19ere',
	    user='',
	    password='',
	    host='localhost',
	    port='',
		)
		return conn
	else:
		urlparse.uses_netloc.append("postgres")
		url = urlparse.urlparse(os.environ["DATABASE_URL"])
		conn = psycopg2.connect(
		    database=url.path[1:],
		    user=url.username,
		    password=url.password,
		    host=url.hostname,
		    port=url.port,
		)
		return conn

def set_database():
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	if 'WTFPrinceton' in BASE_DIR:
		DATABASES = {
		    'default': {
		        'ENGINE': 'django.db.backends.postgresql_psycopg2',
		        'NAME': 'd8qajk44a19ere',
		        'USER': '',
		        'PASSWORD': '',
		        'HOST': 'localhost',
		        'PORT': '',
		    }
		}
		return DATABASES
	else:
		DATABASES = {
		    'default': {
		        'ENGINE': 'django.db.backends.postgresql_psycopg2',
		        'NAME': 'd8qajk44a19ere',
		        'USER': 'ebrvvrlzfykjpq',
		        'PASSWORD': '8K7FrLGu2C8tTwgwhNHa80cqR1',
		        'HOST': 'ec2-23-21-42-29.compute-1.amazonaws.com',
		        'PORT': '5432',
		    }
		}
		return DATABASES