function hidens_extrac (hidens_ids, temperature, threshold)

% load ntk and save events

for hidens_id = hidens_ids

    flistfilename = sprintf('flist_hidens%dat%dC',hidens_id,temperature);

    filename = sprintf('hidens%dat%dC_thr%d',hidens_id,temperature,threshold);    
    matfilename = ['computed_results/mat/',filename,'.mat'];
    figfilename = ['computed_results/figures/configuration_',filename,'.eps'];
    
    eval (flistfilename);
    
    rec_el_idx = get_recording_configurations(flist);
    figure ('Position',[1,1,1200,1200]); 
    plot_multiple_configurations(rec_el_idx,'findfixedclusters','hidensid',hidens_id);
    format_figure;
    export_fig (figfilename);
    
    fixed_electrodes = cell_array_intersect(rec_el_idx);
    events = init_events (flist, fixed_electrodes);
    events.parameters.threshold_factor = threshold;

    events = load_events(events);

    save (matfilename,'events','-v7.3');
    
end

% load events and export movies
    
for hidens_id = hidens_ids

    filename = sprintf('hidens%dat%dC_thr%d',hidens_id,temperature,threshold);    
    matfilename = ['computed_results/mat/',filename,'.mat'];
    movfilename = ['computed_results/movies/',filename,'_'];
    
    load (matfilename,'events');
    
    events

    plot_neuron (events,movfilename);   
    
end

end





