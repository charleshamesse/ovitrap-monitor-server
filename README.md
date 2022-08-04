# Ovitrap Monitor - Server

Web application to process ovitrap stick pictures, count eggs and visualize overviews of mosquito activity.

This repo holds the code for the back-end of the application which runs server-side. It is developed using Python and the Django framework. It connects to AWS S3 to store, retrieve and process ovitrap pictures.

## Project setup

1. Set up a local development environment with Python 3 and install the Python packages listed in `requirements.txt`.
2. Edit the variable `CORS_ALLOWED_ORIGINS` in the file `oeg/settings.py` to point to your Ovitrap Monitor front-end instance. Otherwise, the connection will be refused.
3. Create a `.env` file with the your AWS S3 bucket credentials:
```
S3_BUCKET=your-WS-S3-bucket-name
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-AWS-secret-access-key
```
4. Run the following command to launch Django on your local computer:
```
python manage.py runserver
```
