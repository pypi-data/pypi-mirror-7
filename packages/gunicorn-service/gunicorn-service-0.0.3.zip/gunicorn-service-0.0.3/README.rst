
startup gunicorn as service
====
Add python file as service in /etc/init.d/

example: /etc/init.d/myproj

    #!/usr/local/bin/python


    import sys, os
    
    from  gunicorn_service import ServiceSetting, gunicorn_service

    # 
    # work dir setting in /home/project/myproj.py
    # and work dir contains wsgi as startup module
    #
    p = ServiceSetting(   config="/home/project/myproj.py"
                          name=os.path.basename(__file__), 
                          exe="/usr/local/bin/gunicorn" )


    gunicorn_service( p )


myproj.py
    settings            = "Game.settings.local" 
    bind                = "0.0.0.0:55555"       
    backlog             = 512                   
    user                = "root"                
    workers             = 1                     
    worker_connections  = 2048                  
    daemon              = True                  
    max_requests        = 40000
    chdir               = "/hoem/Server/Game"
    worker_class        = "gevent"              
    access_logfile      = "/var/log/access.log"
    error_logfile       = "/var/log/error.log"
    

    
    
use service start| stop | stat, and try chkconfig myproj on 


use one config to startup standalone or startup as a service..



Fix.. start with pid, and restart..

