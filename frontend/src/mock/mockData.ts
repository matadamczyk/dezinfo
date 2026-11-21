import type { AnalysisResponse, UseCase } from '../types/analysis';

export const POLISH_POLITICAL_USE_CASES: UseCase[] = [
  {
    id: 'toxic-fake-news',
    title: 'Wulgarny fake news',
    badge: 'Toksyczność + Fałsz',
    description: 'Agresywny wpis oskarżający rząd o tajną konfiskatę oszczędności obywateli',
    text: 'Te skorumpowane złodzieje i sprzedajne zdrajcy z rządu znowu bezczelnie kłamią! Podpisali tajną ustawę o przymusowej konfiskacie 50% wszystkich oszczędności Polaków w bankach od nowego roku! To jest jawna zdrada stanu i bandytyzm, a skorumpowane media milczą!',
    expectedVerdict: 'Fałsz',
    mockResponse: {
      style: {
        sentiment: 'negative',
        toxicity_score: 0.94,
        is_toxic: true,
      },
      fact_check: {
        verdict: 'Fałsz',
        explanation: 'Brak jakichkolwiek prac legislacyjnych lub aktów prawnych przewidujących konfiskatę oszczędności. Zgodnie z ustawą o Bankowym Funduszu Gwarancyjnym (BFG) depozyty w polskich bankach są gwarantowane do kwoty 100 000 EUR na osobę.',
        censored_text: 'Te [WULGARYZM/NIENAWIŚĆ] z rządu znowu kłamią! Podpisali tajną ustawę o przymusowej konfiskacie 50% wszystkich oszczędności Polaków w bankach od nowego roku! To jest [NIENAWIŚĆ], a media milczą!',
        neutralized_text: 'Pojawiły się nieprawdziwe twierdzenia o rzekomym projekcie konfiskaty depozytów bankowych. Zgodnie z obowiązującym prawem środki na rachunkach bankowych w Polsce są w pełni chronione gwarancjami BFG do limitu 100 000 euro.',
        subgraph_edges: [
          ['Wpis_X', 'twierdzi', 'Konfiskata_50%_Oszczędności'],
          ['Wpis_X', 'zarzuca', 'Tajna_Ustawa'],
          ['Prawo_Bankowe', 'gwarantuje', 'Depozyty_do_100k_EUR'],
          ['Bankowy_Fundusz_Gwarancyjny', 'zabezpiecza', 'Oszczędności_Obywateli'],
          ['Sejm_RP', 'status_prac', 'Brak_Projektu_Konfiskaty'],
          ['Konfiskata_50%_Oszczędności', 'sprzeczność_z', 'Ustawa_o_BFG'],
        ],
      },
    },
  },
  {
    id: 'statistic-manipulation',
    title: 'Manipulacja statystykami',
    badge: 'Manipulacja danymi',
    description: 'Zniekształcona interpretacja danych GUS dotyczących stopy bezrobocia',
    text: 'Oficjalny komunikat: bezrobocie w Polsce wzrosło w ostatnim miesiącu o dramatyczne 25%, to największa fala biedy i kryzysu w historii III RP! Rząd celowo ukrywa masowe bankructwa firm przed opinią publiczną.',
    expectedVerdict: 'Manipulacja',
    mockResponse: {
      style: {
        sentiment: 'negative',
        toxicity_score: 0.42,
        is_toxic: false,
      },
      fact_check: {
        verdict: 'Manipulacja',
        explanation: 'Wpis drastycznie wyolbrzymia i manipuluje danymi statystycznymi. Stopa bezrobocia rejestrowanego wzrosła nie o 25 punktów procentowych, lecz odnotowano okresową korektę sezonową o 0.1 p.p. (z 5.0% do 5.1%), co w relacji względnej oznacza zmianę o 2%, a nie 25%. Polska utrzymuje jedną z najniższych stóp bezrobocia w UE.',
        censored_text: 'Oficjalny komunikat: bezrobocie w Polsce wzrosło w ostatnim miesiącu o dramatyczne 25%, to największa fala biedy i kryzysu w historii III RP! Rząd celowo ukrywa masowe bankructwa firm przed opinią publiczną.',
        neutralized_text: 'Według oficjalnych raportów GUS stopa bezrobocia w Polsce wynosi ok. 5.1% i odnotowała minimalną zmianę sezonową o 0.1 punktu procentowego. Dane Eurostatu potwierdzają stabilną sytuację na rynku pracy.',
        subgraph_edges: [
          ['Wpis_X', 'twierdzi', 'Wzrost_Bezrobocia_o_25%'],
          ['Wpis_X', 'powołuje_się_na', 'Raport_GUS'],
          ['GUS_Raport_Miesięczny', 'rzeczywista_wartość', 'Stopa_Bezrobocia_5.1%'],
          ['Korekta_Sezonowa', 'zakres_zmiany', 'Wzrost_o_0.1_pp'],
          ['Eurostat_Polska', 'pozycja_w_UE', '2_Najniższe_w_Europie'],
          ['Wzrost_Bezrobocia_o_25%', 'błędna_interpretacja', 'Korekta_Sezonowa'],
        ],
      },
    },
  },
  {
    id: 'neutral-truth',
    title: 'Neutralna prawda',
    badge: 'Fakt potwierdzony',
    description: 'Zweryfikowana informacja infrastrukturalna GDDKiA',
    text: 'Generalna Dyrekcja Dróg Krajowych i Autostrad podpisała umowę na realizację nowego odcinka drogi ekspresowej S19 na Podkarpaciu. Całkowity koszt inwestycji wynosi ponad 450 mln zł.',
    expectedVerdict: 'Prawda',
    mockResponse: {
      style: {
        sentiment: 'neutral',
        toxicity_score: 0.03,
        is_toxic: false,
      },
      fact_check: {
        verdict: 'Prawda',
        explanation: 'Treść wpisu jest całkowicie zgodna z faktami. GDDKiA w oficjalnym komunikacie potwierdziła podpisanie kontraktu na budowę kolejnego odcinka międzynarodowego szlaku Via Carpatia (droga S19) w województwie podkarpackim na wskazaną kwotę.',
        censored_text: 'Generalna Dyrekcja Dróg Krajowych i Autostrad podpisała umowę na realizację nowego odcinka drogi ekspresowej S19 na Podkarpaciu. Całkowity koszt inwestycji wynosi ponad 450 mln zł.',
        neutralized_text: 'GDDKiA zawarła oficjalną umowę na budowę odcinka trasy ekspresowej S19 na terenie Podkarpacia w ramach korytarza Via Carpatia, a wartość inwestycji przekracza 450 mln zł.',
        subgraph_edges: [
          ['Wpis_X', 'dotyczy', 'Inwestycja_S19'],
          ['GDDKiA', 'podpisała_kontrakt', 'Odcinek_Podkarpacie'],
          ['Kontrakt_S19', 'wartość_umowy', 'Kwota_450_mln_PLN'],
          ['Inwestycja_S19', 'należy_do', 'Szlak_Via_Carpatia'],
          ['Rządowy_Program_Dróg', 'finansuje', 'Budowa_S19'],
        ],
      },
    },
  },
  {
    id: 'out-of-scope',
    title: 'Wpis bez pokrycia w bazie',
    badge: 'Brak danych w grafie',
    description: 'Lokalne doniesienie niemające odzwierciedlenia w rejestrach',
    text: 'Przewodniczący osiedlowego klubu modelarskiego w Pcimiu Dolnym poinformował na wczorajszym zebraniu, że odmawia przekazania kluczy do modelarni nowemu zarządowi.',
    expectedVerdict: 'Brak danych',
    mockResponse: {
      style: {
        sentiment: 'neutral',
        toxicity_score: 0.08,
        is_toxic: false,
      },
      fact_check: {
        verdict: 'Brak danych',
        explanation: 'Brak powiązanych węzłów referencyjnych w grafie wiedzy oraz zewnętrznych bazach fact-checkingowych. Wypowiedź odnosi się do zdarzenia o charakterze mikro-społecznościowym, które nie występuje w monitorowanych źródłach publicznych.',
        censored_text: 'Przewodniczący osiedlowego klubu modelarskiego w Pcimiu Dolnym poinformował na wczorajszym zebraniu, że odmawia przekazania kluczy do modelarni nowemu zarządowi.',
        neutralized_text: 'Wypowiedź dotyczy wewnętrznej kwestii lokalnego koła hobbystycznego, nieodnotowanej w oficjalnych rejestrach i źródłach informacji publicznej.',
        subgraph_edges: [
          ['Wpis_X', 'wzmiankuje', 'Klub_Modelarski_Pcim'],
          ['Baza_Wiedzy_GraphRAG', 'status_podmiotu', 'Brak_Węzła_Referencyjnego'],
          ['Rejestr_Publiczny', 'weryfikacja', 'Zdarzenie_Nieweryfikowalne'],
        ],
      },
    },
  },
];

