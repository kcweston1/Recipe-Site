create table users(
    id int,
    email varchar(200),
    username varchar(30),
    passwordhash text,
    salt char(32),
    reset_time timestamp,
    reset_code char(32),
    primary key (id)
    ) engine=innodb;


create table unconfirmed_users(
    email varchar(200),
    username varchar(30),
    passwordhash text,
    salt char(32),
    confirmationcode char(32)
    );

create table categories(
    id int,
    name varchar(30),
    primary key (id)
    ) engine=innodb;

create table recipes(
    id int,
    name varchar(100),
    description text,
    preptime int,
    cooktime int,
    rating float default 0.0,
    picture varchar(255) default "https://www.pythonanywhere.com/user/recipe0/files/home/recipe0/Recipe-Site/mysite/static/images/ham.gif",
    category int,
    creatorid int,
    primary key (id),
    foreign key (creatorid) references users(id),
    foreign key (category) references categories(id)
    ) engine=innodb;


create table ingredients(
    id int,
    name varchar(30),
    primary key (id)
    ) engine=innodb;


create table recipe_ingredients(
    recipe int,
    ingredient int,
    foreign key (recipe) references recipes(id),
    foreign key (ingredient) references ingredients(id)
    ) engine=innodb;


create table comments(
    id int,
    user int,
    recipe int,
    comment text,
    primary key (id),
    foreign key(user) references users(id),
    foreign key(recipe) references recipes(id)
    ) engine=innodb;


create table likes(
    user int,
    recipe int,
    islike boolean,
    foreign key(user) references users(id),
    foreign key(recipe) references recipes(id),
    primary key(user, recipe)
    ) engine=innodb;


create table instructions(
    recipe int,
    instructionnumber int,
    instruction text,
    foreign key (recipe) references recipes(id)
    ) engine=innodb;

