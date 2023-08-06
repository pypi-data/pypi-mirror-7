#YubiHSM Setup#
While YubiAuth works fine without the use of a
(YubiHSM)[http://www.yubico.com/products/yubihsm/], the security of your users
passwords can be greatly increased by use of one. This document describes why
you may want to use a YubiHSM together with YubiAuth, and how to set it all up.

##Benefits of a YubiHSM##
###Without a YubiHSM###
In the event that your server becomes compromized, an attacker may gain access
to the YubiAuth database, which stores user credentials such as usernames and
passwords. Passwords are never stored as plain text, they are always hashed
to make it as difficult as possible for an attacker to extract them. Even so,
if the attacker can guess a users password, they can use the database to
verify if their guess is correct or not. Given enough time and processing
power, an attacker test weak passwords such as words or simple phases, and
expose some of your users passwords that way.

###With a YubiHSM###
When using a YubiHSM, users passwords are hashed using a keyed hash. This key
exists inside the YubiHSM hardware device, and never leaves it. Without the
physical device, it becomes impossible for an attacker to verify if a guessed
password is correct or not. This means that even if an attacker gains access
to the YubiAuth server, the attacker can at most test passwords for as long
as (s)he has access to the machine, and at a very low rate. As soon as the
intrusion becomes detected and the YubiHSM is disconnected (or the attacker
loses access), the attacker can no longer test passwords, even with a copy of
the database.

##Configuration##
For maximum security, a YubiHSM should have as restrictive permissions set as
possible. Here are instructions on how to configure a YubiHSM with the bare
minimum required for use with YubiAuth.

###YubiHSM###
Insert the YubiHSM into the USB-slot of a trusted computer, preferably one
which is not connected to the Internet (this is for initially programming the
YubiHSM) while pressing the configuration switch to enter configuration mode.
Once connected, access the device configuration by opening a terminal program,
and connecting to the device (See the
(YubiHSM Manual)[http://www.yubico.com/wp-content/uploads/2012/10/YubiHSM-Manual-v1.0.4.pdf]
for detailed instructions). If the YubiHSM has been previously configured,
begin by erasing the old configuration as described in the manual. With an
empty configuration, program the YubiHSM in hsm mode with HMAC_SHA1_GENERATE
enabled:

	NO CFG> hsm 00010000

Optionally, set a master password and add admin YubiKeys. See the YubiHSM
manual for more details.

Once configured, you will need to generate at least one key to use:

	HSM> keygen 1 1 20 - using flags 00010000 and len 032
	00000001,a90327480bdb3876cb84883b91f8795e61fb460f6ba09f2a7fa03554549fe43b
	HSM> keycommit - Done

The above commands will generate a random key and commit it to memory. You
will most likely want to make note of the generated key, but it is vital that
you keep it safe. If it becomes known to an attacker the benefit of having a
YubiHSM will be lost.

Once done, exit the configuration mode:

	HSM> exit

Now, remove the YubiHSM device and plug it into the YubiAuth server machine
(without pressing the configuration mode button). If the YubiHSM was
configured with a master password and/or administrator YubiKeys, you will need
to unlock the device as described in the manual (this needs to be done each
time the server is rebooted).

###python-pyhsm###
Once the YubiHSM has been configured with a key that can be used for password
hashing, you need to instruct YubiAuth to use it. First off, you will need to
install the python-pyhsm package if it is not already installed. For debian
this is done by running the following command:

	sudo apt-get install python-pyshm

The recommended way of interfacing with the YubiHSM through YubiAuth is via
the yhsm-daemon process which is part of the python-pyhsm package. This allows
multiple applications to access a single YubiHSM on the same computer. See the
(python-pyhsm documentation)[https://github.com/Yubico/python-pyhsm/wiki] for
more information. With the daemon running, YubiAuth can connect to it over the
loopback interface.

###YubiAuth###
Now the only thing remaining is to tell YubiAuth to use the YubiHSM, which is
done by editing the configuration file located here:

	/etc/yubico/auth/yubiauth.conf

First off, find the USE_HSM setting, and change it to True:

	USE_HSM = True

Once that is done, the default settings should take care of the rest. You may
want to skim through the rest of the configuration file as well, to make sure
everything is correct. Make sure the YHSM_DEVICE settings is correct according
to how you set up the yhsm-daemon, and make sure CRYPT_CONTEXT has the correct
key handle (the yhsm_pbkdf2_sha1__key_handle setting, which should correspond
to the key generated when running the keygen command in the YubiHSM step).

####Existing passwords####
If this is a new installation you can skip this section. If not, it is
important to realize that existing users passwords are not automatically
protected by the YubiHSM. First, their passwords have to be migrated to use
the YubiHSM, which is automatically done the next time they change their
password. It is up to you to get your existing users to update their
passwords to get the increased security.

As an alternative, YubiAuth will automatically migrate users existing passwords
when they log in. This is not quite as secure as having your users change
their passwords, which we recommend you do. 

###Final steps###
Everything should now be configured correctly. You will need to restart your
web server for the changes to take effect.
