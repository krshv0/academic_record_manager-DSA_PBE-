def get_letter_grade(score):
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    else:
        return "F"


from datetime import datetime
import csv

class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1


class HashTable:
    def __init__(self):
        self.table = {}  # name (lowercase) → { roll_no: student_dict }

    def insert(self, name, roll_number, grades, status):
        name = name.lower().strip()
        if name not in self.table:
            self.table[name] = {}
        if roll_number in self.table[name]:
            return False  # Duplicate
        self.table[name][roll_number] = {
            "grades": grades,
            "status": status
        }
        return True

    def search(self, name):
        name = name.lower().strip()
        if name not in self.table:
            return None
        matches = []
        for roll_no, student in self.table[name].items():
            matches.append({
                "roll_no": roll_no,
                "name": name,
                "grades": student["grades"],
                "status": student["status"],
                "gpa": AVLRecord.calculate_gpa_static(student["grades"], student["status"])
            })
        return matches

    def delete(self, name, roll_no):
        name = name.lower().strip()
        if name in self.table and roll_no in self.table[name]:
            del self.table[name][roll_no]
            if not self.table[name]:
                del self.table[name]  # Clean up if list becomes empty
            return True
        return False


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

    @staticmethod
    def calculate_gpa_static(grades, status):
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
            "gpa": self.calculate_gpa_static(grades, status)
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
        return self.hash_table.delete(name, roll_no)

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

    def export_ranked_list_to_csv(self, file_path=None):
        ranked = self.get_ranked_list()
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"ranked_student_records_{timestamp}.csv"

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Rank", "Roll No", "Name", "GPA", "Status"])
                for s in ranked:
                    writer.writerow([s["rank"], s["roll_no"], s["name"], s["gpa"], s["status"]])
            print(f"✅ Ranked list successfully exported to: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to export ranked list: {e}")
            return False
    
