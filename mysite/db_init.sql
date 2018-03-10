create table users(
    id int,
    passwordhash text,
    email varchar(200),
    username varchar(30),
    salt char(32),
    primary key (id)
    ) engine=innodb;

create table unconfirmed_users(
    email varchar(200),
    username varchar(30),
    passwordhash text,
    salt char(32),
    confirmationcode char(32)
    );
