# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define :servidorWeb do |servidorWeb|
    servidorWeb.vm.box = "ubuntu/jammy64"
    servidorWeb.vm.boot_timeout = 600
    servidorWeb.vm.network :private_network, ip: "192.168.60.3"
    servidorWeb.vm.provision "file", source: "webapp", destination: "/home/vagrant/webapp"
    servidorWeb.vm.provision "file", source: "init.sql", destination: "/home/vagrant/init.sql"
    servidorWeb.vm.provision "shell", path: "script.sh"
    servidorWeb.vm.hostname = "servidorWeb"
    servidorWeb.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
      vb.cpus = 1
    end
  end
end