export function generateCustomMockResponse(text: string): AnalysisResponse {
  const matched = POLISH_POLITICAL_USE_CASES.find(c => 
    c.text.trim().toLowerCase() === text.trim().toLowerCase()
  );
  if (matched) {
    return JSON.parse(JSON.stringify(matched.mockResponse));
  }

  const lower = text.toLowerCase();
  const toxicKeywords = ['złodziej', 'kłam', 'zdrajc', 'idiot', 'bandyt', 'oszust', 'hańba', 'skurw', 'jeb'];
  const hasToxicWords = toxicKeywords.some(w => lower.includes(w));

  if (hasToxicWords) {
    return {
      style: {
        sentiment: 'negative',
        toxicity_score: 0.88,
        is_toxic: true,
      },
      fact_check: {
        verdict: 'Fałsz',
        explanation: 'Przedstawiona teza zawiera elementy mowy nienawiści oraz twierdzenia niezgodne z faktami zweryfikowanymi w bazie wiedzy.',
        censored_text: text.replace(new RegExp(toxicKeywords.join('|'), 'gi'), '[OCENZUROWANO]'),
        neutralized_text: 'Wypowiedź odnosi się do spornych zagadnień politycznych, jednak brak jest wiarygodnych dowodów na poparcie sformułowanych zarzutów.',
        subgraph_edges: [
          ['Analizowany_Tekst', 'zawiera', 'Treści_Spiskowe'],
          ['Baza_FactCheckingowa', 'weryfikacja', 'Sprzeczność_z_Faktami'],
          ['Analizowany_Tekst', 'kwestionuje', 'Stan_Faktyczny'],
        ],
      },
    };
  }

  return {
    style: {
      sentiment: 'neutral',
      toxicity_score: 0.15,
      is_toxic: false,
    },
    fact_check: {
      verdict: 'Brak danych',
      explanation: 'Wpis został przeanalizowany w trybie offline. W lokalnej bazie demonstracyjnej nie znaleziono jednoznacznego potwierdzenia ani zaprzeczenia dla wprowadzonego tekstu.',
      censored_text: text,
      neutralized_text: `Analiza semantyczna wpisu: "${text.slice(0, 100)}${text.length > 100 ? '...' : ''}" nie wykazuje cech manipulacji, brak jednak odnośników w podgrafie faktów.`,
      subgraph_edges: [
        ['Wprowadzony_Tekst', 'analizowany_w', 'Tryb_Demonstracyjny'],
        ['Graf_Wiedzy', 'stan_indeksu', 'Brak_Dopasowania_Semantycznego'],
      ],
    },
  };
}
