alter table aanbiedingen
add column if not exists datum_intro date;

alter table aanbiedingen drop constraint if exists aanbiedingen_status_check;
alter table aanbiedingen drop constraint if exists offers_status_check;

alter table aanbiedingen
add constraint aanbiedingen_status_check
check (status in (
  'open',
  'verstuurd',
  'intro',
  'latent',
  'automatisch_afgewezen_langlopende_intro',
  'afgewezen',
  'teruggetrokken',
  'mismatch',
  'nvt'
));

alter table kandidaten
add column if not exists disciplines text,
add column if not exists softwarekennis text;
