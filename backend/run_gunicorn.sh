#!/bin/bash

gunicorn foodgram.wsgi:application --bind 0:8000