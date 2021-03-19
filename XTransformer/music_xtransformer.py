# -*- coding: utf-8 -*-
"""Music_XTransformer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HNRP8k6YdboMRvqqFfaENdm5I_3GBTld

# Music XTransformer (PyTorch/GPU) (Ver 1.0)

***

Credit for the PyTorch Reformer implementation goes out to @lucidrains of GitHub: 

https://github.com/lucidrains/x-transformers

***

This is a work in progress so please check back for updates.

***

Project Los Angeles

Tegridy Code 2021

***

# Setup the environment
"""

#@title Install dependencies
!git clone https://github.com/asigalov61/tegridy-tools
!pip install x-transformers
!pip install numpy

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

import numpy as np

os.chdir('/content/tegridy-tools/tegridy-tools')
import TMIDI
os.chdir('/content/')

from x_transformers import TransformerWrapper, Decoder
from x_transformers.autoregressive_wrapper import AutoregressiveWrapper

import random
import tqdm
import gzip
import torch
import torch.optim as optim
from torch.nn import functional as F
from torch.utils.data import DataLoader, Dataset

"""# Prep the MIDIs and TXT/INT datasets"""

# Commented out IPython magic to ensure Python compatibility.
#@title Download special Tegridy Piano MIDI dataset

#@markdown Works best stand-alone/as-is for the optimal results
# %cd /content/Dataset/

!wget 'https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Tegridy-Piano-CC-BY-NC-SA.zip'
!unzip -j '/content/Dataset/Tegridy-Piano-CC-BY-NC-SA.zip'
!rm '/content/Dataset/Tegridy-Piano-CC-BY-NC-SA.zip'

# %cd /content/

# Commented out IPython magic to ensure Python compatibility.
#@title Download special Synthetic Tegridy Piano MIDI dataset

#@markdown Works best stand-alone/as-is for the optimal results
# %cd /content/Dataset/

!wget 'https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/Synthetic-Tegridy-Piano-MIDI-Dataset-CC-BY-NC-SA.zip'
!unzip '/content/Dataset/Synthetic-Tegridy-Piano-MIDI-Dataset-CC-BY-NC-SA.zip'
!rm '/content/Dataset/Synthetic-Tegridy-Piano-MIDI-Dataset-CC-BY-NC-SA.zip'

# %cd /content/

#@title Process MIDIs to special MIDI dataset with Tegridy MIDI Processor
#@markdown NOTES:

#@markdown 1) Dataset MIDI file names are used as song names. Feel free to change it to anything you like.

#@markdown 2) Best results are achieved with the single-track, single-channel, single-instrument MIDI 0 files with plain English names (avoid special or sys/foreign chars)

#@markdown 3) MIDI Channel = -1 means all MIDI channels except drums. MIDI Channel = 16 means all channels will be processed. Otherwise, only single indicated MIDI channel will be processed.

file_name_to_output_dataset_to = "/content/Music-XTransformer_TXT_Dataset" #@param {type:"string"}
desired_MIDI_channel_to_process = 16 #@param {type:"slider", min:-1, max:16, step:1}
encode_velocities = True #@param {type:"boolean"}
encode_MIDI_channels = False #@param {type:"boolean"}
add_transposed_dataset_by_this_many_pitches = 0 #@param {type:"slider", min:-12, max:12, step:1}
chordify_input_MIDIs = False #@param {type:"boolean"}
time_denominator = 10 #@param {type:"slider", min:1, max:20, step:1}
chars_encoding_offset = 33 #@param {type:"number"}


print('Starting up...')
###########

average_note_pitch = 0
min_note = 127
max_note = 0

files_count = 0

ev = 0

chords_list_f = []
melody_list_f = []

chords_list = []
chords_count = 0

melody_chords = []
melody_count = 0

TXT_String = 'DATASET=Music-XTransformer-Dataset' + chr(10)

TXT = ''
melody = []
chords = []

###########

print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset/"
os.chdir(dataset_addr)
filez = os.listdir(dataset_addr)

