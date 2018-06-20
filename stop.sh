#!/bin/bash

port=${1:-8080}
ps -ef|grep gunicorn|grep ${port}|awk '{print $2}'|xargs kill -15
