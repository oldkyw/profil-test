
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
            
    def avg_no_of_people(self, max_year):
        avg_number = 0
        years_no = 0
        for data_element in self.datasets:
            if data_element.status == 'przystąpiło':
                if data_element.year <= max_year:
                    avg_number += data_element.value
                    years_no += 1
        if years_no != 0:
            return avg_number/years_no
        else:
            return 0
        
    def passability(self, year=None):
        pass_index = {}
        for data_element in self.datasets:
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

    def has_regressed(self):
        index = self.passability()
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
        print('reading URI: {}'.format(uri))
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


if __name__ == '__main__':
    URI = 'https://api.dane.gov.pl/resources/17363/data'
    data = fetchData(URI, limit=4)

    some_data = Dataset('Pomorskie', 'pass', 'm', 2018, 20123 )


    polska = State('Polska')
    for data_list in data:
        polska.add_dataset(data_list)
    
    some_year = 2015
    
    for item in polska.substates:
        print('{}, srednia liczba przystepujacych do roku {}: {:0.0f} rocznie'.format(polska.substates[item].get_name(), some_year, polska.substates[item].avg_no_of_people(some_year)))
        print('Zdawalnosc na przestrzeni lat dla {}: \n\t {}'.format(polska.substates[item].get_name(), polska.substates[item].passability(some_year)))
        for occurance in polska.substates[item].has_regressed():
            print('Dla {} zanotowano regres w latach {} -> {} (z {:.2%} na {:.2%})'.format(polska.substates[item].get_name(), *occurance))
    
    
    
