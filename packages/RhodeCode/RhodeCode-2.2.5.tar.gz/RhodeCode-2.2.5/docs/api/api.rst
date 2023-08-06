.. _api:

===
API
===


Starting from RhodeCode version 1.2 a simple API was implemented.
There's a single schema for calling all api methods. API is implemented
with JSON protocol both ways. An url to send API request to RhodeCode is
<your_server>/_admin/api

API ACCESS FOR WEB VIEWS
++++++++++++++++++++++++

API access can also be turned on for each web view in RhodeCode that is
decorated with `@LoginRequired` decorator. To enable API access simple change
the standard login decorator to `@LoginRequired(api_access=True)`.

To make this operation easier, starting from version 1.7.0 there's a white list
of views that will have API access enabled. Simply edit `api_access_controllers_whitelist`
option in your .ini file, and define views that should have API access enabled.
Following example shows how to enable API access to patch/diff raw file and archive
in RhodeCode::

    api_access_controllers_whitelist =
        ChangesetController:changeset_patch,
        ChangesetController:changeset_raw,
        FilesController:raw,
        FilesController:archivefile


After this change, a rhodecode view can be accessed without login by adding a
GET parameter `?api_key=<api_key>` to url. For example to access the raw diff::

 http://<server>/<repo>/changeset-diff/<sha>?api_key=<key>

By default this is only enabled on RSS/ATOM feed views. Exposing raw diffs is a
good way to integrate with 3rd party services like code review, or build farms
that could download archives.


API ACCESS
++++++++++

All clients are required to send JSON-RPC spec JSON data::

    {
        "id:"<id>",
        "api_key":"<api_key>",
        "method":"<method_name>",
        "args":{"<arg_key>":"<arg_val>"}
    }

Example call for autopulling remotes repos using curl::
    curl https://server.com/_admin/api -X POST -H 'content-type:text/plain' --data-binary '{"id":1,"api_key":"xe7cdb2v278e4evbdf5vs04v832v0efvcbcve4a3","method":"pull","args":{"repo":"CPython"}}'

Simply provide
 - *id* A value of any type, which is used to match the response with the request that it is replying to.
 - *api_key* for access and permission validation.
 - *method* is name of method to call
 - *args* is an key:value list of arguments to pass to method

.. note::

    api_key can be found in your user account page


RhodeCode API will return always a JSON-RPC response::

    {
        "id":<id>, # matching id sent by request
        "result": "<result>"|null, # JSON formatted result, null if any errors
        "error": "null"|<error_message> # JSON formatted error (if any)
    }

All responses from API will be `HTTP/1.0 200 OK`, if there's an error while
calling api *error* key from response will contain failure description
and result will be null.


API CLIENT
++++++++++

From version 1.4 RhodeCode adds a script that allows to easily
communicate with API. After installing RhodeCode a `rhodecode-api` script
will be available.

To get started quickly simply run::

  rhodecode-api --save-config --apikey=<youapikey> --apihost=<rhodecode host>

This will create a file named .config in users HOME directory, storing
json config file with credentials. You can skip this step and always provide
both of the arguments to be able to communicate with server


after that simply run any api command for example get_repo::

    rhodecode-api get_repo

    Calling method get_repo => http://127.0.0.1:5000
    Server response
    "Missing non optional `repoid` arg in JSON DATA"

Ups looks like we forgot to add an argument

Let's try again now giving the repoid as parameters::

    rhodecode-api get_repo repoid:rhodecode

    Calling method get_repo => http://127.0.0.1:5000
    Server response
    {
        <json data>
    }

Optionally user can specify `--format` param to change the output to pure JSON::

    rhodecode-api --format=json get_repo repoid:rhodecode

In such case only output that this function shows is pure JSON, we can use that
and pip output to some json formatter::

    rhodecode-api --format=json get_repo repoid:rhodecode | python -m json.tool


API METHODS
+++++++++++

Each method by default required following arguments::

    id :      "<id_for_response>"
    api_key : "<api_key>"
    method :  "<method name>"
    args :    {}

Use each **param** from docs and put it in args, Optional parameters
are not required in args::

    args: {"repoid": "rhodecode"}


--- API DEFS ---

