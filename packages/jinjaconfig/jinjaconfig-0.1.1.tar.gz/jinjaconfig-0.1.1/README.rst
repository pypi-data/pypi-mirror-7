jinjaconfig
===========

A jinja2 renderer receiving a JSON string from commandline. Useful for generating config files in deployment
environments.


Installation
------------
Install jinja config ::

    pip install jinjaconfig

Install from sources ::

    pip install git+https://bitbucket.org/luisfernando/jinjaconfig.git

Usage ::

    usage: jinjaconfig [-h] --values [values] [file]

    A jinja2 renderer receiving arguments from commandline. Useful for generating
    config files in deployment enviroments

    positional arguments:
      file               template to parse

    optional arguments:
      -h, --help         show this help message and exit
      --values [values]  json encoded values

Basic Use
---------

1. Pass arguments from command line ::

    jinjaconfig example.conf --values="{"celery":{"task":"mytask","path":"/home/x/Env/myenv/bin/celery"},
    "num_procs":2,"user":"user","workdir":"/home/x/app/app/","logs":{"error":"/home/x/app/logs/err.log",
    "log":"/home/x/app/logs/log.log"}}"

2. Pass arguments from a file (\*NIX, Bash) and output to file ::

    jinjaconfig example.conf --values="`cat arguments.json`" > result.conf

example.conf ::

    ; ==================================
    ;  configuration example
    ; ==================================

    [program:celery]
    ; Set full path to celery program if using virtualenv
    command={{ celery.path }} worker -A {{ celery.task }}

    directory={{ workdir }}
    user={{ user }}
    numprocs={{ num_procs }}
    stdout_logfile={{ logs.log }}
    stderr_logfile={{ logs.error }}
    autostart=true
    autorestart=true
    startsecs=10

    ; Need to wait for currently executing tasks to finish at shutdown.
    ; Increase this if you have very long running tasks.
    stopwaitsecs = 600

    ; When resorting to send SIGKILL to the program to terminate it
    ; send SIGKILL to its whole process group instead,
    ; taking care of its children as well.
    killasgroup=true

    ; if rabbitmq is supervised, set its priority higher
    ; so it starts first
    priority=998

arguments.json ::

    {
       "celery" : {
          "task" : "mytask",
          "path" : "/home/x/Env/myenv/bin/celery"
       },
       "num_procs" : 2,
       "user" : "user",
       "workdir" : "/home/x/app/app/",
       "logs" : {
          "error" : "/home/x/app/logs/err.log",
          "log" : "/home/x/app/logs/log.log"
       }
    }


