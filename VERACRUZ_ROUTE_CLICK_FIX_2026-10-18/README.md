# Veracruz route selection click hotfix

From promo_Veracruz root, after extracting archive:

```
python VERACRUZ_ROUTE_CLICK_FIX_2026-10-18/install.py
```

Fixes the current route planner where the first click fills Start, but subsequent map clicks are swallowed by overlapping attraction markers. Captures clicks at the map section boundary, uses stable route site IDs and automatically picks Start → Finish → Optional stop. Hides background labels during selection and shows gold marker labels on hover or focus to reduce clutter.

No changes to road network, Dijkstra, tourism data, attraction coordinates, or campaign optimization. Installer backs up changed site files and refuses to proceed if required files/references are missing.

**Not tested against your live Codespaces browser.**
