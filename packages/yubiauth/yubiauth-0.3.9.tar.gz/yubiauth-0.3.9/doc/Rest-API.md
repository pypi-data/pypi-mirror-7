#YubiAuth REST API#
All responses are formatted as JSON. Note that the URLs given in this document
assume the default REST_PATH of 'yubiauth'. If this setting is changed, you
will need to modify the below URLs accordingly.

##Users
Users each have a unique user ID as well as a unique username. Each user has a
password, and may have zero or more [YubiKeys](#yubikeys) assigned to them. 
Users can have [Attributes](#attributes).

###Create a user
####Resource

    POST http://<host>/yubiauth/users

####Request
**Paramerers**
 * **username** - A unique username **(required)**
 * **password** - The password to give to the user **(required)**

**Example:**

    curl http://127.0.0.1:8080/yubiauth/users --data "username=trillian&password=foobar"

####Response
Returns a **201 Created** response, with a **Location** header pointing to the 
created resource, as well as a JSON body containing the user ID and username:

    {"id": 41, "name": "trillian"}

###Listing users
####Resource

    GET http://<host>/yubiauth/users

####Request
Query parameters can optionally be provided to filter users by their Attributes,
or by their assigned YubiKeys. Only users matching the filters are shown.

**Example:**

    curl http://127.0.0.1:8080/yubiauth/users?yubikey=ccccccccccce

####Response
Returns a list of user IDs and usernames, for example:

    [
        { 'id': 42, 'name': 'zaphod' },
        { 'id': 43, 'name': 'ford' }
    ]

###View a user
####Resource

    GET http://<host>/yubiauth/users/<id-or-username>

####Request
A user can be uniquely identified by either the user ID or by the username.

**Example:**

    curl http://127.0.0.1:8080/yubiauth/users/43
    
or
    
    curl http://127.0.0.1:8080/yubiauth/users/ford

####Response
Returns a JSON representation of the user:

    {
        "attributes": {
            "full_name": "Ford Prefect"
        },
        "yubikeys": ["ccccccccccce"],
        "id": 43, 
        "name": "ford"
    }
    
###Deleting a user
####Resource

    DELETE http://<host>/yubiauth/users/<id-or-username>
    
or

    POST http://<host>/yubiauth/users/<id-or-username>/delete
    
####Request
Deleting a user is done by sending a DELETE request to the user. To accomodate
browsers that do not support this, an alternative is available which uses POST.

**Example:**

    curl -X DELETE http://127.0.0.1:8080/yubiauth/users/41
    
or

    curl -X POST http://127.0.0.1:8080/yubiauth/users/41/delete
    
####Response
Returns an empty response with status **204 No Content** on success.

###(Re-) Setting a users password
####Resource

    POST http://<host>/yubiauth/users/<id-or-username>/reset

####Request
**Parameters**
 * **password** - The users new password **(required)**

**Example:**

    curl http://127.0.0.1:8080/yubiauth/users/41/reset --data "password=newpass"

####Response
Returns an empty response with status **204 No Content** on success.

###Validating a users password and/or YubiKey OTP
Checks if a given password and/or YubiKey OTP (One Time Password) is valid for the user.

####Resource

    GET or POST http://<host>/yubiauth/users/<id-or-username>/validate

####Request
**Parameters**
 * **password** - The value of the attribute to set **(optional)**
 * **otp** - The value of the attribute to set **(optional)**

**Example:**

    curl http://127.0.0.1:8080/yubiauth/users/41/validatepassword=foo&otp=ccccccccccceglgvbrbttbctichrejkvbjbgigetfgkr

####Response
A JSON object containing "valid_password" and "valid_otp" keys, each mapping to either true or false.
For example:

    {
        "valid_password": true,
        "valid_otp": false
    }

##YubiKeys
YubiKeys are identified by their unique prefixes. Each YubiKey can be assigned to
zero or more [Users](#users), and can be enabled or disabled. Each YubiKey can have
[Attributes](#attributes).

###Assigning a YubiKey to a User
####Resource

    POST http://<host>/yubiauth/user/<id-or-username>/yubikeys

####Request
**Parameters**
 * **yubikey** - The prefix of the YubiKey to assign **(required)**

**Example:**

    curl http://127.0.0.1:8080/yubiauth/users/1/yubikeys --data "yubikey=ccccccccccce"

####Response
Returns an empty response with status **204 No Content** on success.

###View a YubiKey
####Resource

    GET http://<host>/yubiauth/user/<id-or-username>/yubikeys/<prefix>

or

    GET http://<host>/yubiauth/yubikeys/<prefix>

####Request
A YubiKey can be accessed either via a user to which is is assigned, or directly
via its prefix alone. Note that trying to access an existing YubiKey (correct prefix)
via a user to which it is NOT assigned will result in a 404 Not Found.

**Example:**

    curl http://127.0.0.1:8080/yubiauth/users/1/yubikeys/ccccccccccce
    
or

    curl http://127.0.0.1:8080/yubiauth/yubikeys/ccccccccccce

####Response
Returns a JSON representation of the YubiKey:

    {
        "attributes": {},
        "prefix": "ccccccccccce",
        "enabled": true,
        "id": 53
    }

###Unassigning a YubiKey for a User
####Resource

    DELETE http://<host>/yubiauth/user/<id-or-username>/yubikeys/<prefix>

or

    POST http://<host>/yubiauth/user/<id-or-username>/yubikeys/<prefix>/delete

####Request
Unassigning a YubiKey for a User to which it is assigned is done by sending a 
HTTP DELETE request to it. NOTE that the YubiKey will still exist in the system
retaining its enabled state as well as any attributes. A POST alternative is available.

**Example:**

    curl -X DELETE http://127.0.0.1:8080/yubiauth/users/41/yubikeys/ccccccccccce
    
or

    curl -X POST http://127.0.0.1:8080/yubiauth/users/41/yubikeys/ccccccccccce/delete

####Response
Returns an empty response with status **204 No Content** on success.

###Deleting a YubiKey
####Resource

    DELETE http://<host>/yubiauth/yubikeys/<prefix>

or

    POST http://<host>/yubiauth/yubikeys/<prefix>/delete

####Request
Deleting a YubiKey removes it together with any data it holds from the system, as well
as removing any assignment to it any Users may have.

**Example:**

    curl -X DELETE http://127.0.0.1:8080/yubiauth/yubikeys/ccccccccccce

or

    curl -X POST http://127.0.0.1:8080/yubiauth/yubikeys/ccccccccccce/delete

####Response
Returns an empty response with status **204 No Content** on success.

##Attributes
Both [Users](#users) and [YubiKeys](#yubikeys) have attributes. These are accessed by 
taking the path of the user or YubiKey and appending "/attributes" to the end, for example:

    http://127.0.0.1:8080/yubiauth/users/42/attributes

or

    http://127.0.0.1:8080/yubiauth/yubikeys/cccccccccccd/attributes
    
or

    http://127.0.0.1:8080/yubiauth/users/42/yubikeys/cccccccccccd/attributes

In the following requests, any of the above formats qualify as **attribute_base**.

###View attributes
####Resource

    GET http://<host>/yubiauth/<attribute_base>

####Request
**Example**:

    curl http://127.0.0.1:8080/yubiauth/users/42/attributes

####Response
A JSON object with key-values matching the attributes.

    {
        "full_name": "Ford Prefect"
        "email": "ford@example.com",
    }

###Set attribute
Sets the value of an attribute. If the attribute already exists, it will be overwritten.
####Resource

    POST http://<host>/yubiauth/<attribute_base>

####Request
**Parameters**
 * **key** - The key of the attribute to set **(required)**
 * **value** - The value of the attribute to set **(required)**

**Example**:

    curl http://127.0.0.1:8080/yubiauth/users/42/attributes --data "key=email&value=ford@example.com"

####Response
Returns an empty response with status **204 No Content** on success.

###Get attribute
Gets the value of a single attribute.

####Resource

    GET http://<host>/yubiauth/<attribute_base>/<key>

####Request
**Example:**

    curl http://127.0.0.1:8080/yubiauth/users/42/attributes/email

####Response
A JSON string, or null, for example:

    "ford@example.com"

###Unset/Delete attribute
Removes an attribute, if it exists.

####Resource

    DELETE http://<host>/yubiauth/<attribute_base>/<key>

or

    POST http://<host>/yubiauth/<attribute_base>/<key>/delete

####Request
Attributes are removed by sending a HTTP DELETE request (POST alternative 
available).

**Example:**

    curl -X DELETE http://127.0.0.1:8080/yubiauth/users/42/attributes/email

####Response
Returns an empty response with status **204 No Content**.

##Authentication
Validate user credentials. Also see Validating a users password and/or YubiKey
under [Users](#users).

###Authenticate a user
Gets a user if the provided credentials are valid and sufficient to 
authenticate the user.

####Resource

    GET or POST http://<host>/yubiauth/authenticate

####Request
**Parameters**
 * **username** - The username of the user to authenticate **(required)**
 * **password** - The users password **(required)**
 * **otp** - A valid OTP from a YubiKey that is assigned to the user **(optional)**

**Example:**

    curl http://127.0.0.1:8080/yubiauth/authenticate --data "username=trillian&password=foo"

####Response
If the given parameters are valid, a JSON object describing the user is returned
(the same as accessing the user via /users/<id-or-username>). If not, an error 
is generated. For example:

    {
        "attributes": {
            "full_name": "Tricia Marie McMillan"
        },
        "id": 41,
        "name": "trillian"
    }
