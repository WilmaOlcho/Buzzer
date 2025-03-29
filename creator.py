from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import pyaudio
import numpy as np

class Staff(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Staff")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
        for i in range(1,6,1):
            y = (i + 1) * 10
            painter.drawLine(0, y, self.width(), y)
        # draw the treble clef
        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
        painter.drawLine(30, 10, 33, 70)
        painter.drawArc(23, 40, 16, 18, 0, 180*16)
        painter.drawArc(23, 40, 16, 13, 180*16, 45*16)
        painter.drawArc(16, 40, 22, 20, 180*16, 210*16)
        painter.drawArc(16, 40, 22, 20, 135*16, 45*16)
        painter.drawLine(18, 45, 35, 10)
        painter.drawArc(30, 5, 5, 5, 0, 180*16)
        painter.drawArc(28, 68, 5, 5, 180*16, 180*16)

        # draw the notes
        skip = 0
        for i, note in enumerate(self.parent().sound.notes):
            note_name, note_duration = note
            shift = 70 + (i+skip) * 20
            if note_name == 'P':
                match note_duration:
                    case 1:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 4))
                        painter.drawLine(shift, 32, shift + 8, 32)
                    case 2:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 4))
                        painter.drawLine(shift, 39, shift + 8, 39)
                    case 4:
                        pass #TODO draw quarter pause
                    case 8:
                        pass #TODO draw eighth pause
                    case 16:
                        pass #TODO draw sixteenth pause
                    case 32:
                        pass #TODO draw thirty-second pause
            elif note_name == 'T':
                skip += 1
            else:
                # draw the note
                dur = note_name.find('#')
                mol = note_name.find('b')
                note_name = note_name.replace('#', '').replace('b', '')
                y = 0
                match note_name:
                    case 'E3':
                        y = 90
                    case 'F3':
                        y = 85
                    case 'G3':
                        y = 80
                    case 'A4':
                        y = 75
                    case 'B4':
                        y = 70
                    case 'C4':
                        y = 65
                    case 'D4':
                        y = 60
                    case 'E4':
                        y = 55
                    case 'F4':
                        y = 50
                    case 'G4':
                        y = 45
                    case 'A5':
                        y = 40
                    case 'B5':
                        y = 35
                    case 'C5':
                        y = 30
                    case 'D5':
                        y = 25
                    case 'E5':
                        y = 20
                    case 'F5':
                        y = 15
                    case 'G5':
                        y = 10
                    case 'A6':
                        y = 5
                    case 'B6':
                        y = 0

                match note_duration:
                    case 1:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.drawEllipse(shift, y, 15, 10)
                        
                    case 2:
                        pass #TODO draw half note
                    case 4:
                        pass #TODO draw quarter note
                    case 8:
                        pass #TODO draw eighth note
                    case 16:
                        pass #TODO draw sixteenth note
                    case 32:
                        pass #TODO draw thirty-second note
                    

        painter.end()
        self.update()

