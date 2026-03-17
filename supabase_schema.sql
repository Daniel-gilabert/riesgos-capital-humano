-- Schema para Supabase - Riesgos de Capital Humano
-- Ejecutar en el editor SQL de Supabase

-- Tabla principal para almacenar análisis realizados
create table analisis (
    id uuid primary key default uuid_generate_v4(),
    fecha_analisis timestamp with time zone not null,
    nombre_archivo text not null,
    total_citas integer not null,
    costo_total decimal(10,2) not null,
    datos_resumen jsonb,  -- Almacena el resumen completo como JSON
    creado_en timestamp with time zone default now()
);

-- Índices para mejorar el rendimiento de consultas comunes
create index idx_analisis_fecha on analisis(fecha_analisis desc);
create index idx_analisis_archivo on analisis(nombre_archivo);

-- Tabla opcional para guardar detalle de citas analizadas
-- (Descomentar si se necesita guardar el detalle de cada cita)
/*
create table citas_analizadas (
    id uuid primary key default uuid_generate_v4(),
    analisis_id uuid not null references analisis(id) on delete cascade,
    nombre_empleado text not null,
    fecha_cita timestamp with time zone,
    asistio boolean not null,
    anulada boolean not null,
    genera_costo boolean not null,
    monto_costo decimal(5,2) not null
);

-- Índices para la tabla de detalle
create index idx_citas_analisis on citas_analizadas(analisis_id);
create index idx_citas_fecha on citas_analizadas(fecha_cita);
*/

-- Comentarios para documentación
comment on table analisis is 'Almacena los resultados de los análisis de riesgos de capital humano realizados';
comment on table citas_analizadas is 'Almacena el detalle de cada cita analizada (opcional)';

-- Función para obtener el análisis más reciente (útil para dashboard)
create or replace function get_latest_analisis()
returns table (
    id uuid,
    fecha_analisis timestamp with time zone,
    nombre_archivo text,
    total_citas integer,
    costo_total decimal,
    datos_resumen jsonb,
    creado_en timestamp with time zone
)
language sql as $$
    select * from analisis 
    order by fecha_analisis desc 
    limit 1;
$$;

-- Función para obtener estadísticas resumidas
create or replace function get_analisis_stats()
returns table (
    total_analisis integer,
    costo_total_acumulado decimal,
    promedio_costo_por_analisis decimal,
    ultimo_analisis timestamp with time zone
)
language sql as $$
    select 
        count(*) as total_analisis,
        sum(costo_total) as costo_total_acumulado,
        avg(costo_total) as promedio_costo_por_analisis,
        max(fecha_analisis) as ultimo_analisis
    from analisis;
$$;