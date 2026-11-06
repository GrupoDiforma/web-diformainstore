# Plan — diformainstore.com (app nueva)

## Meta

Rehacer el sitio corporativo + portafolio + blog SEO + formularios de leads como app en Cursor. Demo en **demo.diformainstore.com**. Corte al dominio principal solo tras validar. Email sigue en Google.

## Contexto breve

- Backup JetBackup extraído en `C:\Users\Edwin_Laverde\Downloads\download_diformainstore` (fuente de contenido).
- Stack actual del sitio: WordPress 7.1.4, Storefront Child, Elementor, Rank Math; DB principal `diformainstore_wp61.sql.gz`; uploads ~643 MB.
- Decisión: app nueva (no mantener WordPress en Cursor). Inventario: [`inventario-backup.md`](inventario-backup.md).

## Etapas

1. **Backup JetBackup** — descargar Full Account (fuente de contenido). ✅
2. **Inventario** — páginas, posts, imágenes, formularios, URLs actuales. ✅ (ver inventario)
3. **Sede del Project** — este repo con README + docs. ← *ahora*
4. **App espejo en Cursor** — mismo contenido; panel sencillo para blog/leads si hace falta.
5. **Subdominio demo** — apuntar demo.diformainstore.com a la app publicada (DNS/cPanel).
6. **Validar** — diseño, formularios, SEO (URLs/redirecciones).
7. **Corte** — dominio principal cuando el demo esté OK.
8. **Después** — las otras webs de Marketeros.

## Reglas

- Edwin ejecuta en cPanel; guía paso a paso.
- No cambiar el dominio principal hasta validar demo.
- No pedir contraseñas en el chat.
- No tocar el backup salvo lectura.
- SEO: preservar URLs / 301 al corte.
