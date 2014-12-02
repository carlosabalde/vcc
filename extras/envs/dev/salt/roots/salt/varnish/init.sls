varnish.repository:
  pkgrepo.managed:
    - name: deb https://repo.varnish-cache.org/ubuntu/ trusty varnish-{{ pillar['version'] }}.0
    - humanname: Varnish {{ pillar['version'] }}.x
    - key_url: https://repo.varnish-cache.org/ubuntu/GPG-key.txt
    - file: /etc/apt/sources.list.d/varnish.list
    - require_in:
      - pkg: varnish.packages

varnish.packages:
  pkg.installed:
    - refresh: True
    - pkgs:
      - varnish
      - libvarnishapi1
      - libvarnishapi-dev

varnish.service:
  service.running:
    - name: varnish
    - require:
      - pkg: varnish.packages
