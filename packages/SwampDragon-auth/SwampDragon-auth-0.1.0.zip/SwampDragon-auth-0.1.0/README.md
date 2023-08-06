Swamp Dragon auth
=================

# Installation
```pip install swampdragon-auth```


# Django settings.py file
Add the following code to your settings file:

    SOCKJS_CLASSES = (
        ('swampdragon_auth.socketconnection.HttpDataConnection', '/data'),
    )


To access a signed in user in your router:

    self.connection.get_user()
    
or alternatively

    self.connection.user
    
The results are the same.
