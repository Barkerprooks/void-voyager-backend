-- collection of places to sell things
create table if not exists `market` (
    `id` integer primary key,
    `name` text unique not null
);

-- ways to pay
create table if not exists `currency` (
    `id` integer primary key,
    `name` varchar(80) unique not null,
    `rate` int not null
);

-- collection of things to sell
create table if not exists `good` (
    `id` integer primary key,
    `name` varchar(120) unique not null,
    `msrp` int not null -- default price of the item
);

-- basically users
create table if not exists `user` (
    `id` integer primary key,
    `username` varchar(80) unique,
    `password` varchar(80) -- MAKE SURE TO HASH :)
);

-- market / curreny mapping
create table if not exists `market_currency` (
    `market` integer not null,
    `currency` integer not null,
    foreign key (`market`) references `market` (`id`),
    foreign key (`currency`) references `currency` (`id`)
);

-- market / good mapping
create table if not exists `market_good` (
    `price` int not null, -- final price of the item
    `count` int not null, -- number of items in the inventory
    `market` integer not null,
    `good` integer not null,
    foreign key (`market`) references `market` (`id`),
    foreign key (`good`) references `good` (`id`)
);

-- users can own multiple markets
create table if not exists `user_market` (
    `user` integer not null,
    `market` integer not null,
    foreign key (`user`) references `user` (`id`),
    foreign key (`market`) references `market` (`id`)
);