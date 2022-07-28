Actinia Basics
==============

Actinia REST API documentation
------------------------------

Actinia is fully documented using the OpenAPI standard[^1], better known
as swagger[^2]. The JSON definition of the API can be accessed here:

 <https://actinia.mundialis.de/latest/swagger.json>

<!---
commented out because of 502 Bad Gateway
The full API documentation is available here:

 <https://actinia.mundialis.de/api_docs/>
--->

To generate a readable documentation out of the swagger.json file, the
spectacle tool can be used:

```bash
 # Download the latest swagger definition from the actinia service
 wget  https://actinia.mundialis.de/latest/swagger.json -O /tmp/actinia.json

 # Run spectacle docker image to generate the HTML documentation
 docker run -v /tmp:/tmp -t sourcey/spectacle spectacle /tmp/actinia.json -t /tmp

 # Start Firefox to show the documentation
 firefox /tmp/index.html
```

The petstore swagger UI creator[^3] can be used to show all available
REST API calls and all response models in a convenient way.


User, user-roles and user-groups
--------------------------------

Actinia uses the concept of users, user-roles and user-groups to manage
the access to the actinia databases and API calls. A single user has
always a specific user role and can be member of one single user-group.

The following user-roles are supported:

 1.  

     superadmin:

         -   Can create, modify and delete users with all user-roles
         -   Has access to all API calls and read/write access to all
             databases

 2.  

     admin:

         -   Can create, modify and delete locations in a user specific
             database
         -   Can access all API calls
         -   Can create, modify and delete users with the maximum
             user-role *user* of the same user group
         -   Has access to persistent databases that were granted by a
             superadmin

 3.  

     user:

         -   Can run computational tasks in ephemeral and user specific
             databases
         -   Can create, modify and delete mapsets in user
             specific databases
         -   Has limited access to API calls
         -   Can not create, modify or delete users
         -   Has access to persistent databases that were granted by a
             superadmin

 4.  

     guest:

         -   Has very limited access to API calls
         -   Can not create, modify or delete mapsets
         -   Can not create, modify or delete users
         -   Has access to persistent databases that were granted by a
             superadmin

Overview table:

| task | superadmin | admin | user | guest |notes |
|------|------------|-------|------|-------|------|
| amount raster cells is unlimited | y | y | limited, selected via redis | limited, selected via redis | - |
| database access is unlimited                              | y         | only to persistent databases that were granted by a superadmin | limited, defined in redis | limited, defined in redis | - |
| location/mapset access is unlimited  | y | y | can create, modify and delete mapsets in user specific databases, defined in redis | has access to persistent databases that were granted by a superadmin, defined in redis | - |
|module access is unlimited  | y | y | can run computational tasks in ephemeral and user specific databases | has very limited access to API calls | - |
| get, create, delete a single user | y | users with the maximum user-role user of the same user group | n | n | Only normal users (role=user can be created) |

In the file actinia.cfg, limits and more can be defined:

```bash
[LIMITS]
max_cell_limit = 2000000
process_time_limt = 60
process_num_limit = 20
number_of_workers = 3
```

The Actinia databases
---------------------

Actinia manages GRASS GIS locations in its *persistent database*. User
are not permitted to modify data in the actinia persistent database, but
can access all data read-only for processing and visualization. Data in
the persistent database can only be accessed via HTTP GET API calls.

The user can either process data in an *ephemeral databases*, that will
be removed after the processing is finished, or in a *user specific
database*. A user specific database is persistent, only visible to users
of the same user-group and can contain any data the user has
imported. The user can read-access all data from the persistent database
while running analysis in the ephemeral database or user specific
database.

**Summary**

 1.  

     Persistent database:

         -   Read only database with locations and mapsets that can be
             used as processing environment and data source
         -   Data can only be accessed using HTTP GET API calls

 2.  

     Ephemeral database:

         -   All processing is performed in ephemeral databases for
             performance and security reasons
         -   Ephemeral databases are created for all API calls and
             removed after the processing is finished
         -   Ephemeral databases use persistent databases as processing
             environments to access required data from mapsets in
             persistent locations

 3.  

     User specific databases:

         -   Persistent databases that can be created and modified by a
             specific user group
         -   The base for a location in a user specific database can be
             a location from a persistent database, however mapsets
             names must be unique.
         -   A user group can only access a single database with any
             number of locations

**Footnotes**

[^1]: <https://www.openapis.org/>

[^2]: <https://swagger.io>

[^3]: <https://petstore.swagger.io>
