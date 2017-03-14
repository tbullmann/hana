% % Import
% neurons=events.neurons;
% NeuronTable = events.NeuronTable;
% clear events;

% define time
pre = 80;
post = 80;
sampling_frequency = 20000;
t = (-pre:post)/sampling_frequency;

filename_format = '/Users/tbullmann/Desktop/export/neuron%d.h5';
for neuron_index = 1:length(neurons)
    filename = sprintf(filename_format, neuron_index);
    x = neurons{neuron_index}.x;
    y = neurons{neuron_index}.y;
    V = neurons{neuron_index}.mean ;
    % The function below contains the bug
    trigger_el_idx = Neuron2Electrode ( NeuronTable, neuron_index);
     try
        V = interpolate_stack ( x, y, V );  % nan electrodes interpolieren
        V = bsxfun(@minus,V,median(V));  % subtract for each electrode
        hdf5write(filename, '/V',V, '/t',t, '/x',x, '/y',y ,...
            '/trigger',trigger_el_idx-1, '/neuron',neuron_index)
        fprintf('Saved %s \n', filename);
     catch
        fprintf('No neuron.\n')
     end
end

