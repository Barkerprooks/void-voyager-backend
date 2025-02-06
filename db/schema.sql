-- collection of places to sell things
create table if not exists `market` (
    `id` integer primary key,
    `name` varchar(80) unique not null
);

-- ways to pay
create table if not exists `currency` (
    `id` integer primary key,
    `name` varchar(80) unique not null,
    `rate` integer not null
);

-- collection of things to sell
create table if not exists `good` (
    `id` integer primary key,
    `name` varchar(120) unique not null,
    `msrp` integer not null -- default price of the item
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
    `price` integer not null, -- final price of the item
    `count` integer not null, -- number of items in the inventory
    `market` integer not null,
    `good` integer not null,
    foreign key (`market`) references `market` (`id`),
    foreign key (`good`) references `good` (`id`)
);

-- users can own multiple markets
create table if not exists `user_market` (
    `user` integer not null,
    `market` integer not null,
    `stake` integer not null, -- how much ownership the user has over the market
    foreign key (`user`) references `user` (`id`),
    foreign key (`market`) references `market` (`id`)
);