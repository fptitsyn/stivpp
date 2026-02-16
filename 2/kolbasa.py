'''
Колбаса
марка - строка
тип - выбор один из ('варёная', 'копчёная', 'сырокопчёная', 'полукопчёная', 'вяленая')
вес (в граммах) - число
нарезка - логический тип
количество кусочков в нарезке - число (необязательно, только если предыдущий параметр - истина)

api_answer = {
    'brand': 'Клинская',
    'kind': 'варёная',
    'weight': 400,
    'precut': false,
}
'''

class Kolbasa():
    
    kinds = ['варёная', 'копчёная', 'сырокопчёная', 'полукопчёная', 'вяленая']

    def __init__(self, obj):
        vals = obj.values()
        assert vals[0] is str
        assert vals[1].lower() in self.kinds
        assert vals[2] is int and vals[2] >= 50
        assert vals[3] is bool

        self.brand = vals[0]
        self.kind = vals[1]
        self.weight = vals[2]
        self.precut = vals[3]

        if self.precut:
            self.num_of_slices = vals[4]

    
    def calculate_weight_per_slice(self):
        if self.precut:
            return self.weight / self.num_of_slices
        return -1
