DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS ITEMS;
DROP TABLE IF EXISTS USERS;

create table users (
	id int auto_increment primary key,
	first_name varchar(255) not null,
	last_name varchar(255) not null,
	email varchar(50) unique not null,
	phone varchar(12) unique,
	password varchar(100) not null,
	created_at timestamp default now()
);

create table items (
	id int auto_increment primary key,
	catagory varchar(50) not null,
	created_at timestamp default now()
);

create table carts (
	id int auto_increment primary key,
	user_id int not null,
	created_at timestamp default now(),
	foreign key(user_id) references users(id)
);

create table cart_items (
	cart_id int not null,
	item_id int not null,
	item_quantity int not null,
	foreign key(cart_id) references carts(id),
	foreign key(item_id) references items(id),
	primary key (cart_id, item_id)
);

create table orders (
	id int auto_increment primary key,
	user_id int not null,
	created_at timestamp default now(),
	foreign key(user_id) references users(id)
);

create table order_items (
	order_id int not null,
	item_id int not null,
	item_quantity int not null,
	foreign key(order_id) references orders(id),
	foreign key(item_id) references items(id),
	primary key (order_id, item_id)
);