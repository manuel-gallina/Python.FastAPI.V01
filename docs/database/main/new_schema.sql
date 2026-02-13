create database python_fastapi_v01;

create schema python_fastapi_v01.public;

create schema python_fastapi_v01.auth;

create table python_fastapi_v01.auth.user
(
    id        int generated always as identity,
    full_name varchar not null,
    email     varchar not null,
    constraint u__id__pk primary key (id),
    constraint u__email__uk unique (email)
)
