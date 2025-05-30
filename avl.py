class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.height = 1

class AVLRecord:
    def __init__(self):
        self.root = None

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
        self.update_height(y)
        self.update_height(x)
        return y

    def insert(self, root, data):
        if not root:
            return TreeNode(data)
        if data['roll_no'] < root.data['roll_no']:
            root.left = self.insert(root.left, data)
        elif data['roll_no'] > root.data['roll_no']:
            root.right = self.insert(root.right, data)
        else:
            return root  # duplicate roll_no not allowed

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

            # Node with two children: get inorder successor
            temp = self.min_value_node(root.right)
            root.data = temp.data
            root.right = self.delete_node(root.right, temp.data['roll_no'])

        # Update and balance
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

    def add_student(self, data):
        self.root = self.insert(self.root, data)

    def remove_student(self, roll_no):
        self.root = self.delete_node(self.root, roll_no)

    def inorder(self, root):
        if not root:
            return []
        return self.inorder(root.left) + [root.data] + self.inorder(root.right)

    def print_inorder(self):
        result = self.inorder(self.root)
        for student in result:
            print(student)

# Demo
if __name__ == "__main__":
    record = AVLRecord()
    record.add_student({"roll_no": 1, "name": "Krishiv"})
    record.add_student({"roll_no": 3, "name": "Jogendar"})
    record.add_student({"roll_no": 6, "name": "Neeraj Pepsu"})
    record.add_student({"roll_no": 2, "name": "Dhinchak Pooja"})
    
    print("Before deletion:")
    record.print_inorder()

    record.remove_student(3)

    print("\nAfter deleting roll_no 3:")
    record.print_inorder()
