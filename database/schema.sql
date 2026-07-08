create extension if not exists pgcrypto;

create table if not exists recruiters (
  id uuid primary key default gen_random_uuid(),
  naam text not null unique,
  created_at timestamptz not null default now()
);

create table if not exists kandidaten (
  id uuid primary key default gen_random_uuid(),
  naam text not null,
  woonplaats text,
  leeftijd integer,
  opleiding text,
  gezochte_functies text,
  salarisindicatie text,
  tarief text,
  korte_omschrijving text,
  eigenaar_id uuid not null references recruiters(id),
  status text not null default 'Actief'
    check (status in ('Actief', 'Inactief', 'Geplaatst', 'Teruggetrokken')),
  cv_link text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists offers (
  id uuid primary key default gen_random_uuid(),
  candidate_id uuid not null references kandidaten(id) on delete cascade,
  company_name text not null,
  status text not null default 'open'
    check (status in ('open', 'verstuurd', 'intro', 'afgewezen', 'teruggetrokken')),
  sent_date date,
  last_customer_response date,
  follow_up_date date,
  note text,
  created_by_recruiter_id uuid not null
    constraint offers_created_by_recruiter_id_fkey references recruiters(id),
  assigned_to_recruiter_id uuid
    constraint offers_assigned_to_recruiter_id_fkey references recruiters(id),
  sent_by_recruiter_id uuid
    constraint offers_sent_by_recruiter_id_fkey references recruiters(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists kandidaten_eigenaar_id_idx on kandidaten(eigenaar_id);
create index if not exists kandidaten_status_idx on kandidaten(status);
create index if not exists offers_candidate_id_idx on offers(candidate_id);
create index if not exists offers_created_by_recruiter_id_idx on offers(created_by_recruiter_id);
create index if not exists offers_assigned_to_recruiter_id_idx on offers(assigned_to_recruiter_id);
create index if not exists offers_sent_by_recruiter_id_idx on offers(sent_by_recruiter_id);
create index if not exists offers_status_idx on offers(status);

insert into recruiters (naam)
values ('Andy'), ('Jay')
on conflict (naam) do nothing;
