postgresql:
  pkgrepo.managed:
    - name: deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main
    - key_url: http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc
  pkg.installed:
    - pkgs:
      - postgresql-9.3
      - postgresql-contrib-9.3
      - postgresql-client-9.3
      - postgresql-server-dev-9.3
    - require:
      - pkgrepo: postgresql
  service.running:
    - enable: True
    - require:
      - pkg: postgresql
  postgres_user.present:
    - user: postgres
    - name: {{ pillar['postgresql']['username'] }}
    - password: {{ pillar['postgresql']['password'] }}
    - require:
      - service: postgresql
  postgres_database.present:
    - user: postgres
    - template: template0
    - name: {{ pillar['postgresql']['database'] }}
    - owner: {{ pillar['postgresql']['username'] }}
    - encoding: UTF8
    - lc_ctype: en_US.UTF8
    - lc_collate: en_US.UTF8
    - require:
      - postgres_user: postgresql