.. py:function:: pull(apiuser, repoid)
   Triggers a pull from remote location on given repo. Can be used to
   automatically keep remote repos up to date. This command can be executed
   only using api_key belonging to user with admin rights

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int

   OUTPUT::

     id : <id_given_in_input>
     result : {
       "msg": "Pulled from `<repository name>`"
       "repository": "<repository name>"
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "Unable to pull changes from `<reponame>`"
     }

.. py:function:: rescan_repos(apiuser, remove_obsolete=<Optional:False>)
   Triggers rescan repositories action. If remove_obsolete is set
   than also delete repos that are in database but not in the filesystem.
   aka "clean zombies". This command can be executed only using api_key
   belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param remove_obsolete: deletes repositories from
       database that are not found on the filesystem
   :type remove_obsolete: Optional(bool)

   OUTPUT::

     id : <id_given_in_input>
     result : {
       'added': [<added repository name>,...]
       'removed': [<removed repository name>,...]
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       'Error occurred during rescan repositories action'
     }

.. py:function:: invalidate_cache(apiuser, repoid)
   Invalidate cache for repository.
   This command can be executed only using api_key belonging to user with admin
   rights or regular user that have write or admin or write access to repository.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int

   OUTPUT::

     id : <id_given_in_input>
     result : {
       'msg': Cache for repository `<repository name>` was invalidated,
       'repository': <repository name>
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       'Error occurred during cache invalidation action'
     }

.. py:function:: lock(apiuser, repoid, locked=<Optional:None>, userid=<Optional:<OptionalAttr:apiuser>>)
   Set locking state on given repository by given user. If userid param
   is skipped, then it is set to id of user whos calling this method.
   If locked param is skipped then function shows current lock state of
   given repo. This command can be executed only using api_key belonging
   to user with admin rights or regular user that have admin or write
   access to repository.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param locked: lock state to be set
   :type locked: Optional(bool)
   :param userid: set lock as user
   :type userid: Optional(str or int)

   OUTPUT::

     id : <id_given_in_input>
     result : {
       'repo': '<reponame>',
       'locked': <bool: lock state>,
       'locked_since': <int: lock timestamp>,
       'locked_by': <username of person who made the lock>,
       'lock_state_changed': <bool: True if lock state has been changed in this request>,
       'msg': 'Repo `<reponame>` locked by `<username>` on <timestamp>.'
       or
       'msg': 'Repo `<repository name>` not locked.'
       or
       'msg': 'User `<user name>` set lock state for repo `<repository name>` to `<new lock state>`'
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       'Error occurred locking repository `<reponame>`
     }

.. py:function:: get_locks(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)
   Get all repositories with locks for given userid, if
   this command is runned by non-admin account userid is set to user
   who is calling this method, thus returning locks for himself.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param userid: User to get locks for
   :type userid: Optional(str or int)

   OUTPUT::

     id : <id_given_in_input>
     result : {
       [repo_object, repo_object,...]
     }
     error :  null

.. py:function:: get_ip(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)
   Shows IP address as seen from RhodeCode server, together with all
   defined IP addresses for given user. If userid is not passed data is
   returned for user who's calling this function.
   This command can be executed only using api_key belonging to user with
   admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param userid: username to show ips for
   :type userid: Optional(str or int)

   OUTPUT::

       id : <id_given_in_input>
       result : {
                    "server_ip_addr": "<ip_from_clien>",
                    "user_ips": [
                                   {
                                      "ip_addr": "<ip_with_mask>",
                                      "ip_range": ["<start_ip>", "<end_ip>"],
                                   },
                                   ...
                                ]
       }

.. py:function:: show_ip(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)
   Shows IP address as seen from RhodeCode server, together with all
   defined IP addresses for given user. If userid is not passed data is
   returned for user who's calling this function.
   This command can be executed only using api_key belonging to user with
   admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param userid: username to show ips for
   :type userid: Optional(str or int)

   OUTPUT::

       id : <id_given_in_input>
       result : {
                    "server_ip_addr": "<ip_from_clien>",
                    "user_ips": [
                                   {
                                      "ip_addr": "<ip_with_mask>",
                                      "ip_range": ["<start_ip>", "<end_ip>"],
                                   },
                                   ...
                                ]
       }

