create extension if not exists pgcrypto;

create table if not exists public.orders (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    username text,
    quantity integer not null check (quantity between 1 and 100),
    total bigint not null,
    status text not null default 'waiting_payment',
    proof_file_id text,
    created_at timestamptz not null default now()
);

create table if not exists public.inventory (
    id bigint generated always as identity primary key,
    account_data text not null,
    is_sold boolean not null default false,
    order_id uuid references public.orders(id),
    created_at timestamptz not null default now()
);

create index if not exists orders_user_status_idx
on public.orders(user_id, status, created_at desc);

create index if not exists inventory_available_idx
on public.inventory(is_sold, id);

create or replace function public.approve_order(p_order_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    v_order public.orders%rowtype;
    v_accounts text[];
    v_count integer;
begin
    select *
    into v_order
    from public.orders
    where id = p_order_id
    for update;

    if not found then
        return jsonb_build_object(
            'success', false,
            'message', 'Pesanan tidak ditemukan'
        );
    end if;

    if v_order.status <> 'waiting_review' then
        return jsonb_build_object(
            'success', false,
            'message', 'Pesanan sudah diproses'
        );
    end if;

    with selected as (
        select id
        from public.inventory
        where is_sold = false
        order by id
        limit v_order.quantity
        for update skip locked
    ),
    updated as (
        update public.inventory i
        set is_sold = true,
            order_id = p_order_id
        from selected s
        where i.id = s.id
        returning i.account_data
    )
    select
        array_agg(account_data),
        count(*)
    into v_accounts, v_count
    from updated;

    if coalesce(v_count, 0) <> v_order.quantity then
        raise exception 'Stok tidak mencukupi';
    end if;

    update public.orders
    set status = 'completed'
    where id = p_order_id;

    return jsonb_build_object(
        'success', true,
        'accounts', to_jsonb(v_accounts)
    );

exception
    when others then
        return jsonb_build_object(
            'success', false,
            'message', sqlerrm
        );
end;
$$;

revoke all on function public.approve_order(uuid) from public;
grant execute on function public.approve_order(uuid) to service_role;

alter table public.orders enable row level security;
alter table public.inventory enable row level security;
