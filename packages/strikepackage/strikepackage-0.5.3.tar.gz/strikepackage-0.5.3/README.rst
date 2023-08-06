Strikepackage
=============

Overview
--------

Strikepackage is a command line tool for creating and provisioning VMs on Citrix XenServer. It supports any XenServer that will work with the XenSever 6.2 SDK.
It's been tested on XenServer 5.6, 6.0.2, 6.1 and 6.2.

Although you can use this tool to simply clone VMs, the main purpose of Strikepackage is to get a VM that is configured with `cloud-init <http://cloudinit.readthedocs.org/en/latest/index.html>`_ online, on the right IP, and attached to a Puppet server so it can run its manifests. To this end, Strikepackage supports integration with `MCHM <https://github.com/pwyliu/magna-carta-holy-metadata>`_, a simple Flask application for hosting cloud-init userdata, and the `Puppet HTTP API <http://docs.puppetlabs.com/guides/rest_api.html>`_. Together these APIs provide a way to automatically deploy a machine without having to use XenCenter at all. Which is good, because XenCenter is a huge pain in the ass sometimes.

A Strikepackage run that uses MCHM and Puppet works like this:

#. Strikepackage gathers network, hostname and other info from user.
#. Strikepackage generates cloud-init userdata based on templates you provide. Templates are written in the `jinja2 templating language <http://jinja.pocoo.org/docs/>`_ (see below for more details).
#. Strikepackage then uploads the userdata to MCHM and clones the VM with the XenAPI.
#. The VM starts with a "url=" kernel parameter. cloud-init uses this kernel param to grab the userdata from MCHM and bootstrap the VM.
#. After the VM is up, cloud-init has `phoned home <http://cloudinit.readthedocs.org/en/latest/topics/examples.html#call-a-url-when-finished>`_ to MCHM, and the Puppet agent has requested a certificate, Strikepackage uses the Puppet API to sign the new node CSR.
#. Puppet manifests run and all is right with the world. Success!

Requirements
------------

* Python 2.7.6+

Installation And Configuration
------------------------------

1. Install strikepackage with pip.

.. code:: bash

  pip install strikepackage

2. Before you can use strikepackage, you need to create a *config.yaml* file and edit it for your environment. The example config contains more info.

.. code:: bash

  # When you run strikepackage, it looks for a config file in the current
  # directory first, then in /home/$USER/.strikepackage/.
  # If you specify an alternate path with --conf, this will be used instead.

  # mkconfig creates /home/$USER/.strikepackage and places example files.
  strikepackage mkconfig
  cd ~/.strikepackage
  cp examples/config.yaml config.yaml
  vim config.yaml

3. In XenCenter, tag the XenServer templates you would like to clone with the string you configured in *config.yaml*.

4. If you are using MCHM, create *userdata.jinja2* and *metadata.jinja2* in the template directory you configured in *config.yaml*.

.. code:: bash

  cd ~/.strikepackage
  cp examples/*.jinja2 templates/
  cd templates/
  vim userdata.jinja2
  vim metadata.jinja2

5. If you are using Puppet, make sure you've got a key and cert and have configured *config.yaml*.

6. Now you are ready to run Strikepackage. The main invocation looks like this

.. code:: bash

  strikepackage deploy https://myxenserver.ho.domain.local


Configuring Puppet API Access
-----------------------------

In order to configure access to the `Puppet API <https://docs.puppetlabs.com/guides/rest_api.html>`_ you will need to do two things:

1. Generate a certificate and key on the Puppet master for use with Strikepackage

2. Configure *auth.conf* on the Puppet master to allow access to the */certificate_status* endpoint

Generate the certificate with `puppet cert generate <https://docs.puppetlabs.com/references/3.stable/man/cert.html>`_. You should be creating a unique certificate for every user.

.. code:: bash

  # Generate a certificate for myusername
  puppet cert generate strikepackage-myusername

  # The certificate and key will be located in $ssldir/certs and
  # $ssldir/private_keys respectively. Copy these files and the CA cert to
  # /home/$USER/.strikepackage/keys on your workstation.
  cd $(puppet master --configprint ssldir)
  find . | grep strikepackage
  find . | grep ca_crt

Allow access to */certificate_status* by creating an ACL in *auth.conf*. Below is an example. See the `auth.conf documentation <https://docs.puppetlabs.com/guides/rest_auth_conf.html>`_ for more details.