.. py:function:: get_server_info(apiuser)
   return server info, including RhodeCode version and installed packages

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser

   OUTPUT::

     id : <id_given_in_input>
     result : {
       'modules': [<module name>,...]
       'py_version': <python version>,
       'platform': <platform type>,
       'rhodecode_version': <rhodecode version>
     }
     error :  null

.. py:function:: get_user(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)
   Get's an user by username or user_id, Returns empty result if user is
   not found. If userid param is skipped it is set to id of user who is
   calling this method. This command can be executed only using api_key
   belonging to user with admin rights, or regular users that cannot
   specify different userid than theirs

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param userid: user to get data for
   :type userid: Optional(str or int)

   OUTPUT::

       id : <id_given_in_input>
       result: None if user does not exist or
               {
                   "user_id" :     "<user_id>",
                   "api_key" :     "<api_key>",
                   "api_keys":     "[<list of all api keys including additional ones>]"
                   "username" :    "<username>",
                   "firstname":    "<firstname>",
                   "lastname" :    "<lastname>",
                   "email" :       "<email>",
                   "emails":       "[<list of all emails including additional ones>]",
                   "ip_addresses": "[<ip_addresse_for_user>,...]",
                   "active" :      "<bool: user active>",
                   "admin" :       "<bool: user is admin>",
                   "extern_name" : "<extern_name>",
                   "extern_type" : "<extern type>
                   "last_login":   "<last_login>",
                   "permissions": {
                       "global": ["hg.create.repository",
                                  "repository.read",
                                  "hg.register.manual_activate"],
                       "repositories": {"repo1": "repository.none"},
                       "repositories_groups": {"Group1": "group.read"}
                    },
               }

       error:  null

.. py:function:: get_users(apiuser)
   Lists all existing users. This command can be executed only using api_key
   belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser

   OUTPUT::

       id : <id_given_in_input>
       result: [<user_object>, ...]
       error:  null

.. py:function:: create_user(apiuser, username, email, password=<Optional:''>, firstname=<Optional:''>, lastname=<Optional:''>, active=<Optional:True>, admin=<Optional:False>, extern_name=<Optional:'rhodecode'>, extern_type=<Optional:'rhodecode'>)
   Creates new user. Returns new user object. This command can
   be executed only using api_key belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param username: new username
   :type username: str or int
   :param email: email
   :type email: str
   :param password: password
   :type password: Optional(str)
   :param firstname: firstname
   :type firstname: Optional(str)
   :param lastname: lastname
   :type lastname: Optional(str)
   :param active: active
   :type active: Optional(bool)
   :param admin: admin
   :type admin: Optional(bool)
   :param extern_name: name of extern
   :type extern_name: Optional(str)
   :param extern_type: extern_type
   :type extern_type: Optional(str)


   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "created new user `<username>`",
                 "user": <user_obj>
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "user `<username>` already exist"
       or
       "email `<email>` already exist"
       or
       "failed to create user `<username>`"
     }

.. py:function:: update_user(apiuser, userid, username=<Optional:None>, email=<Optional:None>, password=<Optional:None>, firstname=<Optional:None>, lastname=<Optional:None>, active=<Optional:None>, admin=<Optional:None>, extern_type=<Optional:None>, extern_name=<Optional:None>)
   updates given user if such user exists. This command can
   be executed only using api_key belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param userid: userid to update
   :type userid: str or int
   :param username: new username
   :type username: str or int
   :param email: email
   :type email: str
   :param password: password
   :type password: Optional(str)
   :param firstname: firstname
   :type firstname: Optional(str)
   :param lastname: lastname
   :type lastname: Optional(str)
   :param active: active
   :type active: Optional(bool)
   :param admin: admin
   :type admin: Optional(bool)
   :param extern_name:
   :type extern_name: Optional(str)
   :param extern_type:
   :type extern_type: Optional(str)


   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "updated user ID:<userid> <username>",
                 "user": <user_object>,
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to update user `<username>`"
     }

