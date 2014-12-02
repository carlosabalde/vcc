# -*- mode: ruby -*-
# vi: set ft=ruby :

VMS = [
  {
    version: '4',
    primary: true,
  },
  {
    version: '3',
    primary: false,
  },
]

Vagrant.configure('2') do |config|
  config.vm.box = 'ubuntu/trusty64'
  config.vm.box_version = '=14.04'
  config.vm.box_check_update = true
  config.vm.hostname = 'dev'

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      'modifyvm', :id,
      '--memory', '1024',
      '--natdnshostresolver1', 'on',
      '--accelerate3d', 'off',
    ]
  end

  VMS.each do |vm|
    config.vm.define 'v' + vm[:version], primary: vm[:primary] do |machine|
      machine.vm.provider :virtualbox do |vb|
        vb.customize [
          'modifyvm', :id,
          '--name', 'Varnish Custom Counters (Varnish ' + vm[:version] + '.x)',
        ]
      end

      machine.vm.provision :salt do |salt|
        salt.pillar({
          'version' => vm[:version],
        })

        salt.minion_config = 'extras/envs/dev/salt/minion'
        salt.run_highstate = true
        salt.verbose = true
        salt.log_level = 'info'
        salt.colorize = true
        salt.install_type = 'stable'
      end

      machine.vm.network :public_network

      machine.vm.synced_folder '.', '/vagrant', :nfs => false

      machine.vm.synced_folder 'extras/envs/dev/salt/roots', '/srv', :nfs => false
    end
  end
end