class Sound:
    note_freqs = {
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
        
    def __init__(self, parent=None):
        self.parent = parent
        self.p = pyaudio.PyAudio()
        self.notes = []
        self._stream = None

    def add_note(self, note:tuple[str, int|float]) -> None:
        """
        Add a note to the list of notes.
        :param note: A tuple containing the note and its duration.
        """
        if isinstance(note, tuple) and len(note) == 2:
            note_name, note_duration = note
            if note_name in self.note_freqs.keys() and isinstance(note_duration, int|float) \
                or note_name in ['P', 'T'] and isinstance(note_duration, int|float):
                self.notes.append(note)

    def remove_note(self, note_index:int) -> None:
        if 0 <= note_index < len(self.notes):
            self.notes.pop(note_index)

    def clear_notes(self) -> None:
        self.notes = []

    def generate_sound(self, frequency:int|float, duration:int|float) -> np.ndarray:
        silence = 0.010 # seconds of silence
        duration = duration - silence
        sample_rate = 44100
        # Generate a time array
        t = (np.arange(sample_rate * duration) / sample_rate).astype(np.float32)
        # Generate a sinusoidal wave
        wave = 0.5 * np.sin(2 * np.pi * frequency * t)
        # convert to square wave
        wave = np.sign(wave)
        # Convert to Pafloat32
        wave = (wave * 32767).astype(np.float32)
        # Add silence at the end
        silence_end = np.zeros(int(sample_rate * silence), dtype=np.float32)
        wave = np.concatenate((wave, silence_end))
        return wave
    
    def generate_melody(self) -> np.ndarray:
        melody = np.array([], dtype=np.float32)
        # Default BPM
        bpm = 120
        for note, note_duration in self.notes:
            if note == 'T':
                bpm = note_duration
                continue
            duration = 60 / bpm * (4/note_duration)
            if isinstance(note_duration, float):
                duration += 60 / bpm * (4/note_duration)/2
            if note == 'P':
                # Pause, add silence
                silence = np.zeros(int(44100 * duration), dtype=np.float32)
                melody = np.concatenate((melody, silence))
                continue
            # Calculate frequency based on the note
            frequency = self.note_freq(note)
            # Generate sound for the note
            sound = self.generate_sound(frequency, duration)
            melody = np.concatenate((melody, sound))
        return melody

    def note_freq(self, note_name:str) -> int|float:
        """
        Get the frequency of a note.
        :param note_name: The name of the note.
        :return: The frequency of the note.
        """
        if note_name in self.note_freqs:
            return self.note_freqs[note_name]
        else:
            raise ValueError(f"Note {note_name} not found in frequency dictionary.")

    def play(self):
        """
        Play the generated melody.
        """
        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception as e:
                print(f"Error stopping stream: {e}")
        # Generate the melody
        melody = self.generate_melody()
        self._stream = self.p.open(format=pyaudio.paFloat32,
                             channels=1,
                             rate=44100,
                             output=True)
        self._stream.write(melody.tobytes())
        self._stream.stop_stream()
        self._stream.close()
        self._stream = None
        
class TopWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Top Widget")
        self.layout = QtWidgets.QHBoxLayout()
        self._parent = parent

        self.import_button = QtWidgets.QPushButton("Import")
        self.import_button.clicked.connect(self.import_notes)
        self.layout.addWidget(self.import_button)
        self.export_button = QtWidgets.QPushButton("Export")
        self.export_button.clicked.connect(self.export_notes)
        self.layout.addWidget(self.export_button)
        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.clicked.connect(self.play_notes)
        self.layout.addWidget(self.play_button)
        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_notes)
        self.layout.addWidget(self.clear_button)
        self.setLayout(self.layout)

    def import_notes(self):
        import_dialog = QtWidgets.QInputDialog(self)
        import_dialog.setWindowTitle("Import Notes")
        import_dialog.setLabelText("Enter the notes to import (comma-separated):")
        import_dialog.setTextValue("")
        if import_dialog.exec():
            notes_text = import_dialog.textValue()
            #extract tuples
            notes = []
            while len(notes_text) > 0:
                char = notes_text[0]
                if char in ['[', ']', ' ', "'", '"', '\n', '\r']:
                    notes_text = notes_text[1:]
                    continue
                if char == '(':
                    notes_text = notes_text[1:]
                    note = ''
                    while True:
                        char = notes_text[0]
                        if char == ')':
                            break
                        note += char
                        notes_text = notes_text[1:]
                    note = note.split(',')
                    note[0] = note[0].replace("'", "").replace('"', "").strip()
                    notes.append([note[0], note[1]])
                    notes_text = notes_text[1:]
                if char == ',':
                    notes_text = notes_text[1:]
            
            self._parent.sound.clear_notes()
            for note in notes:
                if note[1].find('.') > 0:
                    note[1] = float(note[1])
                else:
                    note[1] = int(note[1])
                self._parent.sound.add_note(tuple(note))
            self.parent().staff.update()

    def export_notes(self):
        export_dialog = QtWidgets.QInputDialog(self)
        export_dialog.setWindowTitle("Export Notes")
        export_dialog.setLabelText("Copy the notes to export")
        export_dialog.setTextValue(str(self._parent.sound.notes))
        export_dialog.setOkButtonText("Copy")
        export_dialog.setCancelButtonText("Close")

        if export_dialog.exec():
            notes_text = export_dialog.textValue()
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(notes_text)

    def play_notes(self):
        self._parent.sound.play()

    def clear_notes(self):
        self._parent.sound.clear_notes()

class Creator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creator")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QtWidgets.QVBoxLayout()
        self.sound = Sound(self)

        self.top = TopWidget(self)
        self.staff = Staff(self)
        self.layout.addWidget(self.top, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.staff)
        

        # Set the layout for the widget
        self.setLayout(self.layout)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    creator = Creator()
    creator.show()
    sys.exit(app.exec())