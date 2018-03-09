create table users(
    id int,
    passwordhash text,
    email varchar(200),
    username varchar(200),
    salt char(32),
    primary key (id)
    ) engine=innodb;