.. py:function:: delete_user(apiuser, userid)
   deletes givenuser if such user exists. This command can
   be executed only using api_key belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param userid: user to delete
   :type userid: str or int

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "deleted user ID:<userid> <username>",
                 "user": null
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete user ID:<userid> <username>"
     }

.. py:function:: get_user_group(apiuser, usergroupid)
   Gets an existing user group. This command can be executed only
   using api_key belonging to user with admin rights or user who has at
   least read access to user group.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param usergroupid: id of user_group to edit
   :type usergroupid: str or int

   OUTPUT::

       id : <id_given_in_input>
       result : None if group not exist
        {
           "users_group_id" : "<id>",
           "group_name" :     "<groupname>",
           "active":          "<bool>",
           "users" :  [<user_obj>,...],
           "members" : [
                         {
                           "name":        "<username>",
                           "permission" : "usergroup.(read|write|admin)",
                           "origin":      "<permission|owner|super-admin>",
                           "type" :       "user",
                         },
                         ...
                         {
                           "name":        "<usergroup name>",
                           "permission" : "usergroup.(read|write|admin)",
                           "origin":      "<permission|owner|super-admin>",
                           "type" :       "user",
                         },
                       ...
           ]
        }
       error : null

.. py:function:: get_user_groups(apiuser)
   Lists all existing user groups. This command can be executed only using
   api_key belonging to user with admin rights or user who has at least
   read access to user group.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser

   OUTPUT::

       id : <id_given_in_input>
       result : [<user_group_obj>,...]
       error : null

.. py:function:: create_user_group(apiuser, group_name, description=<Optional:''>, owner=<Optional:<OptionalAttr:apiuser>>, active=<Optional:True>)
   Creates new user group. This command can be executed only using api_key
   belonging to user with admin rights or an user who has create user group
   permission

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param group_name: name of new user group
   :type group_name: str
   :param description: group description
   :type description: str
   :param owner: owner of group. If not passed apiuser is the owner
   :type owner: Optional(str or int)
   :param active: group is active
   :type active: Optional(bool)

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg": "created new user group `<groupname>`",
                 "user_group": <user_group_object>
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "user group `<group name>` already exist"
       or
       "failed to create group `<group name>`"
     }

.. py:function:: update_user_group(apiuser, usergroupid, group_name=<Optional:''>, description=<Optional:''>, owner=<Optional:None>, active=<Optional:True>)
   Updates given usergroup.  This command can be executed only using api_key
   belonging to user with admin rights or an admin of given user group

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param usergroupid: id of user group to update
   :type usergroupid: str or int
   :param group_name: name of new user group
   :type group_name: str
   :param description: group description
   :type description: str
   :param owner: owner of group.
   :type owner: Optional(str or int)
   :param active: group is active
   :type active: Optional(bool)

   OUTPUT::

     id : <id_given_in_input>
     result : {
       "msg": 'updated user group ID:<user group id> <user group name>',
       "user_group": <user_group_object>
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to update user group `<user group name>`"
     }

.. py:function:: delete_user_group(apiuser, usergroupid)
   Delete given user group by user group id or name.
   This command can be executed only using api_key
   belonging to user with admin rights or an admin of given user group

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param usergroupid:
   :type usergroupid: int

   OUTPUT::

     id : <id_given_in_input>
     result : {
       "msg": "deleted user group ID:<user_group_id> <user_group_name>"
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete user group ID:<user_group_id> <user_group_name>"
       or
       "RepoGroup assigned to <repo_groups_list>"
     }

.. py:function:: add_user_to_user_group(apiuser, usergroupid, userid)
   Adds a user to a user group. If user exists in that group success will be
   `false`. This command can be executed only using api_key
   belonging to user with admin rights  or an admin of given user group

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param usergroupid:
   :type usergroupid: int
   :param userid:
   :type userid: int

   OUTPUT::

     id : <id_given_in_input>
     result : {
         "success": True|False # depends on if member is in group
         "msg": "added member `<username>` to user group `<groupname>` |
                 User is already in that group"

     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to add member to user group `<user_group_name>`"
     }

