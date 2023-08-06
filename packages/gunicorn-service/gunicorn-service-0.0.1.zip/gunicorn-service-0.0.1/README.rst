
startup gunicorn as service
====

Add python file as service in /etc/init.d/

example: /etc/init.d/myproj

    #!/usr/local/bin/python


    import sys, os
    
    from  gunicorn_service import ServiceSetting, gunicorn_service


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
    chdir               = "/hoem/Dev/Server/Server/Game/Game"
    worker_class        = "gevent"              
    access_logfile      = "/var/logs/Game/access.log"
    error_logfile       = "/var/logs/Game/error.log"

    
    
use service start| stop | stat, and try chkconfig myproj on 


