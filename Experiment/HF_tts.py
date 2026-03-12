import torch
import soundfile as sf
import ssl

# Temporarily bypass SSL verification for torch hub downloads
ssl._create_default_https_context = ssl._create_unverified_context

# SETTINGS
language = 'en'
model_id = 'v3_en'
sample_rate = 48000
speaker = 'en_0'

device = torch.device('cpu')

# Load model from PyTorch Hub
model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language=language,
    speaker=model_id
)

model.to(device)

# Generate speech
audio = model.apply_tts(
    text="Hi jayandhan , you are a multimillionaire pro lionlike , the most successful person in the world with all the power and success in the world",
    speaker=speaker,
    sample_rate=sample_rate
)

# Save audio
sf.write("output.wav", audio, sample_rate)

print("Audio saved as output.wav")