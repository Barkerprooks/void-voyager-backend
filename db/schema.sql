-- all users that exist
create table if not exists `user` (
    `pk` integer primary key,
    `username` varchar(80) unique,
    `password` varchar(80), -- MAKE SURE TO HASH :)
    `is_admin` boolean,
    `money` integer not null
    -- perhaps later we can make a seperate db entity for pilots and whatnot
);

-- all ship types that exist
create table if not exists `ship` (
    `pk` integer primary key,
    `name` varchar(80) unique not null,
    `cost` integer not null
);

-- all incorperations that exist
create table if not exists `incorperation` (
    `pk` integer primary key,
    `name` varchar(80) unique not null,
    `user` integer not null,
    foreign key (`user`) references `user` (`pk`)
);

-- all markets that exist
create table if not exists `market` (
    `pk` integer primary key,
    `name` varchar(80) not null,
    `incorperation` integer not null, -- each market must come from
    foreign key (`incorperation`) references `incorperation` (`pk`)
);

-- all goods that exist
create table if not exists `good` (
    `pk` integer primary key,
    `name` varchar(120) unique not null,
    `cost` integer not null -- default price of the item
);

create table if not exists `user_ship` (
    `pk` integer primary key,
    `name` varchar(80),
    `user` integer not null,
    `ship` integer not null,
    foreign key (`user`) references `user` (`pk`),
    foreign key (`ship`) references `ship` (`pk`)
);

create table if not exists `user_incorperation` (
    `pk` integer primary key,
    `user` integer not null,
    `incorperation` integer not null,
    `stake` integer not null, -- how much ownership the user has over the inc
    foreign key (`user`) references `user` (`pk`),
    foreign key (`incorperation`) references `incorperation` (`pk`)
);