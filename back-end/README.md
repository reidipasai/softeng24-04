# Back-end

## Backend framework

We use flask as our backend framework. To run the backend API you have to do the following:
```bash
cd apis && python3 -m REST.app
```

We use blueprints to organize our API's. All the blueprints available are listed in `app.py`.
In the `admin` subfolder, you can find all the API calls that can only be called by admins. There's a wrapper called
@role_required("role") in login/loginsystem to help with this task. In the `login` subfolder, you can find the `loginsystem.py`
file that contains the `register`, `login` and `logout` calls. Finally, in the `tollstations` subfolder, you can find all the API
calls that are meant for tollstations, like cost computation, pass analysis, etc.
The backend is always running at the port **9115** by default and **mustn't change**.

## Database
We use mongodb as our database. In order for everything to work, the database needs to run at port **27017**, because the app is currently a prototype,
the data is stored in a collection called **test**. Make sure to always open the database first and then run the backend API.
We use mongoengine for our queries, so anything else will be incompatible with what we currently have. We highly suggest you to install mongodb compass
for GUI interaction and always open the mongodb services(especially for MAC users) with `brew services start mongodb-community@{version}`.

## Requirements
We use mongodb as our database. In order to run the REST API and the database you need to install the [requirements](../requirements.txt) and access the
localhost from mongodb compass. The database is running by default on mongodb://localhost:27017/softeng24-04.
