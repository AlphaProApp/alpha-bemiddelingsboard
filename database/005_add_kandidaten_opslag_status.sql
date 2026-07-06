alter table kandidaten drop constraint if exists kandidaten_status_check;

alter table kandidaten
add constraint kandidaten_status_check
check (status in (
  'Actief',
  'Kandidaten opslag',
  'Inactief',
  'Geplaatst',
  'Teruggetrokken',
  'Opgelost'
));

alter table aanbiedingen drop constraint if exists aanbiedingen_kandidaat_id_fkey;

alter table aanbiedingen
add constraint aanbiedingen_kandidaat_id_fkey
foreign key (kandidaat_id)
references kandidaten(id)
on delete cascade;
