class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1


class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * size
        self.count = 0
        self.load_factor_threshold = 0.75

    def hash_function(self, name):
        name = name.lower()
        total = 0
        for i, char in enumerate(name):
            total += ord(char) * (31 ** i)
        return total % self.size

    def insert(self, name, roll_number, grades, status):
        name = name.lower()
        if self.count / self.size >= self.load_factor_threshold:
            print(f"Rehashing: Current count={self.count}, size={self.size}")
            self.rehash()
        index = self.hash_function(name)
        original_index = index
        while self.table[index] is not None:
            if self.table[index][0] == name:
                print(f"Duplicate name detected: {name}")
                return False
            index = (index + 1) % self.size
            if index == original_index:
                print("Hash table full, rehashing failed")
                return False
        self.table[index] = (name, roll_number, grades, status)
        self.count += 1
        print(f"Inserted {name} at index {index}")
        return True

    def search(self, name):
        name = name.lower()
        index = self.hash_function(name)
        original_index = index
        while self.table[index] is not None:
            if self.table[index][0] == name:
                name, roll_no, grades, status = self.table[index]
                return {
                    "roll_no": roll_no,
                    "name": name,
                    "grades": grades,
                    "status": status,
                    "gpa": AVLRecord().calculate_gpa(grades, status)
                }
            index = (index + 1) % self.size
            if index == original_index:
                break
        return None

    def delete(self, name):
        name = name.lower()
        index = self.hash_function(name)
        original_index = index
        while self.table[index] is not None:
            if self.table[index][0] == name:
                self.table[index] = None
                self.count -= 1
                print(f"Deleted {name} from index {index}")
                return True
            index = (index + 1) % self.size
            if index == original_index:
                break
        print(f"Name {name} not found for deletion")
        return False

    def rehash(self):
        old_table = self.table
        self.size *= 2
        self.table = [None] * self.size
        self.count = 0
        for entry in old_table:
            if entry:
                self.insert(*entry)


