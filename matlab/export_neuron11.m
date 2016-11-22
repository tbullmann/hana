%TODO: Fix the BIG BUG in the matlab export script / Neuron2Electrode: Indicies for electrodes in events
%correctly start at 0, in delays and positive peak the (trigger) electrodes from 1 (!)

% Import
neurons=events.neurons;
NeuronTable = events.NeuronTable;
clear events;


neuron_index = 11;
x = neurons{neuron_index}.x;
y = neurons{neuron_index}.y;
distances = distn([x' y']',[x' y']');
V = neurons{neuron_index}.mean ;trigger_el_idx = Neuron2Electrode ( NeuronTable, neuron_index);
V = interpolate_stack ( x, y, V );   % nan electrodes interpolieren
V = bsxfun(@minus,V,median(V));      % subtract median for each electrode


pre = 80;
post = 80;
sampling_frequency = 20000;
time = (-pre:post)/sampling_frequency;


filename = '/Users/tbullmann/Desktop/neuron11.h5';
hdf5write(filename, '/V',V, '/time',time/1000, '/x',x, '/y',y , '/trigger',trigger_el_idx-1, '/neuron',neuron_index)
