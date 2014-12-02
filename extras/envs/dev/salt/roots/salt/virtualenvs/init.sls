virtualenvs.install-virtualenv:
  pip.installed:
    - name: virtualenv==1.11.5
    - user: root
    - require:
      - sls: global

{% for version, packages in [('2.6', []),
                             ('2.7', ['ipython'])] %}
virtualenvs.python{{ version }}:
  virtualenv.managed:
    - name: /home/vagrant/virtualenvs/python{{ version }}
    - python: /usr/bin/python{{ version }}
    - user: vagrant
    - requirements: /vagrant/requirements.txt
    - require:
      - pip: virtualenvs.install-virtualenv

{% for package in packages %}
virtualenvs.python{{ version }}.{{ package }}:
  pip.installed:
    - name: {{ package }}
    - user: vagrant
    - bin_env: /home/vagrant/virtualenvs/python{{ version }}
    - require:
      - virtualenv: virtualenvs.python{{ version }}
{% endfor %}
{% endfor %}
