import quantities as pq
import neo
from PyQt4.Qt import QMessageBox

from spykeutils.plugin import analysis_plugin, gui_data
from spykeutils import plot

# Needed for activatable parameters
stop_prop = gui_data.ValueProp(False)
align_prop = gui_data.ValueProp(False)
optimize_prop = gui_data.ValueProp(False)


class SDEPlugin(analysis_plugin.AnalysisPlugin):
    # Configurable parameters
    kernel_size = gui_data.FloatItem('Kernel size', min=1.0, default=300.0,
        unit='ms')
    start_time = gui_data.FloatItem('Start time', default=0.0, unit='ms')

    stop_enabled = gui_data.BoolItem('Stop time enabled',
        default=False).set_prop('display', store=stop_prop)
    stop = gui_data.FloatItem('Time', default=10001.0,
        unit='ms').set_prop('display', active=stop_prop)

    align_enabled = gui_data.BoolItem('Alignment event enabled',
        default=False).set_prop('display', store=align_prop)
    align = gui_data.StringItem(
        'Event label').set_prop('display', active=align_prop)
    data_source = gui_data.ChoiceItem('Data source', ('Units', 'Selections'))

    _g = gui_data.BeginGroup('Kernel width optimization')
    optimize_enabled = gui_data.BoolItem('Enabled',
        default=False).set_prop('display', store=optimize_prop)
    minimum_kernel = gui_data.FloatItem('Minimum kernel size', default=10.0,
        unit='ms', min=0.5).set_prop('display', active=optimize_prop)
    maximum_kernel = gui_data.FloatItem('Maximum kernel size', default=1000.0,
        unit='ms', min=1.0).set_prop('display', active=optimize_prop)
    optimize_steps = gui_data.IntItem('Kernel size steps', default=30,
        min=2).set_prop('display', active=optimize_prop)
    _g_ = gui_data.EndGroup('Kernel size optimization')
    
    def __init__(self):
        super(SDEPlugin, self).__init__()
        self.unit = pq.ms

    def get_name(self):
        return 'Spike Density Estimation'

    def start(self, current, selections):
        current.progress.begin('Creating spike density estimation')

        # Prepare quantities
        start = float(self.start_time) * self.unit
        stop = None
        if self.stop_enabled:
            stop = float(self.stop) * self.unit
        kernel_size = float(self.kernel_size) * self.unit
        optimize_steps = 0
        if self.optimize_enabled:
            optimize_steps = self.optimize_steps
        minimum_kernel = self.minimum_kernel * self.unit
        maximum_kernel = self.maximum_kernel * self.unit

        # Load data
        events = None
        if self.data_source == 0:
            trains = current.spike_trains_by_unit()
            if self.align_enabled:
                events = current.labeled_events(self.align) 
        else:
            # Prepare dictionaries for psth():
            # One entry of spike trains for each selection,
            # an event for each segment occuring in any selection
            trains = {}
            if self.align_enabled:
                events = {}
            for s in selections:
                trains[neo.Unit(s.name)] = s.spike_trains()
                if self.align_enabled:
                    events.update(s.labeled_events(self.align))
                    
        if events:
            for s in events:  # Align on first event in each segment
                events[s] = events[s][0]

        plot.sde(
            trains, events, start, stop, kernel_size, optimize_steps,
            minimum_kernel, maximum_kernel, None, self.unit, current.progress)

    def configure(self):
        super(SDEPlugin, self).configure()
        while self.optimize_enabled and \
                self.maximum_kernel <= self.minimum_kernel:
            QMessageBox.warning(
                None, 'Unable to set parameters',
                'Maximum kernel size needs to be larger than '
                'minimum kernel size!')
            super(SDEPlugin, self).configure()