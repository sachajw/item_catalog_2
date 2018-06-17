# **Project 4: Item Catalog**

**by Sacha Wharton**

## **About**
This is the fourth project in the Udacity Full Stack Web Developer Nanodegree. The application is for adding books with there relevant details such as title, publisher, cover image and so forth with your favourite browser. It uses a third party login namely Google Sign-In which once signed in will then allow you to perform CRUD operations. A JSON endpoint has been provided to query book information.

## **Required Libraries and Dependencies**

Python 2.x (The Python executable should be in your default path, which the Python installer sets)
Flask Web Framework
Bootstrap
Vagrant
Virtual Box

A requirements.txt file has been created for all package dependencies.

## **Main Project Contents**

The project contains the following files and folders:
- ****static**** - all static content
- ****templates**** - all html templates
- ****database_setup.py**** - database creation
- ****project.py**** - main Python script to run the application

## **How to Run the Project**

- Install Oracle Virtualbox from [here](https://www.virtualbox.org/wiki/Downloads)
- Install Vagrant from [here](https://www.vagrantup.com/downloads.html)
- Use this link to configure and run the virtual machine     [here](https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/bc51d967-cb21-46f4-90ea-caf73439dc59/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0)
- Download the data from [here](https://github.com/sachajw/item_catalog_2.git) and copy the ****item_catalogue_2**** folder into the Vagrant directory
- Navigate to the Vagrant folder on the virtual machine
- Run pip install -r requirements.txt (this installs all the required packages)
- Run ****database_setup.py**** (this will create the sqlite3 database with all the relevant tables)
- Run ****project.py**** (this will start the webserver on port 5000)
- Browse to ****http://localhost:5000**** with your favourite browser

## **Extra Credit Description**

I have implemented CSRF to protect CRUD operations. I have decided to pull book cover images from Amazon by using there image location. I felt this would be a better use of resources should the database grow very large by not having to store the images in the database itself.

## **Miscellaneous**
I based the README on this template [forum](https://discussions.udacity.com/t/readme-files-in-project-1/23524)
I can recommend DB Browser for SQLite [here](http://sqlitebrowser.org/)