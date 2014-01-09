base:
  '*':
    - salt.supervisor
    - salt.postgresql
    - salt.redis
    - salt.nginx
    - salt.django
    - salt.uwsgi
