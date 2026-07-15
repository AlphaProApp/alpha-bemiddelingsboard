alter table aanbiedingen
add column if not exists intro_status text;

alter table aanbiedingen drop constraint if exists aanbiedingen_intro_status_check;

alter table aanbiedingen
add constraint aanbiedingen_intro_status_check
check (
  intro_status is null
  or intro_status in (
    'eerste_gesprek',
    'tweede_gesprek_meeloopdag',
    'intro_afgewezen',
    'kandidaat_teruggetrokken',
    'geplaatst'
  )
);

update aanbiedingen
set intro_status = 'eerste_gesprek'
where status in ('intro', 'latent', 'automatisch_afgewezen_langlopende_intro')
  and intro_status is null;
