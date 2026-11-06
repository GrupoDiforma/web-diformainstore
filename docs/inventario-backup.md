# Inventario del backup WordPress — diformainstore

**Fuente:** JetBackup extraído en la máquina de Edwin  
**Fecha del inventario:** 2026-11-06  
**Alcance:** solo lectura (sin subir el tar, sin tocar sitio en vivo ni cPanel)  
**Sitio principal en `public_html`:** https://www.diformainstore.com — *Diforma In Store* / “In-Store Marketing”  
**WordPress:** 7.1.4 · prefijo de tablas `wp0y_` · DB principal `diformainstore_wp61`

---

## Rutas clave (Windows, absolutas)

| Qué | Ruta |
|---|---|
| Raíz del download | `C:\Users\Edwin_Laverde\Downloads\download_diformainstore` |
| Backup JetBackup | `C:\Users\Edwin_Laverde\Downloads\download_diformainstore\backup` |
| WordPress (public_html) | `C:\Users\Edwin_Laverde\Downloads\download_diformainstore\backup\homedir\public_html` |
| Temas | `...\public_html\wp-content\themes` |
| Plugins | `...\public_html\wp-content\plugins` |
| MU-plugins | `...\public_html\wp-content\mu-plugins` |
| Uploads | `...\public_html\wp-content\uploads` |
| Dump SQL | `C:\Users\Edwin_Laverde\Downloads\download_diformainstore\backup\database` |
| Zona DNS | `C:\Users\Edwin_Laverde\Downloads\download_diformainstore\backup\domain\diformainstore.com.zone` |
| wp-config.php | `...\public_html\wp-config.php` |

### Tamaños aproximados del backup

| Parte | Tamaño aprox. |
|---|---|
| `backup\homedir` | ~1,93 GB |
| `backup\database` | ~11,4 MB (comprimido .sql.gz) |
| `backup\config` | ~38 MB |
| `wp-content\uploads` | **~643 MB** (0,63 GB) |
| `wp-content\plugins` | ~340 MB |
| `wp-content\updraft` | ~287 MB (copias UpdraftPlus) |
| `wp-content\themes` | ~33 MB |

---

## 1. Temas (activos / disponibles)

### Activo (según opciones en `diformainstore_wp61`)

| Rol | Carpeta | Nombre |
|---|---|---|
| **Activo (child)** | `storefront-child` | **Storefront Child** |
| **Padre** | `storefront` | Storefront |

- `current_theme` = `Storefront Child`
- `stylesheet` = `storefront-child`
- `template` = `storefront`
- Portada: página estática (`show_on_front=page`, `page_on_front=7`, blog en `page_for_posts=2879`)
- Permalinks: `/%postname%/`

### Disponibles (instalados, no activos)

| Carpeta | Nombre |
|---|---|
| `hello-elementor` | Hello Elementor *(hay `theme_mods_hello-elementor` en DB → se usó en algún momento)* |
| `twentytwentyfive` | Twenty Twenty-Five |
| `twentytwentyfour` | Twenty Twenty-Four |
| `twentytwentythree` | Twenty Twenty-Three |
| `twentytwentytwo` | Twenty Twenty-Two |
| `twentytwentyone` | Twenty Twenty-One |

**Nota:** no hay tema **Jupiter** en este backup (el contexto previo que lo mencionaba no coincide con el filesystem).

---

## 2. Plugins listados

### MU-plugins

| Archivo | Notas |
|---|---|
| `elementor-safe-mode.php` | modo seguro Elementor |
| `marketeros-security-hardening.php` | hardening Marketeros (~55 KB) |

### Instalados en `wp-content\plugins` (27 carpetas)

| Carpeta | Plugin Name |
|---|---|
| `advanced-google-recaptcha` | Advanced Google reCAPTCHA |
| `all-in-one-wp-migration` | All-in-One WP Migration and Backup |
| `all-in-one-wp-migration-pro` | All-in-One WP Migration Pro |
| `all-in-one-wp-migration-unlimited-extension` | All-in-One WP Migration Unlimited Extension |
| `cookie-law-info` | CookieYes \| GDPR Cookie Consent |
| `elementor` | Elementor |
| `elementor-pro` | Elementor Pro *(carpeta presente; ver activos)* |
| `elementskit-lite` | ElementsKit Lite |
| `metricool` | Metricool |
| `official-facebook-pixel` | Meta pixel for WordPress |
| `polylang` | Polylang |
| `portfolio-elementor` | PowerFolio - Portfolio & Image Gallery for Elementor |
| `post-helpful-schema` | Post Helpful + Article Schema (Impact SERP) |
| `pro-elements` | PRO Elements |
| `really-simple-ssl` | Really Simple Security |
| `sb-elementor-contact-form-db` | FormsDB for Elementor Forms |
| `seo-by-rank-math` | Rank Math SEO |
| `seo-by-rank-math-pro` | Rank Math SEO PRO |
| `sitepress-multilingual-cms` | WPML Multilingual CMS |
| `smart-marketing-for-wp` | Smart Marketing SMS and Newsletters Forms (E-goi) |
| `under-construction-page` | Under Construction |
| `updraftplus` | UpdraftPlus - Backup/Restore |
| `whatsapp-click-email-alert` | Click & Form Email Alerts Pro |
| `wp-child-theme-generator` | WP Child Theme Generator |
| `wp-mail-smtp` | WP Mail SMTP |
| `wp-rocket` | WP Rocket |
| `wp-seo-multilingual` | WPML SEO |

### Activos en la DB (`active_plugins`, 18)

