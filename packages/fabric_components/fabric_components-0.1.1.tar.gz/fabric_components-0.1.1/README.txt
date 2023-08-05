This package contains some common tasks for fabric.

Including:

install mysql

    # db_env will prompt for root password and database user password
    db_env(database="databasename", database_user="databaseuser")

    # Now install the mysql server or client by setting flags
    install_mysql(server=True, client=True)

    # Then create database and user
    create_database()
    create_user()

install apache2
    from fabric-components/apache import *

    # This will install apache and mod wsgi
    install_apache(mods=['list', 'of', 'enabled', 'mod'], disable_sites=['default'])
