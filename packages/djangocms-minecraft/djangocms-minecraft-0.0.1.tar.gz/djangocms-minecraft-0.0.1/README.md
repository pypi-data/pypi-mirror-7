Djangocms-Minecraft
======

With Minecraft 1.9 came a shiny new tool to allow native status querying in vanilla Minecraft servers.
This is a simple set of plugins intended for use with Django-CMS, designed to aid in retrieving any data from the servers.  
Much of this code comes from Dinnerbone's amazing source (..thank you dude!) that he has graciously left as "fully open".

See it in action: [http://www.thenetyeti.com/status/](http://www.thenetyeti.com/status/)

Protocol documention: [http://dinnerbone.com/blog/2011/10/14/minecraft-19-has-rcon-and-query/](http://dinnerbone.com/blog/2011/10/14/minecraft-19-has-rcon-and-query/)

Usage
-----------

Install with pip:

    pip install djangocms-minecraft
    
Or, optionally, install the development version:
    
    pip install git+https://git@bitbucket.org/oddotterco/djangocms-minecraft.git#egg=djangocms-minecraft

Then, in your project's settings.py file, add 'djangocms_minecraft' to the INSTALLED_APPS like so:

    INSTALLED_APPS += ('djangocms_minecraft',)
    
Finally, syncdb, migrate your project, and then simply add the plugins to pages as desired.  
They will show up in both a text plugin's plugins list as well as the page plugins list, under the header "Minecraft".

Rights
-----------
As with Dinerbone's original code - Fully open. Go wild.  Let us know what you do with it and PLEASE feel free to fork and pull-request!
