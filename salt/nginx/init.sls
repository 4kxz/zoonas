nginx:
  pkg:
    - installed
  service.running:
    - enable: True
    - require:
      - pkg: nginx
  file.absent:
    - name: /etc/nginx/sites-enabled/default
    - require:
      - pkg: nginx

nginx_available:
  file.managed:
    - name: /etc/nginx/sites-available/{{ pillar['name'] }}.conf
    - source: salt://salt/nginx/zoonas.conf
    - makedirs: True
    - template: jinja
    - require:
      - pkg: nginx

nginx_enabled:
  file.symlink:
    - name: /etc/nginx/sites-enabled/{{ pillar['name'] }}.conf
    - target: /etc/nginx/sites-available/{{ pillar['name'] }}.conf
    - makedirs: True
    - require:
      - file: nginx_available
