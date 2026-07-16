insert into recruiters (naam, login_code)
values ('Camiel', 'Camieleon')
on conflict (naam) do update
set login_code = case
    when recruiters.login_code is null or recruiters.login_code = '' then excluded.login_code
    else recruiters.login_code
end;