1. WPML Multilingual CMS  
2. WPML SEO  
3. Advanced Google reCAPTCHA  
4. CookieYes (GDPR Cookie Consent)  
5. Elementor  
6. ElementsKit Lite  
7. Metricool  
8. Meta pixel for WordPress  
9. PowerFolio (portfolio-elementor)  
10. Post Helpful + Article Schema  
11. **PRO Elements** *(no Elementor Pro oficial en la lista activa)*  
12. FormsDB for Elementor Forms  
13. Rank Math SEO PRO  
14. Rank Math SEO  
15. UpdraftPlus  
16. Click & Form Email Alerts Pro (WhatsApp/email)  
17. WP Child Theme Generator  
18. WP Mail SMTP  

**Instalados pero no activos** (ejemplos relevantes): `elementor-pro`, `polylang`, `wp-rocket`, `really-simple-ssl`, `smart-marketing-for-wp`, All-in-One WP Migration (+ Pro/Unlimited), `under-construction-page`.

También hay `wp-content\plugins.zip` y carpetas residuales de migraciones/backups (`ai1wm-backups`, `updraft`, `wp-rocket-config`).

---

## 3. Tamaño aproximado de uploads

**`wp-content\uploads` ≈ 643 MB (0,63 GB)**

Desglose top-level:

| Entrada | ≈ MB |
|---|---|
| `2022/` | 130 |
| `2022.zip` | 215 |
| `2023/` | 79 |
| `2024/` | 106 |
| `2025/` | 81 |
| `2026/` | 25 |
| `elementor/` | 5 |
| `wpforms/` | 2 |
| `rank-math/`, `complianz/`, etc. | residual |

Hay restos de formularios ya no instalados como plugin: `wpforms/`, `wpcf7_uploads/`, `cfdb7_uploads/`.

---

## 4. Bases de datos (.sql)

Ubicación: `C:\Users\Edwin_Laverde\Downloads\download_diformainstore\backup\database`

| Archivo | DB en el dump | Tamaño .gz |
|---|---|---|
| `diformainstore_wp61.sql.gz` | **diformainstore_wp61** (sitio principal; tablas `wp0y_*`) | ~8,4 MB |
| `diformainstore_disenni.sql.gz` | **diformainstore_disenni** (tablas `wp_*`) | ~2,2 MB |
| `diformainstore_group.sql.gz` | **diformainstore_group** (tablas `wp9j_*`) | ~0,8 MB |

`wp-config.php` del `public_html` apunta a `DB_NAME` / `DB_USER` = `diformainstore_wp61`.

Las otras dos DB corresponden a otros sitios/addon domains de la misma cuenta cPanel (p. ej. Disenni / Grupo).

---

## 5. Señales: page builders / formularios / SEO

### Page builders / diseño

- **Elementor** activo + **ElementsKit Lite** + **PRO Elements** (capa Pro no oficial / alternativa) + carpeta **Elementor Pro** instalada pero no en `active_plugins`.
- Portfolios: **PowerFolio**.
- Tema activo Storefront Child con CSS que referencia secciones Elementor (p. ej. `elementor-942`).
- En la DB aparecen datos históricos de **Slider Revolution** (plantillas `rev_slider`); **no** hay carpeta `revslider` en plugins actuales → resto/legado.
- **No** hay Jupiter / Divi / Beaver / WPBakery en plugins/themes de este backup.

### Formularios / leads / marketing

- **FormsDB for Elementor Forms** (activo) → captura de formularios Elementor.
- **Click & Form Email Alerts Pro** (WhatsApp / email).
- **Smart Marketing (E-goi)** instalado (no activo); DNS con `marketing` → `egoi.page` y `mkt` → Kmitd.
- Residuos en uploads: **WPForms**, **Contact Form 7** / CFDB7 (plugins no presentes ahora).
- **WP Mail SMTP** activo; **Advanced Google reCAPTCHA** activo.
- **CookieYes** (consentimiento).

### SEO / analítica / multilenguaje

- **Rank Math SEO + Rank Math PRO** (activos; carpeta `uploads/rank-math`).
- **Post Helpful + Article Schema**.
- **WPML + WPML SEO** activos; **Polylang** instalado pero no activo (posible solape histórico).
- **Metricool**, **Meta pixel**.
- Zone file: verificación Google (`google-site-verification=...`) y archivo `google88b3cdf99d4307be.html` en `public_html`.
- Cache/SEO performance: **WP Rocket** instalado (config en `wp-rocket-config`) pero no en activos; también LiteSpeed cache dir en homedir (`lscache`).

### Seguridad / backups

- MU-plugin Marketeros hardening; Really Simple SSL (no activo en lista); UpdraftPlus activo; All-in-One WP Migration (no activo).

---

## 6. Dominio y cuenta cPanel (contexto del backup)

- Zona: `diformainstore.com` → A `70.32.23.100`, NS `ns1/ns2.supercp.com`, host `mi3-tr100.supercp.com`.
- SOA contact: `soporte.marketeros.com.co`.
- En el mismo `homedir` hay otros document roots de la cuenta:  
  `diformagroup.com` (WP), `disenni.net` (WP), `digitalliagency.com`, `disennisas.com`, `grupodiforma.com`.

---

## Resumen operativo para migración / demo

1. Contenido visual y layout: **Elementor + Storefront Child** (no Jupiter).  
2. SEO a preservar: **Rank Math** (+ WPML SEO) y permalinks `/%postname%/`.  
3. Leads: formularios **Elementor + FormsDB** (+ alertas WhatsApp); E-goi/DNS marketing como canal externo.  
4. Media: ~**643 MB** uploads (+ zip 2022 y backups Updraft aparte).  
5. DB a importar para el sitio: **`diformainstore_wp61.sql.gz`**; las otras dos DB son de otros sitios de la cuenta.
