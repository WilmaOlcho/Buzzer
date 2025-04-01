from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import pyaudio
import numpy as np

class ScrollStaff(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.staff = Staff(self.parent())
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWidget(self.staff)

    @property
    def pause_mode(self):
        return self.staff.pause_mode
    
    @pause_mode.setter
    def pause_mode(self, value):
        self.staff.pause_mode = value

    def dot(self):
        self.staff.dot()

    def mol(self):
        self.staff.mol()

    def dur(self):
        self.staff.dur()
    

    


class Staff(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Staff")
        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.mousePressEvent = self.clickEvent
        self.pause_mode = False

    def extractYFromNoteName(self, G4_pos, staf_height, note_name):
        y = G4_pos
        staf_height /= 2
        match note_name:
            case 'E3': y += staf_height * 9
            case 'F3': y += staf_height * 8
            case 'G3': y += staf_height * 7
            case 'A3': y += staf_height * 6
            case 'B3': y += staf_height * 5
            case 'C4': y += staf_height * 4
            case 'D4': y += staf_height * 3
            case 'E4': y += staf_height * 2
            case 'F4': y += staf_height
            case 'G4': pass
            case 'A4': y -= staf_height
            case 'B4': y -= staf_height * 2
            case 'C5': y -= staf_height * 3
            case 'D5': y -= staf_height * 4
            case 'E5': y -= staf_height * 5
            case 'F5': y -= staf_height * 6
            case 'G5': y -= staf_height * 7
            case 'A5': y -= staf_height * 8
            case 'B5': y -= staf_height * 9
        return int(y)

    def drawNotes(self, painter, G4_pos, staf_height):
        skip = 0
        parent = self.parent().parent().parent()
        for i, note in enumerate(parent.sound.notes):
            note_name, note_duration = note
            dur = note_name.find('#') != -1
            mol = note_name.find('b') != -1
            dot = isinstance(note_duration, float)
            note_duration = int(note_duration)
            note_name = note_name.replace('#', '').replace('b', '')
            y = self.extractYFromNoteName(G4_pos,staf_height,note_name)
            shift = 60 + (i-skip) * 45
            if dot:
                painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
                painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.Black))
                painter.drawEllipse(shift+18, y+4, 3, 3)
            if note_name == 'P':
                match note_duration:
                    case 1:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 4))
                        painter.drawLine(shift, 32, shift + 8, 32)
                    case 2:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 4))
                        painter.drawLine(shift, 39, shift + 8, 39)
                    case 4:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.drawLine(shift, 30, shift + 5, 36)
                        painter.drawLine(shift+5, 36, shift, 42)
                        painter.drawLine(shift, 42, shift+5, 48)
                        painter.drawArc(shift,48,5,5,90*16,150*16)
                    case 8:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
                        painter.drawLine(shift, 48, shift + 5, 30)
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.drawArc(shift,30,5,3,180*16,180*16)
                    case 16:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
                        painter.drawLine(shift, 48, shift + 5, 30)
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.drawArc(shift,30,5,3,180*16,180*16)
                        painter.drawArc(shift-2,35,5,3,180*16,180*16)
                    case 32:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
                        painter.drawLine(shift, 48, shift + 5, 30)
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.drawArc(shift,30,5,3,180*16,180*16)
                        painter.drawArc(shift-2,35,5,3,180*16,180*16)
                        painter.drawArc(shift-4,40,5,3,180*16,180*16)
            elif note_name == 'T':
                skip += 1
                continue
            else:
                if dur:
                    painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
                    painter.drawLine(shift+18, y-11, shift+18, y-2)
                    painter.drawLine(shift+21, y-11, shift+21, y-2)
                    painter.drawLine(shift+15, y-8, shift+24, y-8)
                    painter.drawLine(shift+15, y-5, shift+24, y-5)
                if mol:
                    painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
                    painter.setFont(QtGui.QFont("Arial", 10))
                    painter.drawText(shift+15, y-2, 'b')
                match note_duration:
                    case 1:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.drawEllipse(shift, y, 15, 10)
                    case 2:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.drawEllipse(shift, y, 15, 10)
                        if y < 45:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y + 45)
                        else:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y - 40)
                    case 4:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.Black))
                        painter.drawEllipse(shift, y, 15, 10)
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.White))
                        
                        if y < 45:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y + 45)
                        else:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y - 40)
                    case 8:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.Black))
                        painter.drawEllipse(shift, y, 15, 10)
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.White))
                        if y < 45:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y + 35)
                            painter.drawArc(shift, y+5, 30, 30, -90*16, 75*16)
                        else:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y - 30)
                            painter.drawArc(shift, y - 30, 30, 30, 90*16, -75*16)
                    case 16:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.Black))
                        painter.drawEllipse(shift, y, 15, 10)
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.White))
                        if y < 45:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y + 35)
                            painter.drawArc(shift, y, 30, 30, -90*16, 75*16)
                            painter.drawArc(shift, y+5, 30, 30, -90*16, 75*16)
                        else:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y - 30)
                            painter.drawArc(shift, y - 25, 30, 30, 90*16, -75*16)
                            painter.drawArc(shift, y - 30, 30, 30, 90*16, -75*16)
                    case 32:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.Black))
                        painter.drawEllipse(shift, y, 15, 10)
                        painter.setBrush(QtGui.QBrush(QtGui.QColorConstants.White))
                        if y < 45:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y + 35)
                            painter.drawArc(shift, y-5, 30, 30, -90*16, 75*16)
                            painter.drawArc(shift, y, 30, 30, -90*16, 75*16)
                            painter.drawArc(shift, y+5, 30, 30, -90*16, 75*16)
                        else:
                            painter.drawLine(shift + 15, y + 5, shift + 15, y - 30)
                            painter.drawArc(shift, y - 20, 30, 30, 90*16, -75*16)
                            painter.drawArc(shift, y - 25, 30, 30, 90*16, -75*16)
                            painter.drawArc(shift, y - 30, 30, 30, 90*16, -75*16)
                    case _:
                        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Blue, 2))
                        painter.drawEllipse(shift, y, 15, 10)
    
    def drawTrebleClef(self, x, y, painter):
        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 2))
        painter.drawLine(x, y, x+3, y+60)
        painter.drawArc(x-7, y+30, 16, 18, 0, 180*16)
        painter.drawArc(x-7, y+30, 16, 13, 180*16, 45*16)
        painter.drawArc(x-14, y+30, 22, 20, 180*16, 210*16)
        painter.drawArc(x-14, y+30, 22, 20, 135*16, 45*16)
        painter.drawLine(x-12, y+35, 35, 10)
        painter.drawArc(x, y-5, 5, 5, 0, 180*16)
        painter.drawArc(x-2, y+58, 5, 5, 180*16, 180*16)

    def resizeStaff(self):
        parent = self.parent().parent().parent()
        sound_length = len(parent.sound.notes) - len(list(filter(lambda x: x[0] == 'T', parent.sound.notes)))
        width = 60 + sound_length * 45
        if width < self.width():
            width = self.width()
        self.setMinimumWidth(width)

    def drawNoteName(self, painter):
        parent = self.parent().parent().parent()
        cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        note_index = round((cursor.x() - 60) / 45)
        skips = 0      
        if note_index < len(parent.sound.notes) and note_index >= 0:
            for i in range(note_index+1):
                if parent.sound.notes[i][0] == 'T':
                    skips += 1  
            note_index += skips
            name = parent.sound.notes[note_index][0]
            name = name.replace('#', '').replace('b', '')
            pos_y = self.extractYFromNoteName(45,10,name)
            if cursor.y() > pos_y - 10 and cursor.y() < pos_y + 10:
                painter.setPen(QtGui.QPen(QtGui.QColorConstants.Red, 1))
                painter.setFont(QtGui.QFont("Arial", 10))
                painter.drawText(cursor.x()+5, cursor.y() + 5, name)

    def drawStaff(self, painter):
        painter.setPen(QtGui.QPen(QtGui.QColorConstants.Black, 1))
        for i in range(1,6,1):
            y = (i + 1) * 10
            painter.drawLine(0, y, self.width(), y)

    def paintEvent(self, event):
        self.resizeStaff()
        painter = QtGui.QPainter(self)
        self.drawStaff(painter)
        try:
            self.drawTrebleClef(30, 10, painter)
            self.drawNotes(painter, 45, 10)
            self.drawNoteName(painter)
        except Exception as e:
            print(f"Error drawing notes: {e}")
        painter.end()
        self.update()

    def noteIndex(self, x):
        parent = self.parent().parent().parent()
        note_index = round((x - 60) / 45)
        skips = 0
        if note_index < len(parent.sound.notes) and note_index >= 0:
            for i in range(note_index+1):
                if parent.sound.notes[i][0] == 'T':
                    skips += 1  
            note_index += skips
        return note_index

    def clickEvent(self, event):
        parent = self.parent().parent().parent()
        cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        note_index = self.noteIndex(cursor.x())
        if event.button() == Qt.MouseButton.RightButton:    
                parent.sound.remove_note(note_index)
                self.update()
        elif event.button() == Qt.MouseButton.LeftButton:
            durations = [1, 2, 4, 8, 16, 32]
            note_name = ''
            note_duration = 0
            if note_index >= len(parent.sound.notes):
                if self.pause_mode:
                    note_name = 'P'
                    note_duration = 1
                else:
                    note_index = len(parent.sound.notes)
                    note_name = self.note_from_y(cursor.y())
                    note_duration = 1
                parent.sound.add_note((note_name, note_duration))
                self.update()
            else:
                if self.pause_mode:
                    note_name = 'P'
                else:
                    note_name = self.note_from_y(cursor.y())
                duration_index = durations.index(parent.sound.notes[note_index][1])
                if duration_index == len(durations) - 1:
                    duration_index = 0
                else:
                    duration_index += 1
                note_duration = durations[duration_index]
                parent.sound.notes[note_index] = (note_name, note_duration)
                self.update()

    def dot(self):
        parent = self.parent().parent().parent()
        note_index = self.noteIndex(self.mapFromGlobal(QtGui.QCursor.pos()).x())
        if note_index < len(parent.sound.notes):
            note_name, note_duration = parent.sound.notes[note_index]
            if isinstance(note_duration, float):
                note_duration = int(note_duration)
            elif isinstance(note_duration, int):
                note_duration = float(note_duration)
            parent.sound.notes[note_index] = (note_name, note_duration)
    
    def mol(self):
        parent = self.parent().parent().parent()
        note_index = self.noteIndex(self.mapFromGlobal(QtGui.QCursor.pos()).x())
        if note_index < len(parent.sound.notes):
            note_name, note_duration = parent.sound.notes[note_index]
            note_name = note_name.replace('#', 'b')
            if note_name.find('b') == -1:
                note_name += 'b'
            else:
                note_name = note_name.replace('b', '')
            parent.sound.notes[note_index] = (note_name, note_duration)

    def dur(self):
        parent = self.parent().parent().parent()
        note_index = self.noteIndex(self.mapFromGlobal(QtGui.QCursor.pos()).x())
        if note_index < len(parent.sound.notes):
            note_name, note_duration = parent.sound.notes[note_index]
            note_name = note_name.replace('b', '#')
            if note_name.find('#') == -1:
                note_name += '#'
            else:
                note_name = note_name.replace('#', '')
            parent.sound.notes[note_index] = (note_name, note_duration)

    def note_from_y(self, y):
        staf_height = 10
        G4_pos = 45
        pos = round((y - G4_pos) / staf_height*2)
        notes = {
            -9: 'B5', -8: 'A5', -7: 'G5', -6: 'F5', -5: 'E5', -4: 'D5',
            -3: 'C5', -2: 'B4', -1: 'A4', 0: 'G4', 1: 'F4', 2: 'E4',
            3: 'D4', 4: 'C4', 5: 'B3', 6: 'A3', 7: 'G3', 8: 'F3', 9: 'E3'
        }
        return notes.get(pos, 'G4')

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
            
            self.parent().sound.clear_notes()
            for note in notes:
                if note[1].find('.') > 0:
                    note[1] = float(note[1])
                else:
                    note[1] = int(note[1])
                self.parent().sound.add_note(tuple(note))
            self.parent().staff.update()

    def export_notes(self):
        export_dialog = QtWidgets.QInputDialog(self)
        export_dialog.setWindowTitle("Export Notes")
        export_dialog.setLabelText("Copy the notes to export")
        export_dialog.setTextValue(str(self.parent().sound.notes))
        export_dialog.setOkButtonText("Copy")
        export_dialog.setCancelButtonText("Close")

        if export_dialog.exec():
            notes_text = export_dialog.textValue()
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(notes_text)

    def play_notes(self):
        self.parent().sound.play()

    def clear_notes(self):
        self.parent().sound.clear_notes()

class Creator(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creator")
        self.setGeometry(100, 100, 600, 400)
        self.layout = QtWidgets.QVBoxLayout()
        self.sound = Sound(self)

        self.top = TopWidget(self)
        self.staff = ScrollStaff(self)
        self.layout.addWidget(self.top, alignment=Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.staff)
        

        # Set the layout for the widget
        self.setLayout(self.layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Space:
            self.staff.pause_mode = not self.staff.pause_mode
            self.staff.update()
        elif event.key() == Qt.Key.Key_Return:
            self.sound.play()
        elif event.key() == Qt.Key.Key_P:
            self.staff.pause_mode = not self.staff.pause_mode
            self.staff.update()
        elif event.key() == 46:  # '.' key
            self.staff.dot()
            self.staff.update()
        elif event.key() == Qt.Key.Key_B:
            self.staff.mol()
            self.staff.update()
        elif event.key() == Qt.Key.Key_D:
            self.staff.dur()
            self.staff.update()
        super().keyPressEvent(event)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    creator = Creator()
    creator.show()
    sys.exit(app.exec())