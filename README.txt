Place your catalog project in this directory.

Project 2 : Item Catalog

This project develops an application "Sports Catalog App" that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

How to start

Step 1.	Follow all instructions to download and install Vagrant and VirtualBox in the previous lessons.
Step 2. Clone the fullstack-nanodegree-vm
Step 2. Open the shell prompt(terminal) and follow the below steps.
Step 3.	Bring the virtual machine online using the "vagrant up" command
Step 4.	Then log into it with "vagrant ssh".
Step 5.	Next install postgresql to run database commands.
Step 6. Run the "Project2_databaseSetup.py" file to create the required table structures namely Users, Catagory and Item.
Step 7. Add sample/ dummy data to the database by running the "Project2_data.py".
Step 8. Now code your flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM)
Step 9. Run your application within the VM (python/vagrant/catalog/Catalog.py)
Step 10. Access and test your application by visiting http://localhost:5000 locally.