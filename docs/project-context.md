# Contexto del proyecto

## Objetivo
Dejar de pagar a Marketeros (Bogotá, Colombia) por la administración de varias webs, empezando por **diformainstore.com**, y montar un flujo autoadministrado: espejo de prueba → validación → sitio en vivo con hosting/base de datos de Cursor y pasarelas de pago.

## Sitios
1. diformainstore.com (prioridad; WordPress; acceso cPanel) — corporativo + portafolio + blog SEO semanal + formularios de leads; **sin tienda ni pagos**; email corporativo en Google (no en el hosting)
2–4. Tres webs más administradas por Marketeros (pendiente de nombres y accesos)

## Stack actual (conocido)
- WordPress
- Hosting con cPanel (cuenta `diformainstore` en JetBackup; panel diformagroup.com, tema Jupiter)
- JetBackup 5: 30 backups, ~11 GB de uso de cuenta
- Full Account incluye: Home Dir, 3 bases de datos, 9 DB users, 2 emails, dominios, SSL, FTP
- Descarga lista en View Downloads: Accounts `diformainstore`, 19 ítems, **1.19 GB** (5 nov 2026 8:30 PM Bogotá)
- Archivo local: `download_diformainstore_1793928465_30506.tar` (carpeta Descargas)
- Extraído en `Descargas/download_diformainstore/backup/` (homedir, database, domain, email, etc.)
- `public_html` = WordPress (wp-admin, wp-content, wp-includes, wp-config.php)
- También: Softaculous / WordPress Manager by Softaculous

## Enfoque
Edwin es inexperto y quiere aprender haciéndolo. Guía por etapas cortas, con checklist y validación antes de tocar producción.

## Decisión (2026-11-05)
Rehacer la web como app nueva en Cursor (no mantener WordPress). Demo en **demo.diformainstore.com** antes de tocar el dominio principal. Backup JetBackup = fuente de contenido (textos, imágenes, blog, leads). SEO: preservar URLs / 301 al corte.
