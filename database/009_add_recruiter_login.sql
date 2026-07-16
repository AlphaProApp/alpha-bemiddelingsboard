alter table recruiters
add column if not exists login_code text,
add column if not exists is_manager boolean not null default false;
