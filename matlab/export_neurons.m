% Extract events (with thr=6) and calculate spike-triggered averages 
% by running 'hidens_extract.m' in the experiment matlab folder.
% This sript creates '*events.mat' files (and movies as well)

% Import the mat file with the 'events', e.g. 'hidens2023at35C_events.mat'

% Run this script, rename 'export' folder, e.g. 'hidens2023at35C'


neurons=events.neurons;
NeuronTable = events.NeuronTable;

% define time
pre = events.parameters.pre;
post = events.parameters.post;
sampling_frequency = events.parameters.samplingfrequency;
t = (-pre:post)/sampling_frequency;
fprintf('time %1.3f..%1.3f ms\n', 1000*min(t), 1000*max(t));

filename_format = '/home/tbullmann/Desktop/export/neuron%d.h5';
for neuron_index = 1:length(neurons)
    filename = sprintf(filename_format, neuron_index);
    x = neurons{neuron_index}.x;
    y = neurons{neuron_index}.y;
    V = neurons{neuron_index}.mean;
    n = neurons{neuron_index}.count;
% The function below contains the bug:
    trigger_el_idx = Neuron2Electrode ( NeuronTable, neuron_index);
    try
        V = interpolate_stack ( x, y, V );  % nan electrodes interpolieren
        V = bsxfun(@minus,V,median(V));  % subtract for each electrode
        hdf5write(filename, '/V',V, '/t',t, '/x',x, '/y',y ,...
            '/trigger',trigger_el_idx-1, '/neuron',neuron_index,...
            '/n', n)
        fprintf('Saved %s \n', filename);
    catch
        fprintf('No neuron.\n')
    end
end

filename = '/home/tbullmann/Desktop/export/events.h5';
for neuron_index = 1:length(neurons)
    index = events.neuron==neuron_index;
    try 
        hdf5write(filename, sprintf('/%d', neuron_index), events.frame(index)/sampling_frequency, 'WriteMode','append')
    catch
        hdf5write(filename, sprintf('/%d', neuron_index), events.frame(index)/sampling_frequency)
    end
    fprintf('Saved %d events for neuron %d\n', sum(index), neuron_index)
end

% clear all
