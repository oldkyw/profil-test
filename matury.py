
class State:

    def __init__(self, name):
        self.name = name
        self.datasets = []
        self.substates = {}
        
    def get_name(self):
        return self.name
    
    def add_substate(self, state):
        self.substates[state.get_name()] = state
      
    def get_substate_names(self):
        return [self.substates[state].get_name() for state in self.substates]
           
    def add_dataset(self, new_data):
        
        if not isinstance(new_data, Dataset):
            new_data = Dataset(*new_data)
            
        if new_data.get_area_name() == self.name:
            self.datasets.append(new_data)
            
        elif new_data.get_area_name() in self.get_substate_names():
            self.substates[new_data.get_area_name()].add_dataset(new_data)
            
        else:
            new_state = State(new_data.get_area_name())
            new_state.add_dataset(new_data)
            self.add_substate(new_state)
            
    def avg_no_of_people(self, max_year, selected_sex = None):
        avg_number = 0
        years_no = 0
        for data_element in self.datasets:
            #if sex is specified and is the correct sex for Dataset
            if selected_sex and not data_element.sex == selected_sex: continue
            if data_element.status == 'przystąpiło':
                if data_element.year <= max_year:
                    avg_number += data_element.value
                    years_no += 1
        if years_no != 0:
            return avg_number/years_no
        else:
            return 0
        
    def passability(self, year=None, selected_sex = None):
        pass_index = {}
        for data_element in self.datasets:
            #if sex is specified and is the correct sex for Dataset
            if selected_sex and not data_element.sex == selected_sex: continue
            #if year is specified and is the correct year for Dataset
            if year and not data_element.year == year: continue  
            if data_element.year in pass_index:
                if data_element.is_passed():
                    pass_index[data_element.year][0] += data_element.value
                    pass_index[data_element.year][1] += data_element.value
                else:
                    pass_index[data_element.year][1] += data_element.value
            else:
                if data_element.is_passed():
                    pass_index[data_element.year] = [data_element.value, data_element.value]
                else:
                    pass_index[data_element.year] = [0, data_element.value]
        
        for year in pass_index:
            pass_index[year] = pass_index[year][0]/pass_index[year][1]
            
        return pass_index

    def has_regressed(self, selected_sex = None):
        index = self.passability(selected_sex=selected_sex)
        regress = []
        year_list = [year for year in index]
        if sorted(year_list) == year_list:
            for year in index:
                if year == year_list[0]: 
                    previous = index[year]
                elif index[year] < previous:
                    regress.append([year-1 , year, previous, index[year]])
                    previous = index[year]
            return regress
        else:
            raise ValueError('list is not sorted')
            
    def compare(self, state, selected_sex = None):
        index_this = self.passability(selected_sex=selected_sex)
        index_that = state.passability(selected_sex=selected_sex)
        better = []
        for year in index_this:
            if year in index_that:
                if index_that[year] >= index_this[year]:
                    better.append([year, state.get_name(), index_that[year], index_this[year]])
                else:
                    better.append([year, self.get_name(), index_this[year], index_that[year]])
        return better
                    
            
class Dataset:

    def __init__(self, area, status, sex, year, value):
        self.status = status
        self.sex = sex
        self.value = int(value)
        self.year = int(year)
        self.area = area

    def get_area_name(self):
        return self.area
    
    def is_passed(self):
        if self.status == 'zdało':
            return True
        elif self.status == 'przystąpiło':
            return False
        else:
            raise ValueError('unknown status of Dataset (pass/start)') 
    
def fetchData(uri='https://api.dane.gov.pl/resources/17363/data', limit=None):
    import requests
    Data = []
    while True:
        print('Wczytywanie danych z: {}'.format(uri))
        parsed = requests.get(uri).json()
        
        for item in parsed['data']:
            Data.append([item['attributes'][column] for column in ['col1', 'col2', 'col3', 'col4', 'col5']])
        
        if parsed['links']['self'] == parsed['links']['last']:
            count = parsed['meta']['count']
            break
        if len(parsed['data'])==0 or str(limit)==uri.split('=')[-1]:
            break
        uri = parsed['links']['next']   
    return Data

