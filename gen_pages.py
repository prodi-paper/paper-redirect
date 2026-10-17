"""Génère une page 200 par URL de paper.prodi.com → redirection vers la même URL sur prodi.com.

Pourquoi : GitHub Pages ne sait pas faire de 301. Avant, seules la racine (200) et 404.html
existaient : toutes les sous-pages répondaient 404 → Google les jetait sans transmettre leur
historique à prodi.com. Ici chaque page répond 200 avec rel=canonical vers prodi.com +
redirection JS (anti-boucle conservée) + meta refresh dans <noscript> → signal de redirection
permanente. Les chemins absents de la liste (outils : /catalogue/?s=, /proforma/…) restent
servis par 404.html, qui redirige en gardant chemin + query.

Liste = sitemap de prodi.com (téléchargé) + URL paper.* vues dans Search Console (urls_gsc.txt).
Relancer : python3 gen_pages.py   (après ajout de pages sur prodi.com)
"""
import html, os, re, urllib.request

SITEMAP = "https://prodi.com/sitemap.xml"
TPL = open("template.html", encoding="utf-8").read()


def paths():
    xml = urllib.request.urlopen(SITEMAP, timeout=30).read().decode()
    ps = {re.sub(r"^https://prodi\.com", "", u) or "/" for u in re.findall(r"<loc>([^<]+)</loc>", xml)}
    ps |= {l.strip() for l in open("urls_gsc.txt", encoding="utf-8") if l.strip()}
    return sorted(p for p in ps if p.startswith("/") and p.endswith("/"))


def main():
    ps = paths()
    for p in ps:
        dest = "https://prodi.com" + p
        page = TPL.replace("{{DEST}}", html.escape(dest, quote=True))
        out = os.path.join(p.strip("/"), "index.html") if p != "/" else "index.html"
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        open(out, "w", encoding="utf-8").write(page)
    locs = "\n".join(f"  <url><loc>https://paper.prodi.com{p}</loc></url>" for p in ps)
    open("sitemap.xml", "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + locs + "\n</urlset>\n")
    print(len(ps), "pages")


if __name__ == "__main__":
    main()
