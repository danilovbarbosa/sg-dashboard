'''
Sets up navigation in the dashboard 
'''

from flask_nav import Nav
from flask_nav.elements import *

# To keep things clean, we keep our Flask-Nav instance in here. We will define
# frontend-specific navbars in the respective frontend, but it is also possible
# to put share navigational items in here.


nav = Nav()

nav.register_element('top', Navbar(
         Link('Home', dest='/'),
         )
    )