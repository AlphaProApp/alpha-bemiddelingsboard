-- Run this after the first MVP schema if your database still uses the old
-- "aanbiedingen" table and Dutch column names.

alter table if exists aanbiedingen rename to offers;

alter table if exists offers rename column kandidaat_id to candidate_id;
alter table if exists offers rename column bedrijf to company_name;
alter table if exists offers rename column datum_verstuurd to sent_date;
alter table if exists offers rename column laatste_klantreactie to last_customer_response;
alter table if exists offers rename column opvolgdatum to follow_up_date;
alter table if exists offers rename column opmerking to note;
alter table if exists offers rename column aangeboden_door_id to created_by_recruiter_id;

alter table offers
  add column if not exists assigned_to_recruiter_id uuid references recruiters(id),
  add column if not exists sent_by_recruiter_id uuid references recruiters(id);

update offers
set assigned_to_recruiter_id = coalesce(assigned_to_recruiter_id, created_by_recruiter_id)
where assigned_to_recruiter_id is null;

update offers
set sent_by_recruiter_id = coalesce(sent_by_recruiter_id, created_by_recruiter_id)
where sent_by_recruiter_id is null
  and lower(status) in ('verstuurd', 'intro', 'afgewezen', 'teruggetrokken');

update offers
set status = case status
  when 'Open / nog te versturen' then 'open'
  when 'Verstuurd' then 'verstuurd'
  when 'Intro' then 'intro'
  when 'Afgewezen' then 'afgewezen'
  when 'Teruggetrokken' then 'teruggetrokken'
  else status
end;

alter table offers drop constraint if exists aanbiedingen_status_check;
alter table offers drop constraint if exists offers_status_check;
alter table offers
  add constraint offers_status_check
  check (status in ('open', 'verstuurd', 'intro', 'afgewezen', 'teruggetrokken'));

alter table offers drop constraint if exists aanbiedingen_aangeboden_door_id_fkey;
alter table offers drop constraint if exists offers_created_by_recruiter_id_fkey;
alter table offers
  add constraint offers_created_by_recruiter_id_fkey
  foreign key (created_by_recruiter_id) references recruiters(id);

alter table offers drop constraint if exists offers_assigned_to_recruiter_id_fkey;
alter table offers
  add constraint offers_assigned_to_recruiter_id_fkey
  foreign key (assigned_to_recruiter_id) references recruiters(id);

alter table offers drop constraint if exists offers_sent_by_recruiter_id_fkey;
alter table offers
  add constraint offers_sent_by_recruiter_id_fkey
  foreign key (sent_by_recruiter_id) references recruiters(id);

create index if not exists offers_candidate_id_idx on offers(candidate_id);
create index if not exists offers_created_by_recruiter_id_idx on offers(created_by_recruiter_id);
create index if not exists offers_assigned_to_recruiter_id_idx on offers(assigned_to_recruiter_id);
create index if not exists offers_sent_by_recruiter_id_idx on offers(sent_by_recruiter_id);
create index if not exists offers_status_idx on offers(status);
