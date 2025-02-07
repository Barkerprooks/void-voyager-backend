-- all users that exist
create table if not exists `user` (
    `id` integer primary key,
    `username` varchar(80) unique,
    `password` varchar(80), -- MAKE SURE TO HASH :)
    `is_admin` boolean
);

-- all incorperations that exist
create table if not exists `incorperation` (
    `id` integer primary key,
    `name` varchar(80) unique not null,
    `user` integer not null,
    foreign key (`user`) references `user` (`id`)
);

-- all markets that exist
create table if not exists `market` (
    `id` integer primary key,
    `name` varchar(80) not null,
    `incorperation` integer not null, -- each market must come from
    foreign key (`incorperation`) references `incorperation` (`id`)
);

-- all goods that exist
create table if not exists `good` (
    `id` integer primary key,
    `name` varchar(120) unique not null,
    `cost` integer not null -- default price of the item
);

-- all ship types that exist
create table if not exists `ship` (
    `id` integer primary key,
    `name` varchar(80) unique not null,
    `cost` integer not null
);

create table if not exists `incorperation_user` (
    `incorperation` integer not null,
    `user` integer not null,
    `stake` integer not null, -- how much ownership the user has over the inc
    foreign key (`user`) references `user` (`id`),
    foreign key (`stake`) references `stake` (`id`)
);