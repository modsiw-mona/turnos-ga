# Turnos GA — asignación de turnos como servicio

Servicio que arma el horario semanal de un equipo con un algoritmo genético
(PyGAD). Parte del taller de la **Unidad 2** (`notebooks/Taller_U2_GA_Turnos.ipynb`)
y lo lleva a un servicio reproducible, verificable y publicable, como pide la
**Unidad 4** ("Despliegue de modelos de Inteligencia Artificial") del curso
*Técnicas avanzadas de IA*.

> Proyecto en construcción. Este README se completa a medida que avanza el
> historial (ver los tags de Git).

## Estructura

```text
turnos-ga/
├── .python-version      → ¿qué Python utilizamos?
├── pyproject.toml       → ¿qué necesita el proyecto?
├── uv.lock              → ¿qué versiones concretas utilizamos?
├── notebooks/           → exploración original de la Unidad 2
├── src/turnos_ga/       → lógica reutilizable
└── tests/               → pruebas automatizadas
```

## Instalación

```bash
git clone <url-del-repositorio>
cd turnos-ga
uv sync
```
