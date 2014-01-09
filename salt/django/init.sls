admin:
  user.present:
    - name: {{ pillar['username'] }}

django:
  file.recurse:
    - name: {{ pillar['path'] }}/django
    - source: salt://django
    - include_empty: True
    - user: {{ pillar['username'] }}
    - group: {{ pillar['username'] }}
    - file_mode: 744
    - dir_mode: 755
    - require:
      - user: admin

venv:
  pkg.installed:
    - names:
      - python-dev
      - python-pip
      - python-virtualenv
      - libjpeg-dev
  virtualenv.managed:
    - name: {{ pillar['path'] }}/venv
    - user: {{ pillar['username'] }}
    - requirements: salt://django/requirements/{{ pillar['django']['requirements'] }}
    - no_site_packages: True
    - require:
      - pkg: venv
      - file: django

{{ pillar['path'] }}/django/settings/server.py:
  file.managed:
    - source: salt://django/settings/server.py
    - template: jinja
    - user: {{ pillar['username'] }}
    - group: {{ pillar['username'] }}
    - file_mode: 744
    - dir_mode: 755
    - require:
      - file: django

{{ pillar['path'] }}/django/wsgi.py:
  file.managed:
    - source: salt://django/wsgi.py
    - template: jinja
    - user: {{ pillar['username'] }}
    - group: {{ pillar['username'] }}
    - file_mode: 744
    - dir_mode: 755
    - require:
      - file: django

{{ pillar['path'] }}/static-files:
  file.recurse:
    - source: salt://{{ pillar['django']['collectstatic_dir']}}
    - user: {{ pillar['username'] }}
    - group: {{ pillar['username'] }}
    - file_mode: 744
    - dir_mode: 755
    - require:
      - file: django

{{ pillar['path'] }}/media-files:
  file.directory:
    - user: {{ pillar['username'] }}
    - group: {{ pillar['username'] }}
    - file_mode: 744
    - dir_mode: 755
    - makedirs: True
    - require:
      - file: django