print('Processing MIDI files. Please wait...')
for f in tqdm.auto.tqdm(filez):
  try:
    fn = os.path.basename(f)
    fn1 = fn.split('.')[0]
    #notes = song_notes_list[song_notes_list.index(fn1)+1]


    files_count += 1
    TXT, melody, chords = TMIDI.Optimus_MIDI_TXT_Processor(f, chordify_TXT=chordify_input_MIDIs, output_MIDI_channels=encode_MIDI_channels, char_offset=chars_encoding_offset, dataset_MIDI_events_time_denominator=time_denominator, output_velocity=encode_velocities, MIDI_channel=desired_MIDI_channel_to_process, MIDI_patch=range(0, 127))
    TXT_String += TXT
    melody_list_f += melody
    chords_list_f += chords

    if add_transposed_dataset_by_this_many_pitches != 0:

      TXT, melody, chords = TMIDI.Optimus_MIDI_TXT_Processor(f, chordify_TXT=chordify_input_MIDIs, output_MIDI_channels=encode_MIDI_channels, char_offset=chars_encoding_offset, dataset_MIDI_events_time_denominator=time_denominator, output_velocity=encode_velocities, MIDI_channel=desired_MIDI_channel_to_process, transpose_by=add_transposed_dataset_by_this_many_pitches, MIDI_patch=range(0, 127))
      TXT_String += TXT
      melody_list_f += melody
      chords_list_f += chords   
    #TXT_String += 'INTRO=' + notes + '\n'
    
  
  except:
    print('Bad MIDI:', f)
    continue

print('Task complete :)')
print('==================================================')
print('Number of processed dataset MIDI files:', files_count)
print('Number of MIDI chords recorded:', len(chords_list_f))
print('First chord event:', chords_list_f[0], 'Last chord event:', chords_list_f[-1]) 
print('Number of recorded melody events:', len(melody_list_f))
print('First melody event:', melody_list_f[0], 'Last Melody event:', melody_list_f[-1])
print('Total number of MIDI events recorded:', len(chords_list_f) + len(melody_list_f))

# Writing dataset to TXT file
with open(file_name_to_output_dataset_to + '.txt', 'wb') as f:
  f.write(TXT_String.encode('utf-8', 'replace'))
  f.close

# Dataset
MusicDataset = [chords_list_f, melody_list_f]

# Writing dataset to pickle file
TMIDI.Tegridy_Pickle_File_Writer(MusicDataset, file_name_to_output_dataset_to)

#@title Process the TXT MIDI dataset to TXT INT dataset
full_path_to_TXT_dataset = "/content/Music-XTransformer_TXT_Dataset.txt" #@param {type:"string"}

print('Processing...')
with open(full_path_to_TXT_dataset) as file:
  z = file.read()
  file.close()
  Y = list(z)

string = '\n'.join([str(ord(item)) for item in Y if ord(item) < 256])

with open('/content/Music-XTransformer_INT_Dataset.txt', 'w') as file:
  file.write(string)

print('Done!')

#@title Load INT dataset into memory and setup the dataset
full_path_to_INT_dataset = "/content/Music-XTransformer_INT_Dataset.txt" #@param {type:"string"}
dataset_split_ratio = 0.9 #@param {type:"slider", min:0.1, max:0.9, step:0.1}

print('Processing...')
with open(full_path_to_INT_dataset) as file:
    X = file.read()
    H = []
    for x in X.split('\n'):
      H.append(int(x))

trX, vaX = np.split(H, [int(len(H) * dataset_split_ratio)])
data_train, data_val = torch.from_numpy(trX), torch.from_numpy(vaX)
print('Done!')

"""# Setup and Train"""

#@title Setup and intialize the model
# constants

NUM_BATCHES = int(1e5)
BATCH_SIZE = 6
GRADIENT_ACCUMULATE_EVERY = 4
LEARNING_RATE = 1e-4
VALIDATE_EVERY  = 100
GENERATE_EVERY  = 500
GENERATE_LENGTH = 2048
SEQ_LEN = 2048

# helpers

def cycle(loader):
    while True:
        for data in loader:
            yield data

def decode_token(token):
    return str(chr(max(32, token)))

