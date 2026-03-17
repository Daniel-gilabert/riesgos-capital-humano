-- TU RIESGO A RAYA FUNDACION PRODE
-- Esquema EXCLUSIVO para Capital Humano dentro del mismo proyecto Supabase
-- URL objetivo: https://gqfiarxccbaznjxispsv.supabase.co
-- Ejecutar en SQL Editor de Supabase

create extension if not exists pgcrypto;

create table if not exists trrfp_analisis (
    id uuid primary key default gen_random_uuid(),
    fecha_analisis timestamptz not null,
    nombre_archivo text not null,
    total_citas integer not null,
    costo_total numeric(10,2) not null,
    datos_resumen jsonb,
    creado_en timestamptz default now()
);

create index if not exists idx_trrfp_analisis_fecha on trrfp_analisis(fecha_analisis desc);
create index if not exists idx_trrfp_analisis_archivo on trrfp_analisis(nombre_archivo);

create table if not exists trrfp_citas_analizadas (
    id uuid primary key default gen_random_uuid(),
    analisis_id uuid not null references trrfp_analisis(id) on delete cascade,
    nombre_empleado text not null,
    fecha_cita timestamptz,
    asistio boolean not null,
    anulada boolean not null,
    genera_costo boolean not null,
    monto_costo numeric(10,2) not null
);

create index if not exists idx_trrfp_citas_analisis on trrfp_citas_analizadas(analisis_id);
create index if not exists idx_trrfp_citas_fecha on trrfp_citas_analizadas(fecha_cita);

comment on table trrfp_analisis is 'Tabla exclusiva de analisis para TU RIESGO A RAYA FUNDACION PRODE';
comment on table trrfp_citas_analizadas is 'Detalle de citas analizadas exclusivo para TU RIESGO A RAYA FUNDACION PRODE';

-- Vista exclusiva para este proyecto reutilizando empleados de Worktime
create or replace view trrfp_empleados as
select
    id,
    apellidos_y_nombre,
    email,
    activo,
    rol,
    departamento,
    responsable_id,
    jornada_semanal,
    es_responsable,
    es_admin
from empleados;

comment on view trrfp_empleados is 'Vista exclusiva TRRFP sobre la tabla compartida empleados de Worktime';

create table if not exists trrfp_access_keys (
    id uuid primary key default gen_random_uuid(),
    email text not null,
    codigo text not null,
    codigo_hash text not null,
    usado boolean not null default false,
    enviado_ok boolean not null default false,
    creado_en timestamptz not null default now(),
    expira_en timestamptz not null,
    usado_en timestamptz,
    metadata jsonb
);

create index if not exists idx_trrfp_access_keys_email on trrfp_access_keys(email, creado_en desc);
create index if not exists idx_trrfp_access_keys_estado on trrfp_access_keys(usado, expira_en);

comment on table trrfp_access_keys is 'Claves de acceso enviadas por correo para TU RIESGO A RAYA FUNDACION PRODE';
