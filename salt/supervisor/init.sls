supervisor:
  pkg:
    - installed
  service.running:
    - enable: True
    - require:
      - pkg: supervisor
  file.managed:
    - name: /etc/supervisor/conf.d/celeryd.conf
    - source: salt://salt/supervisor/celeryd.conf
    - makedirs: True
    - template: jinja
    - require:
      - pkg: supervisor
