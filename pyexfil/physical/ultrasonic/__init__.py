#!/usr/bin/env python3
import sys

import sounddevice as sd
import numpy as np
import scipy.signal as signal
import scipy.stats as stats

from pyexfil.includes.prepare import rc4, DEFAULT_KEY



class UltrasonicReceiver:
    """
    A class that performs QAM demodulation on audio input.

    Args:
        fs (int): Sampling frequency.
        fc (int): Carrier frequency.
        symbol_duration (float): Duration of each symbol.
        bits_per_symbol (int): Number of bits per symbol.
        modulation_order (int): Order of the QAM modulation.

    Attributes:
        fs (int): Sampling frequency.
        fc (int): Carrier frequency.
        symbol_duration (float): Duration of each symbol.
        bits_per_symbol (int): Number of bits per symbol.
        modulation_order (int): Order of the QAM modulation.

    Methods:
        receive(): Continuously reads audio input and demodulates the QAM signal.

    """

    def __init__(self, fs=48000, fc=22000, symbol_duration=0.01, bits_per_symbol=4, modulation_order=16):
        """
        Initializes the QAMReceiver object with the specified parameters.

        Args:
            fs (int): Sampling frequency.
            fc (int): Carrier frequency.
            symbol_duration (float): Duration of each symbol.
            bits_per_symbol (int): Number of bits per symbol.
            modulation_order (int): Order of the QAM modulation.
        """
        self.fs = fs
        self.fc = fc
        self.symbol_duration = symbol_duration
        self.bits_per_symbol = bits_per_symbol
        self.modulation_order = modulation_order

        # create QAM demodulator
        self.qam_demodulator = signal.qamdemod(np.arange(self.modulation_order), self.modulation_order)

    def receive(self):
        """
        Continuously reads audio input and demodulates the QAM signal.
        """
        while True:
            try:
                # read modulated signal from default audio input device
                recorded_signal = sd.rec(int(self.fs * self.symbol_duration * 256), samplerate=self.fs, channels=1)
                sd.wait()

                # demodulate QAM signal
                demodulated_signal = np.ravel(self.qam_demodulator(signal.medfilt(np.abs(signal.hilbert(recorded_signal)), kernel_size=31)))

                # convert demodulated signal to digital signal
                decoded_signal = np.array([], dtype=int)
                for i in range(0, len(demodulated_signal), self.bits_per_symbol):
                    symbol = demodulated_signal[i:i+self.bits_per_symbol]
                    decoded_signal = np.append(decoded_signal, np.unpackbits(np.array([symbol]))[-self.bits_per_symbol:])

                # output received digital signal
                print(decoded_signal)

            except Exception as e:
                print(f"Error: {e}")


class UltrasonicTransmitter:
    """
    A class that performs QAM modulation and transmits the modulated signal over audio.

    Args:
        fs (int): Sampling frequency.
        fc (int): Carrier frequency.
        symbol_duration (float): Duration of each symbol.
        bits_per_symbol (int): Number of bits per symbol.
        modulation_order (int): Order of the QAM modulation.
        noise_level (float): Level of noise to add to the modulated signal.

    Attributes:
        fs (int): Sampling frequency.
        fc (int): Carrier frequency.
        symbol_duration (float): Duration of each symbol.
        bits_per_symbol (int): Number of bits per symbol.
        modulation_order (int): Order of the QAM modulation.
        noise_level (float): Level of noise to add to the modulated signal.

    Methods:
        transmit(digital_signal): Modulates and transmits the digital signal.

    """

    def __init__(self, fs=48000, fc=22000, symbol_duration=0.01, bits_per_symbol=4,
                 modulation_order=16, noise_level=0.1):
        """
        Initializes the QAMTransmitter object with the specified parameters.

        Args:
            fs (int): Sampling frequency.
            fc (int): Carrier frequency.
            symbol_duration (float): Duration of each symbol.
            bits_per_symbol (int): Number of bits per symbol.
            modulation_order (int): Order of the QAM modulation.
            noise_level (float): Level of noise to add to the modulated signal.
        """
        self.fs = fs
        self.fc = fc
        self.symbol_duration = symbol_duration
        self.bits_per_symbol = bits_per_symbol
        self.modulation_order = modulation_order
        self.noise_level = noise_level

    def transmit(self, digital_signal):
        """
        Modulates and transmits the digital signal using QAM.

        Args:
            digital_signal (numpy.ndarray): The digital signal to transmit.

        """
        try:
            # create QAM modulator
            qam_modulator = signal.qammod(np.arange(self.modulation_order), self.modulation_order)

            # reshape digital signal to match number of bits per symbol
            digital_signal = np.reshape(digital_signal, (-1, self.bits_per_symbol))

            # QAM modulate digital signal
            qam_signal = qam_modulator(np.ravel(digital_signal))

            # add noise to the modulated signal
            noisy_signal = qam_signal + self.noise_level * stats.norm.rvs(size=qam_signal.shape)

            # generate carrier signal
            t = np.arange(0, len(noisy_signal) / self.fs, 1 / self.fs)
            carrier = np.sin(2 * np.pi * self.fc * t)

            # modulate signal onto carrier
            modulated_signal = np.multiply(noisy_signal, carrier)

            # play modulated signal over the default audio output device
            sd.play(modulated_signal, self.fs)

            # wait for signal transmission to finish
            sd.wait()
        except Exception as e:
            print(f"Error: {e}")


    def encode_data(data):
        """
        Encodes a string or bytes object as a NumPy array of bits for transmission.

        Args:
            data (str or bytes): The string or bytes object to encode.

        Returns:
            numpy.ndarray: The encoded data as a NumPy array of bits.
        """
        # Convert data to bytes if it is a string
        if isinstance(data, str):
            data = data.encode()

        # Convert data to a NumPy array of bits
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))

        return bits


if __name__ == "__main__":
    sys.stderr.write("This is a module, not a stand alone file. Please import it instead.\n")
    sys.exit(1)