.. py:function:: remove_user_from_user_group(apiuser, usergroupid, userid)
   Removes a user from a user group. If user is not in given group success will
   be `false`. This command can be executed only
   using api_key belonging to user with admin rights or an admin of given user group

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param usergroupid:
   :param userid:


   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "success":  True|False,  # depends on if member is in group
                 "msg": "removed member <username> from user group <groupname> |
                         User wasn't in group"
               }
       error:  null

.. py:function:: get_repo(apiuser, repoid)
   Gets an existing repository by it's name or repository_id. Members will return
   either users_group or user associated to that repository. This command can be
   executed only using api_key belonging to user with admin
   rights or regular user that have at least read access to repository.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int

   OUTPUT::

     id : <id_given_in_input>
     result :
       {
           "repo_id" :          "<repo_id>",
           "repo_name" :        "<reponame>"
           "repo_type" :        "<repo_type>",
           "clone_uri" :        "<clone_uri>",
           "enable_downloads":  "<bool>",
           "enable_locking":    "<bool>",
           "enable_statistics": "<bool>",
           "private":           "<bool>",
           "created_on" :       "<date_time_created>",
           "description" :      "<description>",
           "landing_rev":       "<landing_rev>",
           "last_changeset":    {
                                  "author":   "<full_author>",
                                  "date":     "<date_time_of_commit>",
                                  "message":  "<commit_message>",
                                  "raw_id":   "<raw_id>",
                                  "revision": "<numeric_revision>",
                                  "short_id": "<short_id>"
                                }
           "owner":             "<repo_owner>",
           "fork_of":           "<name_of_fork_parent>",
           "members" :     [
                             {
                               "name":        "<username>",
                               "permission" : "repository.(read|write|admin)",
                               "origin":      "<permission|owner|super-admin>",
                               "type" :       "user",
                             },
                             ...
                             {
                               "name":        "<usergroup name>",
                               "permission" : "repository.(read|write|admin)",
                               "origin":      "<permission|owner|super-admin>",
                               "type" :       "user",
                             },
                             ...
                           ]
            "followers":   [<user_obj>, ...]
            ]
       }
     error :  null

.. py:function:: get_repos(apiuser)
   Lists all existing repositories. This command can be executed only using
   api_key belonging to user with admin rights or regular user that have
   admin, write or read access to repository.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser

   OUTPUT::

       id : <id_given_in_input>
       result: [
                 {
                   "repo_id" :          "<repo_id>",
                   "repo_name" :        "<reponame>"
                   "repo_type" :        "<repo_type>",
                   "clone_uri" :        "<clone_uri>",
                   "private": :         "<bool>",
                   "created_on" :       "<datetimecreated>",
                   "description" :      "<description>",
                   "landing_rev":       "<landing_rev>",
                   "owner":             "<repo_owner>",
                   "fork_of":           "<name_of_fork_parent>",
                   "enable_downloads":  "<bool>",
                   "enable_locking":    "<bool>",
                   "enable_statistics": "<bool>",
                 },
                 …
               ]
       error:  null

.. py:function:: get_repo_nodes(apiuser, repoid, revision, root_path, ret_type=<Optional:'all'>)
   returns a list of nodes and it's children in a flat list for a given path
   at given revision. It's possible to specify ret_type to show only `files` or
   `dirs`.  This command can be executed only using api_key belonging to
   user with admin rights or regular user that have at least read access to repository.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param revision: revision for which listing should be done
   :type revision: str
   :param root_path: path from which start displaying
   :type root_path: str
   :param ret_type: return type 'all|files|dirs' nodes
   :type ret_type: Optional(str)


   OUTPUT::

       id : <id_given_in_input>
       result: [
                 {
                   "name" :        "<name>"
                   "type" :        "<type>",
                 },
                 …
               ]
       error:  null

