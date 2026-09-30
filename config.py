REFRESH_SECONDS = 30
MAX_CANDIDATES = 4

OFFICES = {
    "Presidente": "1",
    "Governador": "3",
    "Senador": "5",
    "Deputado Federal": "6",
    "Deputado Estadual": "7",
    "Deputado Distrital": "8",
}

TSE = {
    "official": {
        "base": "https://resultados.tse.jus.br",
        "environment": "oficial",
        "cycle": "ele2026",
        "federal_election": "6257",
        "state_election": "6259",
    },
    "simulation": {
        "base": "https://resultados-sim.tse.jus.br/simulado",
        "environment": "simulado2026",
        "cycle": "ele2026",
        "federal_election": "21270",
        "state_election": "21272",
    },
}
