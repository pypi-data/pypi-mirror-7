#LDAP Setup#
If you already have an external user database which can be used to authenticate
users over LDAP, you may use this with YubiAuth instead of the built-in
password system. When LDAP password validation is used, local password
validation will be disabled, and each time a user attempts to log in the
request will be delegated to the LDAP server. Any user that does not exist in
the LDAP database will not be able to log in. 

##Configuration##
To enable LDAP you will need to modify the configuration file, located here:

	/etc/yubico/auth/yubiauth.conf

First off, find the USE_LDAP setting, and change it to True:

	USE_LDAP = True

There are two more settings that are required to make things work. These are
set as follows:

	LDAP_SERVER = '<LDAP server URL>'

This is the URL to the LDAP server to use for password authentication. The
format for this is defined in (RFC 4516)[http://www.ietf.org/rfc/rfc4516.txt].

	LDAP_BIND_DN = '<template for Bind DN>'

This is a template for the Bind DN used to authenticate a user. The template
string is passed the User object when performing authentication, and uses
Pythons (string.format)[http://docs.python.org/2/library/string.html#formatstringshttp://docs.python.org/2/library/string.html#formatstrings]
function to format the string. The User object is passed as "user".
For example:

	LDAP_BIND_DN = 'uid={user.name},ou=People,dc=example,com'

If the user "Bob" tries to log in, the above template expands to:

	uid=Bob,ou=People,dc=example,com

Note that while {user.name} can always be used to expand to the username,
relying on other attributes may require that the user already exist in the
YubiAuth database to work.

Note that what is needed to authenticate the user here is the fully qualified
DN, which might not include the actual username of the user. To connect a user
of with an arbitrary username to a specific LDAP user, you can either use other
user attributes in the template, or use the special attribute "_ldap_bind_dn"
attribute which will override the LDAP_BIND_DN on a user level.

Finally, there is an LDAP_AUTO_IMPORT setting which will automatically create
a user in the YubiAuth database if the user tries to log in while LDAP is being
used, and the user does not already exist in YubiAuth. This is only done once
the password has been verified against the LDAP server.

For example, if the user "johndoe" tries to log in with the password "letmein",
YubiAuth will query the LDAP server, and if authentication is successful, the
"johndoe" user will be created in YubiAuth, so that YubiKeys may be associated
with the account. If the LDAP_AUTO_IMPORT setting is turned off, then the login
request will fail.

###Active Directory###
If you use Active Directory you can find out what the Bind DN should be by
doing the following:

On the Windows Server, open a command prompt. Run the command:

	dsquery user -name <username>

This will list the correct Bind DB to use for the user <username> (you can use
a * instead of a real username and all users will be printed):

	"CN=user1,CN=Users,DC=example,DC=com"

In the above case, the Bind DN would then be set to:

	LDAP_BIND_DN = 'CN={user.name},CN=Users,DC=example,DC=com'

###Final steps###
Everything should now be configured correctly. You will need to restart your
web server for the changes to take effect.
