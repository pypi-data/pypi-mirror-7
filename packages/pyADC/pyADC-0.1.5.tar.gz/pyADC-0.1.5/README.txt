=====
pyADC
=====

pyADC is an implementation of the Advanced Direct Connect (ADC) protocol for use on ADC-supported Direct Connect hubs. This module comes complete with protocol handler, SSL/TLS support, and event functions to handle all the data that would be sent back and forth for users to see/interact with.

I built this because there was no real working implementation of the ADC protocol for Python yet, the closest being python-adc. Which isn't finished and had absolutely no bearing on this project, this module is tested and working for all basic functions of the ADC protocol.

The few things this module does not yet have (planned for later releases) is Searching, Client-To-Client Connections and File Downloads.

Thanks To
=========

A very special thanks goes out to Orochi/Crispy for his help on understanding a few things that, without them, this library would not work at all, so thanks again my friend.

Install
=======

First things first, because this requires the tiger tree hash that ADC uses for basically everything, you need to install libmhash-dev on linux. I have yet to test this on Windows or Mac. If on Ubuntu/Debian based linux the install in terminal would be like this::

    sudo apt-get install libmhash-dev python-dev

Now, install python-mhash separately, because it no longer works with pip::

    wget http://labix.org/download/python-mhash/python-mhash-1.4.tar.gz
    tar -xzvf python-mhash-1.4.tar.gz
    cd python-mhash-1.4.tar.gz
    sudo python setup.py install

Once thats done, then use pip to install pyadc:: 

    sudo pip install pyadc

In case for some reason pip does not install the proper dependencies, they are as follows::

    tiger 0.3 - sudo pip install tiger
    enum34 1.0 - sudo pip install enum34

Examples
========

An example of how to use the module is below::
	
    #!/usr/bin/env python
	
    from pyadc.client import Clients
    
    def main():
        clientlist = Clients() # Create new instance of Client
        clientlist.makeclient("adcs://somehub.com:5000", "username", "somepass", "No files to share", events)
	
    if __name__ == "__main__":
        main()

Event Functions
---------------

The library supports various event functions, for those who do not know the text encased in '' is going to be what the library uses to call the function beside it. Function names can be anything i simply used the same name as the string so that it was easier. This is a standard dictionary with function names passed into it at start up. This should be set before attempting to connect. All events listed are currently supported::

    events = {
    'onconnected': onconnected, # parameter: hubaddress(string)
    'onconnecting': onconnecting, # parameter: hubaddress(string)
    'ondisconnected': ondisconnected, # parameter: hubaddress(string)
    'onjoin': onjoin, # parameters: hubaddress(string) and username(string)
    'onprivatemessage': onprivatemessage, # parameters: hubaddress(string), user(object), message(string)
    'onprivateemote': onprivateemote, # parameters: hubaddress(string), user(object), message(string)
    'onpublicmessage': onpublicmessage, # parameters: hubaddress(string), user(object), message(string)
    'onpublicemote': onpublicemote, # parameters: hubaddress(string), user(object), message(string)
    'onpart': onpart, # parameters: hubaddress(string), username(string)
    'onredirect': onredirect, # parameters: new hubaddress(string)
    'onpassword': onpassword, # parameters: hubaddress(string)
    'onstatusmessage': onstatusmessage, # parameters: hubaddress(string), status code(integer), status message(string)
    'onbadpass': onbadpass, # parameters: hubaddress(string)
    'ontopic': ontopic, # parameters: hubaddress(string), topic(string)
    'onhubname': onhubname # parameters: hubaddress(string), hubname(string)
    }
    cl.events = events

All the parameters listed beside each event in the comments, is the order in which the library will send them out. e.g.::

    def onprivatemessage(hubaddress, user, message):

Clients Class (Main Class)
--------------------------

The Clients class is used for multi-hub connections, it merely makes it so you can simply create a client through a single function call, rather then a group of settings, it does it all for you, this will still work with a single connection for those not wanting to type everything out. Below you will find the properties of the Clients class::

    clients.getclientbyaddress(hubaddress) # Retrieves the Client class of hubaddress, same as given to event functions
    clients.makeclient(address, username, password, description, events={}, owner="", pid="") Creates and returns new Client object, also issues connect().

Client Class
------------