.. code:: bash

  # /etc/puppet/auth.conf
  path /certificate_status
  auth yes
  allow strikepackage-myusername

Creating MCHM Templates
-----------------------

Template are written in the `jinja2 templating language <http://jinja.pocoo.org/docs/>`_. MCHM works by using cloud-init's `NoCloudNet <http://cloudinit.readthedocs.org/en/latest/topics/datasources.html#no-cloud>`_ `data source <http://smoser.brickies.net/ubuntu/nocloud/>`_. Strikepackage looks in the template dir for two files to render and upload to MCHM: *userdata.jinja2* and *metadata.jinja2*.

You can put whatever cloud-config you want in these templates. The only hard requirement is that cloud-init must `phone home <http://cloudinit.readthedocs.org/en/latest/topics/examples.html#call-a-url-when-finished>`_ to MCHMs phonehome API endpoint when it's done. This is how Strikepackage knows the VM came online and finished booting. See the example userdata template in ~/.strikepackage/examples for more details.

A giant dict gets passed to templates as *params*. You can use any of these variables:

.. code:: python

  {
    'sp_tag': 'strikepackage',                                                        # from config.yaml
    'poolmaster': ('my_xenserver_name', 'ad26311d-da4b-48af-ab84-5aa82be42f8d'),      # a tuple of (name, xen_uuid)
    'template': ('my_template_name', '26982928-e8d5-6aab-7ade-66cdf3a900da'),         # a tuple of (name, xen_uuid)
    'network': ('my_network_name', '0c2cda95-f642-e0e2-5042-c1e597a435fa'),           # a tuple of (name, xen_uuid)
    'iid': '4b98060580f341dfa255cac95d01287d',                                        # uuid.uuid4().hex
    'rand_pass': '2905922eb1f34110ba81080206bb9b02e85c8faf6e554311a2b801027dbe1b78',  # a randomly generated password. For temporary use only!

    'hostname': 'my_hostname',                                   # user input
    'fqdn': 'my_hostname.ho.mydomain.local',                     # user input
    'dhcp': False,                                               # user input
    'ip': '192.168.10.42',                                       # user input
    'gw': '192.168.10.1',                                        # user input
    'nw': '192.168.10.0',                                        # user input
    'broadcast': '192.168.10.255',                               # user input
    'netmask': '255.255.255.0',                                  # user input
    'dns_servers': '192.168.10.15 192.168.10.16 192.168.10.17',  # from config.yaml. It's "dns_servers" in the template and "dns_serverstring" in the config.
    'dns_searchdomain': 'ho.mydomain.local',                     # from config.yaml

    'mchm_enable': True,                                                     # from config.yaml
    'mchm_use_zeroconf': True,                                               # from config.yaml
    'mchm_max_polltime': 600,                                                # from config.yaml
    'mchm_templatedir': '/home/my_user/.strikepackage/templates',            # from config.yaml
    'mchm_url': 'https://mchm.mydomain.local',                               # from config.yaml
    'mchm_vm_url': u'http://169.254.169.254/api/53c7218b4ecee3043ee6e638/',  # returned by MCHM API call
    'mchm_id': u'53c7218b4ecee3043ee6e638'                                   # returned by MCHM API call

    'puppet_enable': True,                                                 # from config.yaml
    'puppet_cacert': '/home/my_user/.strikepackage/keys/ca_crt.pem',       # from config.yaml
    'puppet_key': '/home/my_user/.strikepackage/keys/strikepackage.crt',   # from config.yaml
    'puppet_cert': '/home/my_user/.strikepackage/keys/strikepackage.key',  # from config.yaml
    'puppet_url': 'https://puppet.mydomain.local:8140',                    # from config.yaml
    'puppet_environment': 'ops',                                           # from config.yaml
    'puppet_cooldown': 30,                                                 # from config.yaml

    'hipchat_enable': True,           # from config.yaml
    'hipchat_api_token': 'a_token',   # from config.yaml
    'hipchat_roomid': 'chatopzzzzz',  # from config.yaml
    'hipchat_from': 'strikepkg',      # from config.yaml
  }

Contributing
------------

All pull requests welcome! I ain't fancy.

Setup.py creates the strikepackage command. When running from source, execute
*run.py* instead.

.. code:: bash

  git clone https://github.com/pwyliu/strikepackage.git
  cd strikepackage
  ./run.py mkconfig
  ./run.py --help