def execute_option(selection, selected_sex, year, state):
    pass
    return 
    

if __name__ == '__main__':
    URI = 'https://api.dane.gov.pl/resources/17363/data'
    data = fetchData(URI, limit=10)

    polska = State('Polska')
    for data_list in data:
        polska.add_dataset(data_list)
    
    some_year = 2015
    sex = None
    
    print('\nSkrypt do analizy danych o maturzystach przystępujących do egzaminu w latach 2010-2018, dostępnych w bazie https://dane.gov.pl/dataset/1567')
    print('\nWybierz jedną z opcji:')
    options_messages = ['obliczenie średniej liczby osób, które przystąpiły do egzaminu dla \
    danego województwa na przestrzeni lat, do podanego roku włącznie', 'obliczenie procentowej \
    zdawalności dla danego województwa na przestrzeni lat', 'znalezienie województwa o najlepszej \
    zdawalności w konkretnym roku', 'wyszukiwanie województw, które zanotowały regresję zdawalności\
     w kolejnych latach', 'porównanie zdawalności dwóch województw na przestrzeni lat']
    [print('{}) {}'.format(number, " ".join(option.split()))) for number, option in enumerate(options_messages)]
    
    choice = int(input('Podaj numer wybranej opcji: '))
    if choice in [0, 1, 4]:
        print('\nDostępne dane dla następujących województw:')
        statemap = dict( [[str(number), state] for number, state in enumerate(polska.substates)])
        [print('{}. {}'.format(number, state)) for number, state in enumerate(polska.substates)]
        state1 = input('Wybierz województwo: ')
        if state1 not in statemap.keys():
            raise ValueError('Wybrano niewlasciwe województwo')
        else:
            state1 = polska.substates[statemap[state1]]
        if choice == 4:
            state2 = input('Wybierz drugie województwo do porównania: ')
            if state2 not in statemap.keys():
                raise ValueError('Wybrano niewlasciwe województwo')
            else: 
                state2 = polska.substates[statemap[state2]]
    if choice in [0, 2]:
        year = int(input('Podaj wybrany rok (2010-2018): '))
        if year>2018 or year<2010:
            raise ValueError('Podany rok nie znajduje się w bazie')
        
    
    selected_sex = input('Wybierz opcję rozróżniania płci (m/k/0): ')
    if selected_sex == 'm':
        selected_sex = 'mężczyźni'
    elif selected_sex == 'k':
        selected_sex = 'kobiety'
    else:
        selected_sex = None
    
    if choice == 0:
        print('\t{}, średnia liczba przystepujacych do roku {} to {:0.0f} osób rocznie'.format(
        state1.get_name(), year, state1.avg_no_of_people(year)))
    elif choice == 1:
        print('{}, zdawalność na przestrzeni lat:'.format(state1.get_name()))
        [print('\t{}: {:.2%}'.format(year, rate)) for year, rate in state1.passability().items()]
    elif choice == 2:
        best_index = 0
        for item in polska.substates:
            if polska.substates[item].passability(year=year)[year] >= best_index:
                best_index = polska.substates[item].passability(year=year)[year]
                best_state = polska.substates[item].get_name()
        print('\tW roku {} najlepszą zdawalność zanotowano w {} ({:.2%})'.format(year, best_state, best_index))
    elif choice == 3:
        for item in polska.substates:
            for occurance in polska.substates[item].has_regressed():
                print('\t{} zanotowało regres w latach {} -> {} (z {:.2%} na {:.2%})'.format(polska.substates[item].get_name(), *occurance))
    elif choice == 4:
        if state1==state2:
            raise ValueError('Wybrano to samo województwo')
        for item in state1.compare(state2, selected_sex=selected_sex):
            print('\t{} - {} ({:.2%} > {:.2%})'.format(*item))
    else:
        raise ValueError('Niepoprawny wybór')   
        

    
    
