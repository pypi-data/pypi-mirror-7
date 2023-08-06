GLAMS
=====

:Title:    
    GLAMS (Gandhi Lab Animal Management System)

:Author:       
    Kyle Ellefsen

:Date:
    2014.06.13

:Description:  
    This program creates a MySQL database containing mouse colony information. It also contains a web server which, when launched, allows users to retrieve and update information on the database. 


INSTALLATION FOR WINDOWS
========================

#. Install MySQL (for `windows <http://dev.mysql.com/downloads/windows/installer/>`_.)

   - Install the Developer version.
   - Choose ``Sever Machine`` when prompted for 'server configuration type'.
   - Choose ``Enable TCP/IP Networking`` if you would like to access GLAMS from other computers.
   - Leave the port number as the default ``3306``. 
   - Keep ``Open firewall port for network access`` checked.
   - Use your lab password as the ``MySQL Root Password``.
   - Add a user.  
   - Set 'host' to be ``<All Hosts (%)>``. 
   - Set 'Role' as ``DB Admin``.  
   - Leave authentication as ``MySQL``.  This user account will be in GLAMS to communicate with MySQL, and it will be saved as plaintext, so make sure it is a password you don't use for anything else. Remember it for a later step.
   - Run Windows Service as a Standard System Account. This automatically starts MySQL on Windows startup.
#. Install GLAMS using the `installer <https://db.tt/pKfWCj4V>`_.
#. Run glams by clicking the new icon on your desktop.
#. Open a browser, go to http://localhost/, enter the user and password. 
#. Restart glams and refresh your browser.
#. Login as admin (password is 'password') and create a user. Sign out and sign in as that user.

INSTALLATION FOR LINUX AND MAC OSX
==================================
I have not tested installation on these systems.

#. Install and run MySQL
#. Install the latest version of Python 2 (`2.7.6 <http://www.python.org/getit/releases/2.7.6/>`_. as of 2013.12.17) 
#. Install pip (instructions at `pip-installer.org <http://www.pip-installer.org/en/latest/installing.html>`_.)
#. Install `lxml <https://pypi.python.org/pypi/lxml/2.3>`_.
#. Install GLAMS. In a command line, change directory to where pip.py is installed. Then type::

    pip install glams


#. In a command line, change directory to where glams is installed. Launch the GLAMS server by running::

    main.py


   in the glams directory.  
#. Open a browser, go to http://localhost/, enter the user and password. 
#. Restart glams and refresh your browser.
#. Login as admin (password is 'password') and create a user. Sign out and sign in as that user.

INSTRUCTIONS FOR GLAMS INTERFACE
================================

Also included in GLAMS is a package called glamsinterface.  This allows you to interact with the data stored on glams outside of the web browser.  For instance, if you have animals associated in glams with experiments, you can find all of the experiments done on a particular strain or on animals of a particular age.  You can set up another database with the data for those experiments and link the two databases.  This could help automate data analysis, allowing researchers to spend more time designing experiments and less time rearranging spreadsheet values.
   
TODO
=====
- Add full calendar functionality
- Save the column order when a user moves a column.
- add 'date audited' to each cage.  Create a button a user can push to confirm cage information.
- Add column with 'Days Since Possible Mating' in cage view.  If any mature male mice entered a cage with mature female mice, count down 21 days
- Add column "Days Since Birth" in cage view.


BUGS
====
- If viewing on the chrome web browser which has the google docs app installed, you can't view mouse or cage information.  This might be a chrome bug.
- Sometimes creates two 'housing' entries when dragging mouse from one cage to another. Very hard to replicate bug.