.. py:function:: create_repo(apiuser, repo_name, owner=<Optional:<OptionalAttr:apiuser>>, repo_type=<Optional:'hg'>, description=<Optional:''>, private=<Optional:False>, clone_uri=<Optional:None>, landing_rev=<Optional:'rev:tip'>, enable_statistics=<Optional:False>, enable_locking=<Optional:False>, enable_downloads=<Optional:False>, copy_permissions=<Optional:False>)
   Creates a repository. If repository name contains "/", all needed repository
   groups will be created. For example "foo/bar/baz" will create groups
   "foo", "bar" (with "foo" as parent), and create "baz" repository with
   "bar" as group. This command can be executed only using api_key
   belonging to user with admin rights or regular user that have create
   repository permission. Regular users cannot specify owner parameter

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repo_name: repository name
   :type repo_name: str
   :param owner: user_id or username
   :type owner: Optional(str)
   :param repo_type: 'hg' or 'git'
   :type repo_type: Optional(str)
   :param description: repository description
   :type description: Optional(str)
   :param private:
   :type private: bool
   :param clone_uri:
   :type clone_uri: str
   :param landing_rev: <rev_type>:<rev>
   :type landing_rev: str
   :param enable_locking:
   :type enable_locking: bool
   :param enable_downloads:
   :type enable_downloads: bool
   :param enable_statistics:
   :type enable_statistics: bool
   :param copy_permissions: Copy permission from group that repository is
       beeing created.
   :type copy_permissions: bool

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg": "Created new repository `<reponame>`",
                 "success": true,
                 "task": "<celery task id or None if done sync>"
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
        'failed to create repository `<repo_name>`
     }

.. py:function:: add_field_to_repo(apiuser, repoid, key, label=<Optional:''>, description=<Optional:''>)
   Add extra field to a repository.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param key: unique field key for this repository
   :type key: str
   :param label:
   :type label: Optional(str)
   :param description:
   :type description: Optional(str)

.. py:function:: remove_field_from_repo(apiuser, repoid, key)
   Remove extra field from a repository. This command can be executed only
   using api_key belonging to user with admin rights or regular user that
   have admin access to repository.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param key: unique field key for this repository
   :type key: str

.. py:function:: update_repo(apiuser, repoid, name=<Optional:None>, owner=<Optional:<OptionalAttr:apiuser>>, group=<Optional:None>, description=<Optional:''>, private=<Optional:False>, clone_uri=<Optional:None>, landing_rev=<Optional:'rev:tip'>, enable_statistics=<Optional:False>, enable_locking=<Optional:False>, enable_downloads=<Optional:False>)
   Updates repo

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param name:
   :param owner:
   :param group:
   :param description:
   :param private:
   :param clone_uri:
   :param landing_rev:
   :param enable_statistics:
   :param enable_locking:
   :param enable_downloads:

.. py:function:: fork_repo(apiuser, repoid, fork_name, owner=<Optional:<OptionalAttr:apiuser>>, description=<Optional:''>, copy_permissions=<Optional:False>, private=<Optional:False>, landing_rev=<Optional:'rev:tip'>)
   Creates a fork of given repo. In case of using celery this will
   immidiatelly return success message, while fork is going to be created
   asynchronous. This command can be executed only using api_key belonging to
   user with admin rights or regular user that have fork permission, and at least
   read access to forking repository. Regular users cannot specify owner parameter.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param fork_name:
   :param owner:
   :param description:
   :param copy_permissions:
   :param private:
   :param landing_rev:

   INPUT::

       id : <id_for_response>
       api_key : "<api_key>"
       args:     {
                   "repoid" :          "<reponame or repo_id>",
                   "fork_name":        "<forkname>",
                   "owner":            "<username or user_id = Optional(=apiuser)>",
                   "description":      "<description>",
                   "copy_permissions": "<bool>",
                   "private":          "<bool>",
                   "landing_rev":      "<landing_rev>"
                 }

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg": "Created fork of `<reponame>` as `<forkname>`",
                 "success": true,
                 "task": "<celery task id or None if done sync>"
               }
       error:  null

.. py:function:: delete_repo(apiuser, repoid, forks=<Optional:''>)
   Deletes a repository. This command can be executed only using api_key belonging
   to user with admin rights or regular user that have admin access to repository.
   When `forks` param is set it's possible to detach or delete forks of deleting
   repository

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param forks: `detach` or `delete`, what do do with attached forks for repo
   :type forks: Optional(str)

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg": "Deleted repository `<reponame>`",
                 "success": true
               }
       error:  null

