from machine import Pin, PWM
from time import sleep_ms

class Buzzer:
    note_freq = {
        'P': 0, 'T':0,
        'C0': 16.35, 'C0#': 17.32, 'D0b': 17.32, 'D0': 18.35, 'D0#': 19.45, 'E0b': 19.45,
        'E0': 20.60, 'F0': 21.83, 'F0#': 23.12, 'G0b': 23.12, 'G0': 24.50, 'G0#': 25.96,
        'A0b': 25.96, 'A0': 27.50, 'A0#': 29.14, 'B0b': 29.14, 'B0': 30.87, 'C1': 32.70,
        'C1#': 34.65, 'D1b': 34.65, 'D1': 36.71, 'D1#': 38.89, 'E1b': 38.89, 'E1': 41.20,
        'F1': 43.65, 'F1#': 46.25, 'G1b': 46.25, 'G1': 49.00, 'G1#': 51.91, 'A1b': 51.91,
        'A1': 55.00, 'A1#': 58.27, 'B1b': 58.27, 'B1': 61.74, 'C2': 65.41, 'C2#': 69.30,
        'D2b': 69.30, 'D2': 73.42, 'D2#': 77.78, 'E2b': 77.78, 'E2': 82.41, 'F2': 87.31,
        'F2#': 92.50, 'G2b': 92.50, 'G2': 98.00, 'G2#': 103.83, 'A2b': 103.83, 'A2': 110.00,
        'A2#': 116.54, 'B2b': 116.54, 'B2': 123.47, 'C3': 130.81, 'C3#': 138.59, 'D3b': 138.59,
        'D3': 146.83, 'D3#': 155.56, 'E3b': 155.56, 'E3': 164.81, 'F3': 174.61, 'F3#': 185.00,
        'Gb3': 185.00, 'G3': 196.00, 'G3#': 207.65, 'Ab3': 207.65, 'A3': 220.00, 'A3#': 233.08,
        'Bb3': 233.08, 'B3': 246.94, 'C4': 261.63, 'C4#': 277.18, 'D4': 293.66, 'D4#': 311.13,
        'E4': 329.63, 'F4': 349.23, 'F4#': 369.99, 'G4': 392.00, 'G4#': 415.30, 'A4': 440.00,
        'A4#': 466.16, 'B4': 493.88, 'C5': 523.25, 'C5#': 554.37, 'D5': 587.33, 'D5#': 622.25,
        'E5': 659.25, 'F5': 698.46, 'F5#': 739.99, 'G5': 783.99, 'G5#': 830.61, 'A5': 880.00,
        'A5#': 932.33, 'B5': 987.77, 'C6': 1046.50, 'C6#': 1108.73, 'D6': 1174.66, 'D6#': 1244.51,
        'E6': 1318.51, 'F6': 1396.91, 'F6#': 1479.98, 'G6': 1567.98, 'G6#': 1661.22, 'A6': 1760.00,
        'A6#': 1864.66, 'B6': 1975.53, 'C7': 2093.00, 'C7#': 2217.46, 'D7': 2349.32, 'D7#': 2489.02,
        'E7': 2637.02, 'F7': 2793.83, 'F7#': 2959.96, 'G7': 3135.96, 'G7#': 3322.44, 'A7': 3520.00,
        'A7#': 3729.31, 'B7': 3951.07
    }
    demo_melody = [('T', 96), ('G4', 16), ('A4', 16), ('C5', 16), ('A4', 16), ('E5', 8.0),
                   ('E5', 8.0), ('D5', 4.0), ('G4', 16), ('A4', 16), ('B4', 16), ('G4', 16),
                   ('D5', 8.0), ('D5', 8.0), ('C5', 8.0), ('B4', 16), ('A4', 8), ('G4', 16),
                   ('A4', 16), ('B4', 16), ('G4', 16), ('C5', 8.0), ('D5', 8.0), ('B4', 8.0),
                   ('A4', 8.0), ('G4', 8), ('G4', 8), ('D5', 4), ('C5', 2)]

    bpm = 120
    def __init__(self, pin: Pin) -> None:
        self._pwm = PWM(pin)
        self._pwm.freq(1000)
        self._pwm.duty_u16(0)
        self.bpm = 72

    def note_duration(self, duration: int|float = 8) -> int:
        if isinstance(duration,float):
            return self.note_duration(int(duration))+self.note_duration(int(duration*2))
        return int(60000 / self.bpm / duration)*3
        
    def extract_bench_duration(self, melody: list) -> list[int]:
        duration = 0
        connections = 0
        if "L" in melody[0][0]:
            nuduration, nuconnections = self.extract_bench_duration(melody[1:])
            duration += nuduration
            connections += nuconnections
        duration += self.note_duration(melody[0][1])
        connections += 1
        return [duration, connections]

    def play_note(self, note: str, notelength: int) -> None:
        if note != 'P' and note != 'T':
            self._pwm.freq(int(self.note_freq[note]))
            self._pwm.duty_u16(32767)
            sleep_ms(notelength-10)
            self._pwm.duty_u16(0)
            sleep_ms(10)
        else:
            if note != 'T':
                sleep_ms(notelength)

    def play_melody(self, melody: list) -> None:
        connections = 0
        for i, note in enumerate(melody):
            if note[0] == 'T':
                self.bpm = note[1]
                continue
            #print(note)
            if connections > 0:
                connections -= 1
                #print("skip")
                continue
            duration, connections = self.extract_bench_duration(melody[i:])
            notename = note[0]
            if "L" in notename:
                notename = notename[:-1]
            #print(notename, duration)
            self.play_note(notename, duration)
            connections -= 1
    
    def play_melody_demo(self) -> None:
        backup_bpm = self.bpm
        self.bpm = 120
        self.play_melody(self.demo_melody)
        self.bpm = backup_bpm

    def beep(self, freq:int = 2000, duration:int = 100):
        self._pwm.freq(freq)
        self._pwm.duty_u16(32767)
        sleep_ms(duration-10)
        self._pwm.duty_u16(0)
        sleep_ms(10)

class Beep:
    def __init__(self, buzzer:Buzzer):
        self.buzzer = buzzer

    def __call__(self,freq:int=2000,duration:int=100):
        self.buzzer.beep(freq,duration)