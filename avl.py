from hash_table import HashTable
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1

class AVLRecord:
    def __init__(self):
        self.root = None
        self.hash_table = HashTable()

    def height(self, node):
        if not node:
            return 0
        return node.height

    def update_height(self, node):
        if not node:
            return
        node.height = 1 + max(self.height(node.left), self.height(node.right))

    def balance_factor(self, node):
        if not node:
            return 0
        return self.height(node.left) - self.height(node.right)

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
            return root  # Duplicate roll_no not allowed

        self.update_height(root)
        balance = self.balance_factor(root)

        # Rotations
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
            # Node with only one child or no child
            if not root.left:
                return root.right
            elif not root.right:
                return root.left

            # Node with two children
            temp = self.min_value_node(root.right)
            root.data = temp.data
            root.right = self.delete_node(root.right, temp.data['roll_no'])

        self.update_height(root)
        balance = self.balance_factor(root)

        # Rotations
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
        grades = grades or {
            "English": {"IA1": 0, "IA2": 0, "Final": 0},
            "Mathematics": {"IA1": 0, "IA2": 0, "Final": 0},
            "Physics": {"IA1": 0, "IA2": 0, "Final": 0},
            "Chemistry": {"IA1": 0, "IA2": 0, "Final": 0},
            "Second Language": {"IA1": 0, "IA2": 0, "Final": 0}
        }
        data = {
            "roll_no": roll_no,
            "name": name,
            "grades": grades,
            "status": status,
            "gpa": self.calculate_gpa(grades, status)
        }
        # Insert into AVL tree
        old_root = self.root
        self.root = self.insert(self.root, data)
        if self.root != old_root:  # Insertion successful
            # Insert into hash table
            if not self.hash_table.insert(name, roll_no, grades, status):
                # Revert AVL insertion if hash table fails (duplicate name)
                self.root = self.delete_node(self.root, roll_no)
                return False
            return True
        return False

    def remove_student(self, roll_no):
        # Find the student to get the name for hash table deletion
        node = self.search(roll_no)
        if not node:
            return False
        name = node.data["name"]
        # Delete from AVL tree
        self.root = self.delete_node(self.root, roll_no)
        # Delete from hash table
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
        return self.hash_table.search(name)

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
        result = self.inorder(self.root)
        for student in result:
            print(student)

# Demo
if __name__ == "__main__":
    record = AVLRecord()
    # Add students with grades
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

    print("All students (sorted by roll number):")
    record.print_inorder()

    print("\nSorted by name:")
    for student in record.sort_by_field("name"):
        print(student)

    print("\nRanked by GPA:")
    for student in record.get_ranked_list():
        print(student)

    print("\nSearch by name 'Shreya':")
    result = record.search_by_name("Shreya")
    print(result)

    print("\nAfter deleting roll_no 2:")
    record.remove_student(2)
    record.print_inorder()