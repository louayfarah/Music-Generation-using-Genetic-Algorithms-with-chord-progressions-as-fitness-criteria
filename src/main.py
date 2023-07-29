#Louay Farah
#l.farah@innopolis.university

import music21
import random

###Input
# Get user input for the root note and mode of the scale
root_note = input("Enter the root note of the scale (e.g. C): ")
mode = input("Enter the mode of the scale (e.g. major): ")


###Creaating scale, chords, and pitches
# Create a Scale object with the user input
if mode == "major":
    scale = music21.scale.MajorScale(root_note)
else:
    scale = music21.scale.MinorScale(root_note)

# Get the pitches of the scale
scale_pitches = scale.getPitches()

# Create a list to store the chords of the scale
my_chords = []

# Loop through the scale pitches and add the corresponding chord to the list
for i in range(len(scale_pitches)):
    chord = music21.chord.Chord([scale_pitches[i], scale_pitches[(i + 2) % 7], scale_pitches[(i + 4) % 7]])
    my_chords.append(chord)

###Genetic Algorithm (GA)
# Parameters
population_size = 100
mutation_rate = 0.1
num_generations = 1000
melody_length = 200
chord_progression = [my_chords[0].pitchNames[0], my_chords[4].pitchNames[0], my_chords[5].pitchNames[0], my_chords[3].pitchNames[0]]
my_scale_tonic = my_chords[0].pitchNames[0]

# Get the pitches of my scale
my_scale_pitches = [music21.note.Note(pitch) for pitch in scale_pitches]

# Initialization
def initialization(population_size):
    population = []
    for i in range(population_size):
        melody = random_melody()
        population.append(melody)
    return population

# Generate a random melody
def random_melody():
    melody = []
    for i in range(melody_length):
        melody.append(random.choice(my_scale_pitches))
    return melody

# Evaluation using chord progression
def evaluate(melody, chord_progression):
    score = 0
    for note, chord in zip(melody, chord_progression):
        if note.pitch.name in music21.chord.Chord(chord).pitchNames:
            score += 1
    return score / len(chord_progression)

# Selection using roulette wheel
def roulette_wheel_selection(population):
    fitnesses = [evaluate(melody, chord_progression) for melody in population]
    total_fitness = sum(fitnesses)
    probabilities = [fitness / total_fitness for fitness in fitnesses]
    parents = random.choices(population, weights=probabilities, k=2)
    return parents

# Crossover
def crossover(parent1, parent2):
    crossover_point = random.randint(0, len(parent1))
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

# Mutation
def mutate(melody, mutation_rate):
    for i in range(melody_length):
        if random.random() < mutation_rate:
            melody[i] = random.choice(my_scale_pitches)
    return melody

# Replacement
def replacement(population, children):
    fitnesses = [evaluate(melody, chord_progression) for melody in population]
    min_fitness_index = fitnesses.index(min(fitnesses))
    population[min_fitness_index] = children[random.randint(0, 1)]
    return population

#A function that generates a chord given the pitches of a scale and the position (rank) of a note in the scale
def generate_chord(scale_pitches, rank):
    chord = music21.chord.Chord([scale_pitches[rank], scale_pitches[(rank+2) % 7], scale_pitches[(rank+4) % 7]])
    chord.duration.quarterLength = 4
    transposed_chord = chord.transpose(-12)
    return transposed_chord

# Termination
def main():
    population = initialization(population_size)
    for generation in range(num_generations):
        parents = roulette_wheel_selection(population)
        children = crossover(*parents)
        children = [mutate(child, mutation_rate) for child in children]
        population = replacement(population, children)
    return max(population, key=lambda melody: evaluate(melody, chord_progression))



if __name__ == "__main__":
    best_melody = main()
    ###Pitch durations patterns
    pitch_patterns = [
        [1, 1, 1, 1],
        [0.5, 1, 0.5, 0.5, 0.5, 1],
        [0.5, 0.5, 1, 1, 0.5, 0.5],
        [1, 1, 0.5, 0.5, 1]
        #We can add more in the future
    ]

    ###Create the melody
    melody = music21.stream.Part()
    current_measure = 1
    current_pitch = 0
    while(current_measure <= 19):
        pattern = random.choice(pitch_patterns)
        for dur in pattern:
            note_obj = music21.note.Note()
            note_obj.pitch = best_melody[current_pitch].pitch
            note_obj.duration.quarterLength = dur
            melody.append(note_obj)
            current_pitch += 1
        current_measure += 1
    final_note = music21.note.Note()
    final_note.pitch = music21.note.Note(my_scale_tonic).pitch
    final_note.duration.quarterLength = 2
    melody.append(final_note)
    current_measure += 1

    ###Create the accompainment chords
    accompany_chords = music21.stream.Part()
    for i in range(current_measure//2):
        if i%2 == 0:
            accompany_chords.append(generate_chord(scale_pitches, 0))
            accompany_chords.append(generate_chord(scale_pitches, 4))
        else:
            accompany_chords.append(generate_chord(scale_pitches, 5))
            accompany_chords.append(generate_chord(scale_pitches, 3))

    ###Create the score
    score = music21.stream.Score()
    score.append(melody)
    score.append(accompany_chords)

    tempo = music21.tempo.MetronomeMark(number=120)
    score.insert(0, tempo)

    ###Save the generated music as a MIDI file
    output_file = 'midi/output.mid'
    score.write('midi', fp=output_file)

    ###Confirm the successful generation of the output file
    print("MIDI file generated:", output_file)
