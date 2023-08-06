.. _performance:

================================
Optimizing RhodeCode Performance
================================

When serving large amount of big repositories RhodeCode can start
performing slower than expected. Because of demanding nature of handling large
amount of data from version control systems here are some tips how to get
the best performance.

* RhodeCode will perform better on machines with faster disks (SSD/SAN). It's
  more important to have faster disk than faster CPU.

* Slowness on initial page can be easily fixed by grouping repositories, and/or
  increasing cache size (see below), that includes using lightweight dashboard
  option and vcs_full_cache setting in .ini file


Follow these few steps to improve performance of RhodeCode system.


1. Increase cache and move /tmp to a hgfs based filesystem.

    in the .ini file::

     beaker.cache.sql_cache_long.expire=3600 <-- set this to higher number

    This option affects the cache expiration time for main page. Having
    few hundreds of repositories on main page can sometimes make the system
    to behave slow when cache expires for all of them. Increasing `expire`
    option to day (86400) or a week (604800) will improve general response
    times for the main page. RhodeCode has an intelligent cache expiration
    system and it will expire cache for repositories that had been changed.

    Good option is moving your /tmp folder to a ram based hgfs. A lot of RhodeCode
    components relly on access to /tmp folder and putting this inside a RAM can
    give a noticeable speed boost.

2. Switch from sqlite to postgres or mysql

    sqlite is a good option when having small load on the system. But due to
    locking issues with sqlite, it's not recommended to use it for larger
    setup. Switching to mysql or postgres will result in a immediate
    performance increase.

3. Switch to database based user sessions.

    While file based sessions are fine for smaller setups, larger ones can
    generate problems with this setup. Most common issue is file limit/open
    file limit errors when there are a lot of session files. For best performance
    and maintainability it's recommended to switching to database based user sessions.
    Simply uncomment this section in your .ini file adjusting `beaker.session.sa.url`
    to your database type used ::

     ## db session ##
     beaker.session.type = ext:database
     beaker.session.sa.url = postgresql://postgres:<pass>@localhost/rhodecode
     beaker.session.table_name = db_session

4. Scale RhodeCode horizontally

    Scaling horizontally can give huge performance increase when dealing with
    large traffic (large amount of users, CI servers etc). RhodeCode can be
    scaled horizontally on a single (recommended) or multiple machines. In order
    to scale horizontally you need to do the following:

    - set `instance_id = *` in your .ini file for letting RhodeCode know that you
      will use multi node setup.
    - If you scale on more than one different machine, each instance
      `data` storage (defined in .ini file) needs to be configured to be
      stored on a shared disk storage, preferably together with repositories.
      This `data` dir contains template caches, whoosh index and it's used for
      tasks locking (so it's safe across multiple instances). Set the
      `cache_dir`, `index_dir`, `beaker.cache.data_dir`, `beaker.cache.lock_dir`
      variables in each .ini file to shared location across RhodeCode instances
    - if celery is used each instance should run separate celery instance, but
      the message broken should be common to all of them (ex one rabbitmq
      shared server)
    - load balance using round robin or ip hash, recommended is writing LB rules
      that will separate regular user traffic from automated processes like CI
      servers or build bots.
