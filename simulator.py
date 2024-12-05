import math
import random

class Qubit:
    def __init__(self):
        self.alpha = 1.0  # Amplitude von |0⟩
        self.beta = 0.0   # Amplitude von |1⟩

    def apply_hadamard(self):
        alpha_new = (self.alpha + self.beta) / math.sqrt(2)
        beta_new = (self.alpha - self.beta) / math.sqrt(2)
        self.alpha = alpha_new
        self.beta = beta_new

    def apply_pauli_x(self):
        self.alpha, self.beta = self.beta, self.alpha

    def apply_pauli_y(self):
        self.alpha, self.beta = -self.beta, self.alpha

    def apply_pauli_z(self):
        self.beta = -self.beta

    def apply_cnot(self, control_qubit):
        if control_qubit.measure() == 1:
            self.apply_pauli_x()

    def apply_toffoli(self, control_qubit_1, control_qubit_2):
        if control_qubit_1.measure() == 1 and control_qubit_2.measure() == 1:
            self.apply_pauli_x()

    def apply_swap(self, other_qubit):
        self.alpha, other_qubit.alpha = other_qubit.alpha, self.alpha
        self.beta, other_qubit.beta = other_qubit.beta, self.beta

    def measure(self):
        probability_zero = self.alpha ** 2
        random_value = random.random()
        if random_value < probability_zero:
            self.alpha = 1.0
            self.beta = 0.0
            return 0
        else:
            self.alpha = 0.0
            self.beta = 1.0
            return 1

    def get_state_vector(self):
        return (self.alpha, self.beta)

class QuantumRegister:
    def __init__(self, size):
        self.qubits = [Qubit() for _ in range(size)]

    def apply_hadamard(self, index):
        self.qubits[index].apply_hadamard()

    def apply_pauli_x(self, index):
        self.qubits[index].apply_pauli_x()

    def apply_pauli_y(self, index):
        self.qubits[index].apply_pauli_y()

    def apply_pauli_z(self, index):
        self.qubits[index].apply_pauli_z()

    def apply_cnot(self, control_index, target_index):
        self.qubits[target_index].apply_cnot(self.qubits[control_index])

    def apply_toffoli(self, control_1_index, control_2_index, target_index):
        self.qubits[target_index].apply_toffoli(self.qubits[control_1_index], self.qubits[control_2_index])

    def apply_swap(self, index_1, index_2):
        self.qubits[index_1].apply_swap(self.qubits[index_2])

    def measure_all(self):
        return [qubit.measure() for qubit in self.qubits]

    def get_state_vector(self):
        return [qubit.get_state_vector() for qubit in self.qubits]

class ClassicalRegister:
    def __init__(self, size):
        self.bits = [0] * size

    def store_result(self, index, value):
        self.bits[index] = value

    def get_result(self, index):
        return self.bits[index]

class QuantumComputer:
    def __init__(self):
        self.qreg = None
        self.creg = None

    def execute_qscript(self, script):
        lines = script.splitlines()
        loop_stack = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("#"):  # Leere Zeilen und Kommentare überspringen
                i += 1
                continue
            parts = line.split()
            command = parts[0]

            if command == "QREG":
                size = int(parts[1])
                self.qreg = QuantumRegister(size)
                print(f"Quantum Register initialized with {size} qubits.")

            elif command == "CREG":
                size = int(parts[1])
                self.creg = ClassicalRegister(size)
                print(f"Classical Register initialized with {size} bits.")

            elif command == "H":
                self.qreg.apply_hadamard(int(parts[1]))

            elif command == "X":
                self.qreg.apply_pauli_x(int(parts[1]))

            elif command == "Y":
                self.qreg.apply_pauli_y(int(parts[1]))

            elif command == "Z":
                self.qreg.apply_pauli_z(int(parts[1]))

            elif command == "CNOT":
                control_index = int(parts[1])
                target_index = int(parts[2])
                self.qreg.apply_cnot(control_index, target_index)

            elif command == "TOFFOLI":
                control_1_index = int(parts[1])
                control_2_index = int(parts[2])
                target_index = int(parts[3])
                self.qreg.apply_toffoli(control_1_index, control_2_index, target_index)

            elif command == "SWAP":
                index_1 = int(parts[1])
                index_2 = int(parts[2])
                self.qreg.apply_swap(index_1, index_2)

            elif command == "MEASURE":
                qubit_index = int(parts[1])
                creg_index = int(parts[2])
                measurement = self.qreg.measure_all()[qubit_index]
                self.creg.store_result(creg_index, measurement)

            elif command == "PRINT":
                creg_index = int(parts[1])
                print(f"Classical Register {creg_index}: {self.creg.get_result(creg_index)}")

            elif command == "PRINT_STATE":
                print("State vector:", self.qreg.get_state_vector())

            elif command == "LOOP":
                count = int(parts[1])
                loop_stack.append((i, count))

            elif command == "ENDLOOP":
                loop_start, loop_count = loop_stack.pop()
                loop_count -= 1
                if loop_count > 0:
                    loop_stack.append((loop_start, loop_count))
                    i = loop_start

            elif command == "IF":
                creg_index = int(parts[1])
                value = int(parts[2])
                if self.creg.get_result(creg_index) != value:
                    while i < len(lines) and not lines[i].strip().startswith("ENDIF"):
                        i += 1

            elif command == "ENDIF":
                pass  # End of conditional block

            elif command == "MEASURE_N":
                qubit_index = int(parts[1])
                creg_index = int(parts[2])
                n = int(parts[3])
                results = [self.qreg.measure_all()[qubit_index] for _ in range(n)]
                avg_result = round(sum(results) / n)
                self.creg.store_result(creg_index, avg_result)

            i += 1

# Beispielnutzung
qc = QuantumComputer()

file_name = input("filename: ")

with open(f"./scripts/{file_name}", "r") as qscript:
	qc.execute_qscript(qscript.read())