.. py:function:: grant_user_permission(apiuser, repoid, userid, perm)
   Grant permission for user on given repository, or update existing one
   if found. This command can be executed only using api_key belonging to user
   with admin rights, or repository administrator.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param userid:
   :type userid:
   :param perm: (repository.(none|read|write|admin))
   :type perm: str

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "Granted perm: `<perm>` for user: `<username>` in repo: `<reponame>`",
                 "success": true
               }
       error:  null

.. py:function:: revoke_user_permission(apiuser, repoid, userid)
   Revoke permission for user on given repository. This command can be executed
   only using api_key belonging to user with admin rights, or
   repository administrator.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param userid:
   :type userid: str or int

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm for user: `<username>` in repo: `<reponame>`",
                 "success": true
               }
       error:  null

.. py:function:: grant_user_group_permission(apiuser, repoid, usergroupid, perm)
   Grant permission for user group on given repository, or update
   existing one if found. This command can be executed only using
   api_key belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param usergroupid: id of usergroup
   :type usergroupid: str or int
   :param perm: (repository.(none|read|write|admin))
   :type perm: str

   OUTPUT::

     id : <id_given_in_input>
     result : {
       "msg" : "Granted perm: `<perm>` for group: `<usersgroupname>` in repo: `<reponame>`",
       "success": true

     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user group: `<usergroup>` in repo `<repo>`'
     }

.. py:function:: revoke_user_group_permission(apiuser, repoid, usergroupid)
   Revoke permission for user group on given repository. This command can be
   executed only using api_key belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repoid: repository name or repository id
   :type repoid: str or int
   :param usergroupid:

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm for group: `<usersgroupname>` in repo: `<reponame>`",
                 "success": true
               }
       error:  null

.. py:function:: get_repo_group(apiuser, repogroupid)
   Returns given repo group together with permissions, and repositories
   inside the group

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repogroupid: id/name of repository group
   :type repogroupid: str or int

   OUTPUT::

       id : <id_given_in_input>
       result : None if group does not exist
           {
               "group_description": "<group_description>",
               "group_id": <group_id>,
               "group_name": "<group_name>",
               "members" : [
                     {
                       "name":        "<username>",
                       "permission" : "group.(read|write|admin)",
                       "origin":      "<permission|owner|super-admin>",
                       "type" :       "user",
                     },
                     ...
                     {
                       "name":        "<usergroup name>",
                       "permission" : "group.(read|write|admin)",
                       "origin":      "<permission|owner|super-admin>",
                       "type" :       "user",
                     },
                     ...
               ],
               "owner": "<group_onwer_username>",
               "parent_group": null,
               "repositories": [
                   <repo_name>,
                   ...
               ]
           }
       error : null

.. py:function:: get_repo_groups(apiuser)
   Returns all repository groups

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser

.. py:function:: create_repo_group(apiuser, group_name, description=<Optional:''>, owner=<Optional:<OptionalAttr:apiuser>>, parent=<Optional:None>, copy_permissions=<Optional:False>)
   Creates a repository group. This command can be executed only using
   api_key belonging to user with admin rights.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param group_name:
   :type group_name:
   :param description:
   :type description:
   :param owner:
   :type owner:
   :param parent:
   :type parent:
   :param copy_permissions:
   :type copy_permissions:

   OUTPUT::

     id : <id_given_in_input>
     result : {
         "msg": "created new repo group `<repo_group_name>`"
         "repo_group": <repogroup_object>
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       failed to create repo group `<repogroupid>`
     }

.. py:function:: update_repo_group(apiuser, repogroupid, group_name=<Optional:''>, description=<Optional:''>, owner=<Optional:<OptionalAttr:apiuser>>, parent=<Optional:None>, enable_locking=<Optional:False>)


.. py:function:: delete_repo_group(apiuser, repogroupid)
   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repogroupid: name or id of repository group
   :type repogroupid: str or int

   OUTPUT::

     id : <id_given_in_input>
     result : {
       'msg': 'deleted repo group ID:<repogroupid> <repogroupname>
       'repo_group': null
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete repo group ID:<repogroupid> <repogroupname>"
     }

