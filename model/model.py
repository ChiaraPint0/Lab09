from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO
import copy

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self.max_giorni = None
        self.max_budget = None
        self.tour_regione = []

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        relazioni = TourDAO.get_tour_attrazioni()
        for relazione in relazioni:
            id_tour = relazione["id_tour"]
            id_attrazioni = relazione["id_attrazione"]

            tour = self.tour_map[id_tour]
            attrazione = self.attrazioni_map[id_attrazioni]

            tour.attrazioni.add(attrazione)
            attrazione.tour.add(tour)

        # TODO

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        max_giorni = max_giorni
        max_budget = max_budget

        self.tour_regione = [tour for tour in self.tour_map.values()
                             if tour.id_regione == id_regione]
        if not self.tour_regione:
            return [], 0, 0

        self._ricorsione(
            start_index=0,
            pacchetto_parziale=[],
            durata_corrente=0,
            costo_corrente=0,
            valore_corrente=0,
            attrazioni_usate=set())

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

        # TODO


    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        if start_index == len(self.tour_regione):
            if valore_corrente > self._valore_ottimo:
                self._valore_ottimo = valore_corrente
                self._costo = costo_corrente
                self._pacchetto_ottimo = pacchetto_parziale.copy()
            return

        for i in range(start_index, len(self.tour_regione)):
            tour = self.tour_regione[i]
            if self.max_giorni is not None and durata_corrente + tour.durata_giorni > self.max_giorni:
                continue

            if self.max_budget is not None and costo_corrente + tour.costo > self.max_budget:
                continue

            if len(attrazioni_usate.intersection(tour.attrazioni)) > 0:
                continue

            pacchetto_parziale.append(tour)
            nuove_attrazioni = attrazioni_usate.union(tour.attrazioni)
            nuovo_valore = valore_corrente + sum(a.valore_culturale for a in tour.attrazioni)
            nuova_durata = durata_corrente + tour.durata_giorni
            nuovo_costo = costo_corrente + tour.costo

            self._ricorsione(i + 1,
                            pacchetto_parziale,
                            nuova_durata,
                            nuovo_costo,
                            nuovo_valore,
                            nuove_attrazioni)

            pacchetto_parziale.pop()

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
