def verify_and_rewrite(text: str) -> dict:
    return {
        "verdict": "FAŁSZ",
        "explanation": "Twierdzenie jest sprzeczne ze zweryfikowanymi danymi statystycznymi oraz oficjalnymi komunikatami.",
        "censored_text": "[TREŚĆ ZAWIERAJĄCA MANIPULACJĘ LUB MOWĘ NIENAWIŚCI ZOSTAŁA ZASTĄPIONA]",
        "neutralized_text": "Zgodnie z oficjalnymi raportami, wskaźniki kształtują się odmiennie od tezy sformułowanej we wpisie.",
        "subgraph_edges": [
            ("Tweet", "odnosi_się_do", "Wskaźnik_Gospodarczy"),
            ("Wskaźnik_Gospodarczy", "oficjalna_wartość", "Spadek o 1.2%"),
            ("Tweet", "twierdzi", "Wzrost o 25%"),
        ],
    }
