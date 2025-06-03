class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * size
        self.count = 0
        self.load_factor_threshold = 0.75

    def hash_function(self, name):
        return hash(name) % self.size

    def insert(self, name, roll_number, grades, status):
        if self.count / self.size >= self.load_factor_threshold:
            self.rehash()
        index = self.hash_function(name)
        while self.table[index] is not None:
            if self.table[index][0] == name:
                return False  # Duplicate name
            index = (index + 1) % self.size  # Linear probing
        self.table[index] = (name, roll_number, grades, status)
        self.count += 1
        return True

    def search(self, name):
        index = self.hash_function(name)
        original_index = index
        while self.table[index] is not None:
            if self.table[index][0] == name:
                return self.table[index]
            index = (index + 1) % self.size
            if index == original_index:
                break
        return None

    def rehash(self):
        old_table = self.table
        self.size *= 2
        self.table = [None] * self.size
        self.count = 0
        for entry in old_table:
            if entry:
                self.insert(*entry)