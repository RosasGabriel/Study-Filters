from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt

import sys
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

class InputWindow(QWidget): # Classe para a janela de entrada de valores
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrada de Valores")
        self.init_ui()

    def init_ui(self):
        # Labels para a interface gráfica
        sampling_rate_label = QLabel("Taxa de Amostragem (Hz):")
        duration_label      = QLabel("Duração em Segundos:")
        amplitude_label     = QLabel("Amplitude:")
        filter_label        = QLabel("Seletor de Filtro (0 para Passa-Baixas e 1 para Passa-Altas)")
        input_label         = QLabel("Seletor de Entrada (0 para White Noise e 1 para Sinal Variável)")
        frequency_label     = QLabel("Frequência do Sinal Variável(Hz):")

        # Editores de texto para a interface gráfica
        self.sampling_rate_entry = QLineEdit()
        self.duration_entry      = QLineEdit()
        self.amplitude_entry     = QLineEdit()
        self.filter_entry        = QLineEdit()
        self.input_entry         = QLineEdit()
        self.frequency_entry     = QLineEdit()

        # Botão para executar o programa
        run_button = QPushButton("Executar")
        run_button.clicked.connect(self.run_program)

        # Layout dos elementos da interface gráfica
        layout = QVBoxLayout()
        layout.addWidget(sampling_rate_label)
        layout.addWidget(self.sampling_rate_entry)
        layout.addWidget(duration_label)
        layout.addWidget(self.duration_entry)
        layout.addWidget(amplitude_label)
        layout.addWidget(self.amplitude_entry)
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_entry)
        layout.addWidget(input_label)
        layout.addWidget(self.input_entry)
        layout.addWidget(frequency_label)
        layout.addWidget(self.frequency_entry)
        layout.addWidget(run_button)

        self.setLayout(layout)

    def run_program(self):
        sampling_rate       = int(self.sampling_rate_entry.text())
        duration_in_seconds = int(self.duration_entry.text())
        amplitude           = float(self.amplitude_entry.text())
        filter_selector     = int(self.filter_entry.text())
        input_selector      = int(self.input_entry.text())
        frequency           = float(self.frequency_entry.text())

        durantion_in_samples = int(sampling_rate * duration_in_seconds)

        # Geração do "White Noise"
        white_noise = np.random.uniform(-1, 1, durantion_in_samples)

        # Geração do sinal variável
        time = np.linspace(0, duration_in_seconds, durantion_in_samples)
        variable_signal = amplitude * np.sin(2 * np.pi * frequency * time)

        # Seleção do sinal de entrada, entre "White Noise" e "Sinal Variável"
        if input_selector == 0:
            input_signal = white_noise
        elif input_selector == 1:
            input_signal = variable_signal

        cut_off_frequency = np.geomspace(20000, 20, input_signal.shape[0])  # Frequência de corte do filtro com base na frequência audível pelo ser humano

        allpass_output = np.zeros_like(input_signal)

        previous_output = 0

        for i in range(input_signal.shape[0]):  # Loop para cada amostra do sinal de entrada
            break_frequency = cut_off_frequency[i] # Frequência de corte do filtro

            tan = np.tan(np.pi * break_frequency / sampling_rate)   # Cálculo do valor tangente
            
            feedback_coefficient = (tan - 1) / (tan + 1) # Cálcuo do valor do coeficiente de feedback

            allpass_output[i] = feedback_coefficient * input_signal[i] + previous_output # Cálculo da saída do filtro

            previous_output = input_signal[i] - feedback_coefficient * allpass_output[i] # Cálculo do valor da saída anterior

        if filter_selector:
            allpass_output *= -1

        filter_output = input_signal + allpass_output

        filter_output *= 0.5

        filter_output *= amplitude

        # Plotagem dos sinais
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

        ax1.plot(input_signal)
        ax1.set_title("Sinal de Entrada - Antes da filtragem")
        ax1.set_ylabel("Amplitude")

        ax2.plot(filter_output)
        ax2.set_title("Sinal de Saída - Após a filtragem")
        ax2.set_ylabel("Amplitude")

        ax3.semilogy(cut_off_frequency)
        ax3.set_title("Frequências de Corte")
        ax3.set_xlabel("Amostras")
        ax3.set_ylabel("Frequência (Hz)")

        plt.tight_layout()
        plt.show()


        sd.play(filter_output, sampling_rate)
        sd.wait()

# Cria a aplicação Qt
app = QApplication(sys.argv)

# Cria a janela de entrada
input_window = InputWindow()
input_window.show()

# Execução da aplicação
sys.exit(app.exec_())
