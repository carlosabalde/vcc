user.timezone:
  timezone.system:
    - name: Europe/Madrid
    - utc: True

/home/vagrant/.bashrc:
  file.managed:
    - source: salt://user/bashrc
    - user: vagrant
    - group: vagrant
    - mode: 644
