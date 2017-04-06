#!/usr/bin/env bash
cd data

mkdir culture1
cd culture1
# Must download each file separately, otherwise wget fails to automatically download the file.
# For files over 25MByte google drive refers to a html warning message 'File to large for virus scan, please confirm'
# that breaks the download.

# Link: https://drive.google.com/open?id=0B-u65ZxPB5iQaVFHYk9iblNuQW8
wget -O events.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQaVFHYk9iblNuQW8'

# Link: https://drive.google.com/open?id=0B-u65ZxPB5iQZW03Rl8wRWplS2s
wget -O metadata.yaml 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQZW03Rl8wRWplS2s'

# Link: https://drive.google.com/open?id=0B-u65ZxPB5iQaFI4ZjlsWmJRaDQ
wget -O neuron10.h5 'https://drive.google.com/uc?export=download&id=id=0B-u65ZxPB5iQaFI4ZjlsWmJRaDQ'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQVi1mN0MwUEhQRG8
wget -O neuron11.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQVi1mN0MwUEhQRG8'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQdVI2V0h6QlJBakU
wget -O neuron13.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQdVI2V0h6QlJBakU'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQdk42QUsyTmp4TUE
wget -O neuron2.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQdk42QUsyTmp4TUE'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQY0ctOHJjT0VBWTA
wget -O neuron20.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQY0ctOHJjT0VBWTA'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQOXRhQ2hjSlFtM0k
wget -O neuron21.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQOXRhQ2hjSlFtM0k'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQaE43TGk2VHhSYWs
wget -O neuron22.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQaE43TGk2VHhSYWs'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQMXA2eUVKZlRBODg
wget -O neuron23.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQMXA2eUVKZlRBODg'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQTExBWEthdmZDcHc
wget -O neuron25.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQTExBWEthdmZDcHc'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQVFp6T2ZjX1lOckk
wget -O neuron27.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQVFp6T2ZjX1lOckk'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQLUpzbW9lbWN2ZlU
wget -O neuron29.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQLUpzbW9lbWN2ZlU'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQaVU3Yzc4Q09NVzQ
wget -O neuron3.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQaVU3Yzc4Q09NVzQ'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQT3Y4VHc5X3Q3aTA
wget -O neuron31.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQT3Y4VHc5X3Q3aTA'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQTzJBRHY1bG1VNjg
wget -O neuron35.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQTzJBRHY1bG1VNjg'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQTTdIbC1Md3QyaVk
wget -O neuron36.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQTTdIbC1Md3QyaVk'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQV3hMM0FxZXhybU0
wget -O neuron37.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQV3hMM0FxZXhybU0'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQdGlUeVhQSEVKVFE
wget -O neuron4.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQdGlUeVhQSEVKVFE'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQYVRBcDV3UUZfNms
wget -O neuron41.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQYVRBcDV3UUZfNms'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQWjNLRDdCOUJBYUk
wget -O neuron49.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQWjNLRDdCOUJBYUk'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQTTdHU1ZNQWw0REk
wget -O neuron5.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQTTdHU1ZNQWw0REk'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQb3dqSzdqTllUZlE
wget -O neuron50.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQb3dqSzdqTllUZlE'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQQXUtSUhEQmQtcTg
wget -O neuron51.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQQXUtSUhEQmQtcTg'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQSVo4alBMcTlDTms
wget -O neuron57.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQSVo4alBMcTlDTms'

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQUjVVSDZfcnpkeTg
wget -O neuron59.h5 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQUjVVSDZfcnpkeTg'

cd ..

# Download ground truth data as zip (rather small neuron, only 6MByte)

# Link https://drive.google.com/open?id=0B-u65ZxPB5iQZi1OV3U3REcxdFU
wget -O culture8.zip 'https://drive.google.com/uc?export=download&id=0B-u65ZxPB5iQZi1OV3U3REcxdFU'
unzip -n culture8.zip
rm culture8.zip




















