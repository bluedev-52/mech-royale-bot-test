# Handoff — Mech Royale bot (sesión Devin 2026-11-21)

## Estado actual
- **Versión enviada:** `bluedev-52/mech-royale-bot-test` rama `main`, commit `4eca115`. Pasa `check.py` y Docker (0 respuestas tardías).
- **Mejor puntaje oficial:** 3.17 (commit `808e115`). `9b0c1e8` = 3.15, `4eca115` = 3.15. Baseline del starter: 1.15; primera versión de esta sesión: 2.67.
- **Meta del usuario:** top-5 en el 80% de partidas (≈ 5.5+ puntos oficiales). **No alcanzada.** Top-5 local actual ≈ 3–8%.
- **Rama `experiments`** (repo de prueba): `main` + opciones experimentales apagadas (huida, borde del gas, drones) + scripts de diagnóstico en `experiments/`.
- El repo original `ianarce/mech-royale-bot` **no** se modificó: el push da 403 (la app de GitHub de Devin no tiene acceso a esa cuenta).

## Reglas oficiales (las dio el usuario)
- 48 partidas por práctica; 16 mechs: tu bot + 15 house bots (4 easy, 4 medium, 4 hard, 3 expert).
- Los house bots son **un solo escuadrón**: comparten visión, no se atacan entre sí y cazan al jugador *weakest-first*. No es FFA.
- Puntaje por partida = `16 - place`. Top-5 = lugar 1–5. 50 ms por observación. Seed, slot y spawn desconocidos.

## Simulador local
- `python3 -m sim.run --bot agent --matches 96 --jobs 8 [--seed N] --params '{json}' --out r.json` (modo squad por defecto; `--ffa` solo diagnóstico).
- Se cambió `sim/engine.py` para que la caza siga el orden weakest-first.
- **Calibración:** el simulador sobreestima ~0.9 puntos frente al oficial (3.53→2.67, 4.07→3.17, 4.35/3.28→3.15).
- **Ruido:** la misma config con las mismas semillas varía ~0.5 puntos entre corridas, porque el agente corta su búsqueda por tiempo (`budget_s`). Hay que correr siempre la base junto a cada variante y confirmar con otra seed (`--seed 1000`). Diferencias < ~0.4 no aparecen en el oficial.
- Validación: `python3 mechfight-kit/check/check.py --map-dir arena -- python3 -u $PWD/bot.py` y lo mismo con `docker run --rm -i --network none --cpus 1 --memory 512m --read-only --tmpfs /tmp:rw,size=64m --user 65534:65534 -v "$PWD/arena:/arena:ro" my-bot`.

## Qué funcionó (todo en `brain/agent.py`, activo por defecto)
1. **Esquive:** dirección sostenida bajo fuego (`w_commit=20`, 0.6–1.1 s) y distancia de pelea con gun `gun_ropt=115`. Fue de 2.44 a 3.53 local y llegó a 2.67 oficial.
2. **Loot de láser/lightning:** bug real: los candidatos de movimiento están a 5/10/16 m y el radio de recogida es 4 m, así que el bot pasaba a 6–8 m del arma sin tomarla. Se agregó un ancla `grab_pt` que camina directo al arma (`grab=1`, `grab_r=80`, `w_grab=40`); también se dejó de recoger mortero (`mortar_ok=0`). Subió a 4.07 local y **3.17 oficial**.
3. **Láser a carga completa** (`laser_hold=0.75`): empate (3.15 oficial).
4. **Cubos** (`cube_grab=1`, `cube_grab_r=40`): mismo bug del radio (3.5 m). Los cubos subieron de 2.7 a 4.3 por partida, pero el puntaje no cambió (3.15 oficial): cada cubo da +4% de HP y daño, pero agranda el mech 5%.