class AVLRecord:
    def __init__(self):
        self.root = None
        self.hash_table = HashTable()

    def height(self, node):
        return node.height if node else 0

    def update_height(self, node):
        if node:
            node.height = 1 + max(self.height(node.left), self.height(node.right))

    def balance_factor(self, node):
        return self.height(node.left) - self.height(node.right) if node else 0

    def right_rotate(self, y):
        x = y.left
        T2 = x.right
        x.right = y
        y.left = T2
        self.update_height(y)
        self.update_height(x)
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2
        self.update_height(x)
        self.update_height(y)
        return y

    def insert(self, root, data):
        if not root:
            return TreeNode(data)
        if data['roll_no'] < root.data['roll_no']:
            root.left = self.insert(root.left, data)
        elif data['roll_no'] > root.data['roll_no']:
            root.right = self.insert(root.right, data)
        else:
            print(f"Duplicate roll_no {data['roll_no']} detected")
            return root

        self.update_height(root)
        balance = self.balance_factor(root)

        if balance > 1 and data['roll_no'] < root.left.data['roll_no']:
            return self.right_rotate(root)
        if balance < -1 and data['roll_no'] > root.right.data['roll_no']:
            return self.left_rotate(root)
        if balance > 1 and data['roll_no'] > root.left.data['roll_no']:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and data['roll_no'] < root.right.data['roll_no']:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def delete_node(self, root, roll_no):
        if not root:
            return root

        if roll_no < root.data['roll_no']:
            root.left = self.delete_node(root.left, roll_no)
        elif roll_no > root.data['roll_no']:
            root.right = self.delete_node(root.right, roll_no)
        else:
            if not root.left:
                return root.right
            elif not root.right:
                return root.left
            temp = self.min_value_node(root.right)
            root.data = temp.data
            root.right = self.delete_node(root.right, temp.data['roll_no'])

        self.update_height(root)
        balance = self.balance_factor(root)

        if balance > 1 and self.balance_factor(root.left) >= 0:
            return self.right_rotate(root)
        if balance > 1 and self.balance_factor(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)
        if balance < -1 and self.balance_factor(root.right) <= 0:
            return self.left_rotate(root)
        if balance < -1 and self.balance_factor(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def calculate_gpa(self, grades, status):
        if status == "Absent":
            return 0.0
        total = 0
        count = 0
        for subject, scores in grades.items():
            if status == "Medical Leave" and scores["Final"] == 0:
                valid_scores = [scores["IA1"], scores["IA2"]]
                valid_scores = [s for s in valid_scores if s > 0]
                if valid_scores:
                    total += sum(valid_scores) / len(valid_scores)
                    count += 1
            else:
                score = (scores["IA1"] * 0.25) + (scores["IA2"] * 0.25) + (scores["Final"] * 0.50)
                total += score
                count += 1
        return round(total / count, 2) if count > 0 else 0.0

    def add_student(self, roll_no, name, grades=None, status="Present"):
        default_subjects = ["English", "Mathematics", "Physics", "Chemistry", "Second Language"]
        grades = grades or {}
        for subject in default_subjects:
            if subject not in grades:
                grades[subject] = {"IA1": 0, "IA2": 0, "Final": 0}

        if self.search(roll_no):
            print(f"Failed to insert roll_no {roll_no} — already exists")
            return False

        data = {
            "roll_no": roll_no,
            "name": name,
            "grades": grades,
            "status": status,
            "gpa": self.calculate_gpa(grades, status)
        }

        self.root = self.insert(self.root, data)

        if not self.hash_table.insert(name, roll_no, grades, status):
            self.root = self.delete_node(self.root, roll_no)
            print(f"Failed to insert {name} into hash table")
            return False

        print(f"Successfully added student {name} (roll_no: {roll_no})")
        return True

    def remove_student(self, roll_no):
        node = self.search(roll_no)
        if not node:
            print(f"Roll_no {roll_no} not found for deletion")
            return False
        name = node.data["name"]
        self.root = self.delete_node(self.root, roll_no)
        return self.hash_table.delete(name)

    def search(self, roll_no):
        current = self.root
        while current:
            if roll_no < current.data['roll_no']:
                current = current.left
            elif roll_no > current.data['roll_no']:
                current = current.right
            else:
                return current
        return None

    def search_by_name(self, name):
        result = self.hash_table.search(name)
        if result:
            print(f"Search by name successful for {name}")
            return result
        print(f"Search by name failed for {name}")
        return None

    def inorder(self, root):
        if not root:
            return []
        return self.inorder(root.left) + [root.data] + self.inorder(root.right)

    def sort_by_field(self, field, reverse=False):
        records = self.inorder(self.root)
        return sorted(records, key=lambda x: x[field], reverse=reverse)

    def get_ranked_list(self):
        records = self.sort_by_field("gpa", reverse=True)
        ranked = []
        current_rank = 1
        prev_gpa = None
        for i, record in enumerate(records, 1):
            if prev_gpa is not None and record["gpa"] != prev_gpa:
                current_rank = i
            ranked.append({**record, "rank": current_rank})
            prev_gpa = record["gpa"]
        return ranked

    def print_inorder(self):
        records = self.inorder(self.root)
        print("\nStudent Records (In-order by Roll Number):")
        print("-" * 80)
        print(f"{'Roll No':<10}{'Name':<20}{'GPA':<10}{'Status':<15}")
        print("-" * 80)
        for s in records:
            print(f"{s['roll_no']:<10}{s['name']:<20}{s['gpa']:<10}{s['status']:<15}")
    
    def print_ranked_list(self):
        ranked = self.get_ranked_list()
        print("\nRanked Student List (by GPA):")
        print("-" * 70)
        print(f"{'Rank':<6}{'Roll No':<10}{'Name':<20}{'GPA':<10}{'Status'}")
        print("-" * 70)
        for student in ranked:
            print(f"{student['rank']:<6}{student['roll_no']:<10}{student['name']:<20}{student['gpa']:<10}{student['status']}")

    def print_sorted_by_field(self, field, reverse=False):
        records = self.sort_by_field(field, reverse)
        print(f"\nStudent Records Sorted by {field.capitalize()}:")
        print("-" * 80)
        print(f"{'Roll No':<10}{'Name':<20}{'GPA':<10}{'Status':<15}")
        print("-" * 80)
        for s in records:
            print(f"{s['roll_no']:<10}{s['name']:<20}{s['gpa']:<10}{s['status']:<15}")


# DEMO
if __name__ == "__main__":
    record = AVLRecord()

    record.add_student(1, "Krishiv", {
        "English": {"IA1": 80, "IA2": 85, "Final": 90},
        "Mathematics": {"IA1": 75, "IA2": 80, "Final": 85}
    })

    record.add_student(2, "Shreya", {
        "English": {"IA1": 90, "IA2": 95, "Final": 92},
        "Mathematics": {"IA1": 88, "IA2": 90, "Final": 87}
    })

    record.add_student(3, "Farah", {
        "English": {"IA1": 70, "IA2": 0, "Final": 0},
        "Mathematics": {"IA1": 65, "IA2": 0, "Final": 0}
    }, status="Medical Leave")

    record.add_student(4, "Zunaira", {
        "English": {"IA1": 0, "IA2": 0, "Final": 0},
        "Mathematics": {"IA1": 0, "IA2": 0, "Final": 0}
    }, status="Absent")

    record.print_inorder()

    print("\nSearch by name 'Krishiv':")
    print(record.search_by_name("Krishiv"))

    print("\nSearch by name 'NonExistent':")
    print(record.search_by_name("NonExistent"))

    print("\nAfter deleting roll_no 2:")
    record.remove_student(2)
    record.print_inorder()

    print("\nSearch by name 'Shreya' after deletion:")
    print(record.search_by_name("Shreya"))

    print(record.print_ranked_list())
