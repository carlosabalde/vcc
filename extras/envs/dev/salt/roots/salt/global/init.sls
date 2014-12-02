global.packages:
  pkg.installed:
    - refresh: True
    - pkgs:
      - python
      - python-pip
      - python-software-properties
      - python-dev
      - python-docutils
      - ntp
      - links
      - curl
      - make
      - automake
      - libtool
      - build-essential
      - dh-make
      - devscripts
      - debhelper
      - apt-transport-https

#global.python-ppa:
#  pkgrepo.managed:
#    - name: ppa:fkrull/deadsnakes
#    - require_in:
#      - pkg: global.python-packages

global.python-ppa:
  cmd.run:
    - user: root
    - name: add-apt-repository -y ppa:fkrull/deadsnakes

global.python-packages:
  pkg.installed:
    - refresh: True
    - pkgs:
      - python2.6
      - python2.6-dev
    - require:
      - cmd: global.python-ppa
