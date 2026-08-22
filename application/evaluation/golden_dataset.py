GOLDEN_DATASET = [
    # --- notas personales (recall semantico) ---
    {"categoria": "notas", "pregunta": "¿Qué es la tríada CIA en seguridad de la información?", "expected_note_path": "Conceptos/CIA-Triad.md"},
    {"categoria": "notas", "pregunta": "¿Cómo funciona el protocolo DNS?", "expected_note_path": "Conceptos/DNS.md"},
    {"categoria": "notas", "pregunta": "¿Cómo se usa Nmap para escanear puertos?", "expected_note_path": "Conceptos/Nmap-Escaneo-Puertos.md"},
    {"categoria": "notas", "pregunta": "¿Para qué sirve la herramienta Hydra?", "expected_note_path": "Conceptos/Herramientas-Hydra.md"},
    {"categoria": "notas", "pregunta": "¿Qué es la Cyber Kill Chain?", "expected_note_path": "Conceptos/Cyber-Kill-Chain.md"},
    {"categoria": "notas", "pregunta": "¿Qué vulnerabilidades cubre el OWASP Top 10?", "expected_note_path": "Conceptos/OWASP-Top-10-2025.md"},
    {"categoria": "notas", "pregunta": "¿Qué es un SIEM y para qué sirven los logs?", "expected_note_path": "Conceptos/Logs-y-SIEM.md"},

    # --- MITRE ATT&CK oficial (recall exacto por ID + semantico) ---
    {"categoria": "attack", "pregunta": "¿Qué técnica de ATT&CK es T1055?", "expected_technique_id": "T1055"},
    {"categoria": "attack", "pregunta": "¿Qué es T1059 en MITRE ATT&CK?", "expected_technique_id": "T1059"},
    {"categoria": "attack", "pregunta": "Explícame la técnica T1056 de ATT&CK", "expected_technique_id": "T1056"},
    {"categoria": "attack", "pregunta": "¿Qué describe la técnica T1030?", "expected_technique_id": "T1030"},
    {"categoria": "attack", "pregunta": "¿Qué es T1110.001 según ATT&CK?", "expected_technique_id": "T1110.001"},
    {"categoria": "attack", "pregunta": "¿Qué técnica corresponde a la exfiltración por otros medios de red?", "expected_technique_id": "T1011"},

    # --- correlacion de IOCs (positivos y negativos, usando datos reales) ---
    {"categoria": "ioc", "pregunta": "¿Has visto la IP 185.220.101.45 antes?", "debe_encontrar": True},
    {"categoria": "ioc", "pregunta": "¿Qué sabes sobre la IP 185.220.101.45?", "debe_encontrar": True},
    {"categoria": "ioc", "pregunta": "¿Tienes registros de fuerza bruta desde la IP 45.155.205.12?", "debe_encontrar": False},
    {"categoria": "ioc", "pregunta": "¿La IP 8.8.8.8 tiene alguna detección asociada?", "debe_encontrar": False},
    {"categoria": "ioc", "pregunta": "Busca información sobre la IP 200.30.15.9", "debe_encontrar": False},
]