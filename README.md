# Web diformainstore

Sede del Project para rehacer **diformainstore.com** como app nueva (no WordPress en Cursor).

Sitio actual: corporativo + portafolio + blog SEO + formularios de leads. Sin tienda ni pagos. Email corporativo en Google.

## Objetivo

- Espejo / app nueva en Cursor a partir del backup JetBackup.
- Demo en **demo.diformainstore.com**.
- Corte al dominio principal solo tras validar diseño, formularios y SEO (URLs / 301).

## Backup (solo lectura)

| Qué | Ruta |
|---|---|
| Raíz del download | `C:\Users\Edwin_Laverde\Downloads\download_diformainstore` |
| Backup JetBackup | `C:\Users\Edwin_Laverde\Downloads\download_diformainstore\backup` |
| WordPress (`public_html`) | `...\backup\homedir\public_html` |
| Dump SQL principal | `...\backup\database\diformainstore_wp61.sql.gz` |
| Uploads | `...\public_html\wp-content\uploads` (~643 MB) |

**Stack del sitio actual (backup):** WordPress 7.1.4 · tema **Storefront Child** · Elementor · Rank Math · prefijo `wp0y_` · DB `diformainstore_wp61`.

Detalle completo: [`docs/inventario-backup.md`](docs/inventario-backup.md).

## Documentación en este repo

| Archivo | Contenido |
|---|---|
| [`docs/inventario-backup.md`](docs/inventario-backup.md) | Temas, plugins, DB, uploads, señales SEO/formularios |
| [`docs/plan.md`](docs/plan.md) | Etapas de migración y reglas |

## Próximos pasos

1. Scaffold de la app demo (contenido espejo; sin WP).
2. Publicar preview / apuntar **demo.diformainstore.com**.
3. Validar diseño, leads y SEO.
4. Corte al dominio principal cuando el demo esté OK.

Aún no se construye la app completa en este commit: solo sede del Project (README + docs).
