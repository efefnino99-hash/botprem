create table if not exists products (
  id bigint generated always as identity primary key,
  name text not null,
  price integer not null check (price > 0),
  active boolean not null default true
);

create table if not exists inventory (
  id bigint generated always as identity primary key,
  product_id bigint references products(id),
  code text not null unique,
  description text,
  note text,
  sold boolean not null default false,
  order_id text,
  sold_at timestamptz
);

create table if not exists orders (
  id text primary key,
  telegram_id bigint not null,
  quantity integer not null check (quantity between 1 and 100),
  total integer not null,
  status text not null default 'awaiting_payment',
  payment_method text not null default 'QRIS',
  proof_file_id text,
  reviewed_by bigint,
  review_note text,
  created_at timestamptz default now(),
  paid_at timestamptz
);

create table if not exists deliveries (
  id bigint generated always as identity primary key,
  order_id text unique references orders(id),
  telegram_id bigint not null,
  items jsonb not null,
  created_at timestamptz default now(),
  sent_at timestamptz
);

alter table products enable row level security;
alter table inventory enable row level security;
alter table orders enable row level security;
alter table deliveries enable row level security;

-- Backend memakai SUPABASE_SERVICE_ROLE_KEY hanya di server.
-- Jangan pernah menaruh service role key di frontend atau repository publik.
