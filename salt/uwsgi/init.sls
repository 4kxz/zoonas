uwsgi:
  pip.installed:
    - pkgs: uwsgi
    - require:
      - sls: salt.django
  service.running:
    - enable: True
    - require:
      - pip: uwsgi

/etc/init/uwsgi.conf:
  file.managed:
    - source: salt://salt/uwsgi/uwsgi.conf
    - makedirs: True
    - template: jinja
    - require:
      - pip: uwsgi

uwsgi_available:
  file.managed:
    - name: /etc/uwsgi/apps-available/{{ pillar['name'] }}.ini
    - source: salt://salt/uwsgi/zoonas.ini
    - makedirs: True
    - template: jinja
    - require:
      - pip: uwsgi

uwsgi_enabled:
  file.symlink:
    - name: /etc/uwsgi/apps-enabled/{{ pillar['name'] }}.ini
    - target: /etc/uwsgi/apps-available/{{ pillar['name'] }}.ini
    - makedirs: True
    - require:
      - file: uwsgi_available

/var/log/uwsgi:
  file.directory:
    - user: {{ pillar['username'] }}
    - makedirs: True
    - require:
      - pip: uwsgi