def decode_tokens(tokens):
    return ''.join(list(map(decode_token, tokens)))

# instantiate GPT-like decoder model

model = TransformerWrapper(
    num_tokens = 256,
    max_seq_len = SEQ_LEN,
    attn_layers = Decoder(dim = 512, depth = 6, heads = 8)
)

model = AutoregressiveWrapper(model)
model.cuda()

'''========================================='''

class TextSamplerDataset(Dataset):
    def __init__(self, data, seq_len):
        super().__init__()
        self.data = data
        self.seq_len = seq_len

    def __getitem__(self, index):
        rand_start = torch.randint(0, self.data.size(0) - self.seq_len - 1, (1,))
        full_seq = self.data[rand_start: rand_start + self.seq_len + 1].long()
        return full_seq.cuda()

    def __len__(self):
        return self.data.size(0) // self.seq_len

train_dataset = TextSamplerDataset(data_train, SEQ_LEN)
val_dataset   = TextSamplerDataset(data_val, SEQ_LEN)
train_loader  = cycle(DataLoader(train_dataset, batch_size = BATCH_SIZE))
val_loader    = cycle(DataLoader(val_dataset, batch_size = BATCH_SIZE))

# optimizer

optim = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

#@title Train the model
# training

for i in tqdm.tqdm(range(NUM_BATCHES), mininterval=10., desc='training'):
    model.train()

    for __ in range(GRADIENT_ACCUMULATE_EVERY):
        loss = model(next(train_loader))
        loss.backward()

    print(f'training loss: {loss.item()}')
    torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
    optim.step()
    optim.zero_grad()

    if i % VALIDATE_EVERY == 0:
        model.eval()
        with torch.no_grad():
            loss = model(next(val_loader))
            print(f'validation loss: {loss.item()}')

    if i % GENERATE_EVERY == 0:
        model.eval()
        inp = random.choice(val_dataset)[:-1]
        prime = decode_tokens(inp)
        print(f'%s \n\n %s', (prime, '*' * 100))

        sample = model.generate(inp, GENERATE_LENGTH)
        output_str = decode_tokens(sample)
        print(output_str)

"""# Save and Load/Reload the model"""

#@title Save the model
torch.save(model.state_dict(), '/content/Music-XTransformer-Model.pth')

checkpoint = {'state_dict': model.state_dict(),'optimizer' :optim.state_dict()}
torch.save(checkpoint, '/content/Music-XTransformer-Model_sd_opt.pth')

#@title Load/Reload the model
model = torch.load('/content/Music-XTransformer-Model.pth')
model.eval()

"""# Generate from the model"""

#@title Generate Music
number_of_tokens_to_generate = 3976 #@param {type:"slider", min:8, max:4096, step:128}
model_temperature = 0.8 #@param {type:"slider", min:0.1, max:2, step:0.1}

inp = random.choice(val_dataset)[:-1]
prime = decode_tokens(inp)
print(f'%s \n\n %s', (prime, '*' * 100))
 
sample = model.generate(start_tokens=inp[:16], seq_len=number_of_tokens_to_generate, temperature=model_temperature) #GENERATE_LENGTH)
output_str = decode_tokens(sample)
print(output_str)

#@title Convert generated output to MIDI
time_denominator = 10 #@param {type:"slider", min:1, max:20, step:1}
encoding_has_velocities = True #@param {type:"boolean"}
simulate_velocity = False #@param {type:"boolean"}
char_encoding_offset = 33 #@param {type:"number"}

SONG = TMIDI.Tegridy_Optimus_TXT_to_Notes_Converter('SONG=SONG ' + output_str, line_by_line_dataset = False, has_MIDI_channels=False, has_velocities=encoding_has_velocities, dataset_MIDI_events_time_denominator=time_denominator, char_encoding_offset=char_encoding_offset, simulate_velocity=simulate_velocity)
stats = TMIDI.Tegridy_SONG_to_MIDI_Converter(SONG[0], output_file_name='/content/Music-XTransformer_MIDI', output_signature='Music XTransformer')
print(stats)

"""# Congrats! You did it :)"""