The Client class is the class that every other class is tied into and is your main way of accessing all the information contained in the various classes, below are the variables and functions used in this class::

    client.clientinfo # variable to access the ClientInfo Class [Object]
    client.hubinfo # variable to access the HubInfo Class[Object]
    client.nicklist # Variable to access the NickList class and the findbyusername function [Object]
    client.sid # The Client's Session ID given by the hub upon connecting [String]
    client.isconnected # Variable to check if the client is connected or not [Boolean]
    client.debug # Variable to turn on/off the debug feature, shows all raw data going in and out of the library, default is False [Boolean]
    client.events # Dictionary of events, as described above for the library to call at certain points. [Dictionary]
    client.connect() # Start connection function
    client.disconnect() # Immediately close connection
    client.sendmainchatmessage(message, emote=False) # Send a message to the main public chat, emote defaults to false, set to true to send as /me command
    client.sendprivatemessagebyclass(user, message, emote=False) # Send a private message to user, this uses the user object and not a string username, emote defaults to false, set to true to send as /me command
    client.sendprivatemessage(username, message, emote=False) # Send private message to username given, this uses the string username instead of the user object, emote defaults to false, set to true to send as /me command
    client.sendprivatemainchatmessagebyclass(user, message) # Send a mainchat message to a specific user (only seen by that user) using the user object
    client.sendprivatemainchatmessage(username, message) # Send a mainchat message to a specific user (only seen by that user) using the string username
    

User Class
-----------

The library tracks all users in the hub using the user class, there are various ways to get the user class. The events onprivatemessage and onpublicmessage include the user object. If you require the user object and have only been given the username by the library simply do this::

    user = cl.nicklist.findbyusername(username)

If nothing is found it will return False, if only one matching it is found, it will return a single User cobject. If there are more then one found it will return a list of user objects.

The following are the variables you can find in the User object::

    user.ip # IPv4 address (Currently IPv6 is not supported) [String]
    user.port # IPv4 Port [Integer]
    user.sharesize # Share Size in bytes [Integer]
    user.sharedfiles # Number of Shared Files [Integer]
    user.tag # Client Identification
    user.maxuploadspeed # Maximum Uplod Speed in bits/sec [Integer]
    user.openslots # Number of Open slots user has [Integer]
    user.autoslots # Automatic slot allocator speed limit in bytes/sec [Integer]
    user.maxopenslots # Maximum number of slots open in automatic slot manager mode [Integer]
    user.email # User's email [String]
    user.username # Username of user, only used for display purposes [String]
    user.description # User's description [String]
    user.hubsnormal # Number of hubs user is unregistered in [Integer]
    user.hubsreg # Number of hubs user is registered in [Integer]
    user.hubsop # Number of hubs user is op in [Integer]
    user.hubsstatus # Protocol value of what users permissions are [Integer] see: http://adc.sourceforge.net/ADC.html#_inf (CT field) for more details
    user.sid # Session ID given to user from hub [String]
    user.cid # Client ID generated from Private ID of client [String]
    user.token # Token for Client to Client connections (Not yet supported) [String] 
    user.isoperator #  Variable if user is an operator in the hub or not [Boolean]
    user.ishidden # Variable is user is hidden in hub [Boolean]
    user.isaway # Variable if user is st to away [Boolean]
    user.isbot # Variable if user is a bot or not [Boolean]
    user.supportlist # List of protocols supported by client. [List]
    user.downloadlist # List of downloads (Currently not supported) [List]

HubInfo Class
-------------

The HubInfo class is a very small class that simply stores some information the hub sends, below is what it contains::

    hubinfo.hubsupports # List of protocols that the hub supports [List]
    hubinfo.hubname # Name of the hub [String]
    hubinfo.topic # Topic of the hub [String]
    hubinfo.hubversion # Version of the hub [String]
    hubinfo.lastmessage # Last message sent by the hub [String]

ClientInfo Class
----------------

The ClientInfo class is a support class that is responsible for generating PID's and CID's according to ADC protocol standards, and also looking up the WAN IP of the computer the script is running on. It is also responsible for holding some information, which can be found below::

    clientinfo.hostname # The Hostname of the hub without scheme or port number [String]
    clientinfo.do_ssl # Variable on whether or not the address given to the hubaddress function requires ssl/tls [Boolean]
    clientinfo.port # port given to the hubaddress function [Integer]
    clientinfo.username # Username to connect with [String]
    clientinfo.password # Password to send upon connecting [String]
    clientinfo.description # Description to set for user connecting [String]
    clientinfo.email # Email of user
    clientinfo.reconnectondisconnect # If disconnected reconnect [Boolean]
    clientinfo.share # Share size in bytes (default is clientinfo.ShareSize.Empty) [Integer]
    clientinfo.followredirects # Follow redirects if any are given to the library [Boolean]
    clientinfo.respondtorevconnecttome # Respond to Reverse Connect To Me's, always false, no support for this option yet [Boolean]
    clientinfo.clientport # To be used later for client-to-client connections, currently defaults to 1337 [Integer]
    clientinfo.client_pid # Private ID for client [String]
    clientinfo.client_cid # Client ID for client [String]
    clientinfo.hubaddress() # Function to either get or set the Hub Address to connect to. e.g. addy = clientinfo.hubaddress() or clientinfo.hubaddress("adcs://somehub.com:500")
    
    
