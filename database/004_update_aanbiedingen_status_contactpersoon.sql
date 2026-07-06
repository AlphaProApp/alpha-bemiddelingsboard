alter table aanbiedingen
add column if not exists contactpersoon text;

update aanbiedingen
set status = case status
  when 'Open / nog te versturen' then 'open'
  when 'Open' then 'open'
  when 'Verstuurd' then 'verstuurd'
  when 'Intro' then 'intro'
  when 'Afgewezen' then 'afgewezen'
  when 'Teruggetrokken' then 'teruggetrokken'
  when 'Mismatch' then 'mismatch'
  when 'N.v.t.' then 'nvt'
  when 'NVT' then 'nvt'
  else status
end;

alter table aanbiedingen drop constraint if exists aanbiedingen_status_check;
alter table aanbiedingen drop constraint if exists offers_status_check;

alter table aanbiedingen
add constraint aanbiedingen_status_check
check (status in (
  'open',
  'verstuurd',
  'intro',
  'afgewezen',
  'teruggetrokken',
  'mismatch',
  'nvt'
));