## Qué no funcionó (opciones apagadas en el código, 96 partidas cada una)
| Idea | Parámetros | Resultado vs base |
|---|---|---|
| 12 ajustes de pesos (cobertura, cruce, distancia, loot, energía, duelo, trampa, espacio) | `W[...]` | todos iguales o peores; más cauto o más agresivo empeora |
| Francotirador 160–200 m | estilo | 2.59–3.38 vs 3.53 |
| Emboscada | `ambush`, `w_hold`, `amb_*` | 2.30–2.72 |
| Duelo temprano | `duel`, `duel_*` | 2.88–3.12 |
| Supervivencia / ir al centro / estilo `defense` | `surv`, `w_center` | 2.26–2.51 |
| Gun junto con láser/lightning | `dual` | 3.67 vs 4.07 |
| Soltar gun por láser+lightning | `no_gun` | 4.17/4.03 vs 4.35 |
| Mejoras de arma primero, cajas a 150 m | `upg_weapon`, `crate_r` | empate |
| Perseguir más tiempo | `chase_s` 15/40 | 3.26/3.20 vs 4.35 (muere antes) |
| Rematar / no cambiar de blanco | `u_finish=2`, `hysteresis=1.5` | 3.67/3.68/3.21 vs 3.88 |
| Drones 200 m + cajas 150 m + loot ×2 | `farm_r`, `crate_r`, `wm_loot` | 4.23 → 3.17 con seed nueva (base 3.28) |
| Suministros aéreos | `drop_grab` | 3.68 vs 3.88 (cubos 3.8–4.8) |
| Huir entre 200 y 325 s | `flee`, `w_flee`, `flee_cov`, `flee_t0` | 3.88–4.06 vs 4.01 |
| Cook-off con láser | `u_counter=2.5` | 4.18 vs 4.01 |
| Borde del gas desde 265 s | `edge` | 4.27/3.42 vs 4.01/3.41 |
| Atraer cazadores a drones | `lure` | 3.94 vs 4.01 |

## Diagnósticos clave
- **Puntería no es el problema:** sin enemigo visible a < 230 m el 73% de los ticks; sin línea de tiro 10%; recargando 5%; esperando alinear puntería solo ~3%.
- **Daño:** ~5,200 por partida; 38% va a bots que no mueren; ~2 kills por partida (house bots: 1400 HP, regeneran 45 HP/s).
- **El lugar depende de cuánto sobrevive:** muere a los 180–240 s → lugar 13.1; a los 300–360 s → 10.0; después de 360 s → 5.4. Desde ~265 s el gas (60–260 dps) mata bots de la casa (en el simulador). Hoy solo ~12% de las partidas pasan de 300 s.
- **Huir no evita el daño:** el escuadrón comparte visión. Huyendo, el tiempo con cazadores a < 60 m baja de 37 a 12 ticks, pero el daño de gun/láser a distancia en el tramo 200–325 s sigue en ~1,000 (total ~1,220–1,275). Al morir hay ~3 cazadores a la vista a ~62 m y poca energía.
- Top-5 exige ~11 house bots muertos antes que tú; hoy son ~2 kills + ~1.8 por gas/drones.

## Ideas no probadas / siguientes pasos sugeridos
1. **Calibrar el simulador contra el oficial:** el modelo de los house bots (`sim/house.py`) es una suposición. Si los bots reales difieren (puntería, si evitan el gas, escalada de cazadores en `_hunter_count`), las conclusiones locales pueden no transferir. Usar los puntajes oficiales conocidos (1.15 starter, 2.67, 3.17, 3.15) como objetivo.
2. Usar envíos oficiales como A/B directo (48 partidas, ruido ~±0.3) para cambios grandes.
3. Ideas estructurales: romper la visión compartida (techos, `jet`), pelear solo en pasillos donde el lightning encadene a 3 bots, gestión de energía para boost de escape en 200–325 s.

## Archivos útiles (rama `experiments`, carpeta `experiments/`)
- `sweep.sh name '{params}' [matches]`: corre 96 partidas y escribe `~/work/r_name.{json,txt}`.
- `fire_diag.py` (visibilidad/fuego/puntería), `waste_diag.py` (daño desperdiciado), `loot_an.py` (armas vistas/tomadas), `cube_diag.py`, `drop_diag.py`, `flee_diag.py '{params}'` (daño y muerte en 200–325 s).
- Los scripts asumen el repo en `~/repos/mech-royale-bot` y la salida en `~/work`.
