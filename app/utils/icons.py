

def icon(name: str, size: int = 20, color: str = "#e74c3c") -> str:
    """Return an HTML string with the requested SVG icon."""
    icons = {

        "globe": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="2" y1="12" x2="22" y2="12"/>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10
                     15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
        </svg>""",

        "map": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/>
            <line x1="8" y1="2" x2="8" y2="18"/>
            <line x1="16" y1="6" x2="16" y2="22"/>
        </svg>""",

        "trending-up": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
            <polyline points="17 6 23 6 23 12"/>
        </svg>""",

        "target": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="6"/>
            <circle cx="12" cy="12" r="2"/>
        </svg>""",

        "activity": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
        </svg>""",

        "info": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>""",

        "bar-chart": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
            <line x1="2" y1="20" x2="22" y2="20"/>
        </svg>""",

        "cpu": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
            <rect x="9" y="9" width="6" height="6"/>
            <line x1="9" y1="1" x2="9" y2="4"/>
            <line x1="15" y1="1" x2="15" y2="4"/>
            <line x1="9" y1="20" x2="9" y2="23"/>
            <line x1="15" y1="20" x2="15" y2="23"/>
            <line x1="20" y1="9" x2="23" y2="9"/>
            <line x1="20" y1="14" x2="23" y2="14"/>
            <line x1="1" y1="9" x2="4" y2="9"/>
            <line x1="1" y1="14" x2="4" y2="14"/>
        </svg>""",

        "book": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>""",

        "shield": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>""",

        "alert": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0
                     1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>""",

        "database": f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"
             viewBox="0 0 24 24" fill="none" stroke="{color}"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
        </svg>""",
    }
    return icons.get(name, icons["info"])


def icon_label(icon_name: str, label: str,
               size: int = 18, color: str = "#e74c3c") -> str:
    """Return an HTML string with an icon followed by a label."""
    return f"""
    <div style="display:flex; align-items:center; gap:8px;">
        {icon(icon_name, size, color)}
        <span style="color:#ffffff; font-weight:600;
                     font-size:0.95rem;">{label}</span>
    </div>
    """