.. py:function:: grant_user_permission_to_repo_group(apiuser, repogroupid, userid, perm, apply_to_children=<Optional:'none'>)
   Grant permission for user on given repository group, or update existing
   one if found. This command can be executed only using api_key belonging
   to user with admin rights, or user who has admin right to given repository
   group.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repogroupid: name or id of repository group
   :type repogroupid: str or int
   :param userid:
   :param perm: (group.(none|read|write|admin))
   :type perm: str
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "Granted perm: `<perm>` (recursive:<apply_to_children>) for user: `<username>` in repo group: `<repo_group_name>`",
                 "success": true
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user: `<userid>` in repo group: `<repo_group_name>`"
     }

.. py:function:: revoke_user_permission_from_repo_group(apiuser, repogroupid, userid, apply_to_children=<Optional:'none'>)
   Revoke permission for user on given repository group. This command can
   be executed only using api_key belonging to user with admin rights, or
   user who has admin right to given repository group.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repogroupid: name or id of repository group
   :type repogroupid: str or int
   :param userid:
   :type userid:
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm (recursive:<apply_to_children>) for user: `<username>` in repo group: `<repo_group_name>`",
                 "success": true
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user: `<userid>` in repo group: `<repo_group_name>`"
     }

.. py:function:: grant_user_group_permission_to_repo_group(apiuser, repogroupid, usergroupid, perm, apply_to_children=<Optional:'none'>)
   Grant permission for user group on given repository group, or update
   existing one if found. This command can be executed only using
   api_key belonging to user with admin rights, or user who has admin
   right to given repository group.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repogroupid: name or id of repository group
   :type repogroupid: str or int
   :param usergroupid: id of usergroup
   :type usergroupid: str or int
   :param perm: (group.(none|read|write|admin))
   :type perm: str
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   OUTPUT::

     id : <id_given_in_input>
     result : {
       "msg" : "Granted perm: `<perm>` (recursive:<apply_to_children>) for user group: `<usersgroupname>` in repo group: `<repo_group_name>`",
       "success": true

     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user group: `<usergroup>` in repo group: `<repo_group_name>`"
     }

.. py:function:: revoke_user_group_permission_from_repo_group(apiuser, repogroupid, usergroupid, apply_to_children=<Optional:'none'>)
   Revoke permission for user group on given repository. This command can be
   executed only using api_key belonging to user with admin rights, or
   user who has admin right to given repository group.

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param repogroupid: name or id of repository group
   :type repogroupid: str or int
   :param usergroupid:
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   OUTPUT::

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm (recursive:<apply_to_children>) for user group: `<usersgroupname>` in repo group: `<repo_group_name>`",
                 "success": true
               }
       error:  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user group: `<usergroup>` in repo group: `<repo_group_name>`"
     }

.. py:function:: get_gist(apiuser, gistid)
   Get given gist by id

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param gistid: id of private or public gist
   :type gistid: str

.. py:function:: get_gists(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)
   Get all gists for given user. If userid is empty returned gists
   are for user who called the api

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param userid: user to get gists for
   :type userid: Optional(str or int)

.. py:function:: create_gist(apiuser, files, owner=<Optional:<OptionalAttr:apiuser>>, gist_type=<Optional:u'public'>, lifetime=<Optional:-1>, description=<Optional:''>)
   Creates new Gist

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param files: files to be added to gist
       {'filename': {'content':'...', 'lexer': null},
        'filename2': {'content':'...', 'lexer': null}}
   :type files: dict
   :param owner: gist owner, defaults to api method caller
   :type owner: Optional(str or int)
   :param gist_type: type of gist 'public' or 'private'
   :type gist_type: Optional(str)
   :param lifetime: time in minutes of gist lifetime
   :type lifetime: Optional(int)
   :param description: gist description
   :type description: Optional(str)

   OUTPUT::

     id : <id_given_in_input>
     result : {
       "msg": "created new gist",
       "gist": {}
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to create gist"
     }

.. py:function:: delete_gist(apiuser, gistid)
   Deletes existing gist

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param gistid: id of gist to delete
   :type gistid: str

   OUTPUT::

     id : <id_given_in_input>
     result : {
       "deleted gist ID: <gist_id>",
       "gist": null
     }
     error :  null

   ERROR OUTPUT::

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete gist ID:<gist_id>"
     }
