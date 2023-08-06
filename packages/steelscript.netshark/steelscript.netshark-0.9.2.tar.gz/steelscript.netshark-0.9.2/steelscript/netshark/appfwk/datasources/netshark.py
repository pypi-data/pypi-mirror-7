# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import time
import logging
import threading

from django import forms

from steelscript.netshark.core.types import Operation, Value, Key
from steelscript.netshark.core.filters import NetSharkFilter, TimeFilter
from steelscript.netshark.core._class_mapping import path_to_class
from steelscript.common.exceptions import RvbdHTTPException
from steelscript.common import timeutils
from steelscript.common.timeutils import (parse_timedelta,
                                          timedelta_total_seconds)
from steelscript.appfwk.apps.datasource.models import (DatasourceTable,
                                                       TableQueryBase)
from steelscript.appfwk.apps.devices.devicemanager import DeviceManager
from steelscript.appfwk.apps.devices.forms import fields_add_device_selection
from steelscript.appfwk.apps.datasource.models import Column, TableField
from steelscript.appfwk.apps.datasource.forms import (fields_add_time_selection,
                                               fields_add_resolution)
from steelscript.appfwk.libs.fields import Function


logger = logging.getLogger(__name__)
lock = threading.Lock()


def setup_capture_job(netshark, name, size=None):
    """ Reference function to initialize new capture job. """
    if size is None:
        size = '10%'

    try:
        job = netshark.get_capture_job_by_name(name)
    except ValueError:
        # create a capture job on the first available interface
        interface = netshark.get_interfaces()[0]
        job = netshark.create_job(interface, name, size,
                                  indexing_size_limit='2GB',
                                  start_immediately=True)
    return job


def netshark_source_name_choices(form, id, field_kwargs, params):
    """ Query netshark for available capture jobs / trace clips. """
    netshark_device = form.get_field_value('netshark_device', id)
    if netshark_device == '':
        label = 'Source'
        choices = [('', '<No netshark device>')]
    else:
        netshark = DeviceManager.get_device(netshark_device)
        #source_type = form.get_field_value('shark_source_type', id)
        source_type = 'job'

        choices = []
        if source_type == 'job':
            for job in netshark.get_capture_jobs():
                choices.append(('jobs/' + job.name, job.name))
            label = 'Capture Job'
        elif source_type == 'clip':
            # Not tested
            label = 'Trace Clip'
            for clip in netshark.get_clips():
                choices.append((clip, clip))
        else:
            raise KeyError('Unknown source type: %s' % source_type)

    field_kwargs['label'] = label
    field_kwargs['choices'] = choices


class NetSharkColumn(Column):
    class Meta:
        proxy = True

    COLUMN_OPTIONS = {'extractor': None,
                      'operation': None,
                      'default_value': None}


class NetSharkTable(DatasourceTable):
    class Meta:
        proxy = True

    _column_class = 'NetSharkColumn'
    _query_class = 'NetSharkQuery'

    TABLE_OPTIONS = {'aggregated': False}

    FIELD_OPTIONS = {'duration': '1m',
                     'durations': ('1m', '15m'),
                     'resolution': '1m',
                     'resolutions': ('1s', '1m'),
                     }

    def fields_add_filterexpr(self, keyword='netshark_filterexpr', initial=None):
        field = TableField(keyword=keyword,
                           label='NetShark Filter Expression',
                           help_text='Traffic expression using '
                                     'NetShark filter syntax',
                           initial=initial,
                           required=False)
        field.save()
        self.fields.add(field)

    def post_process_table(self, field_options):
        duration = field_options['duration']
        if isinstance(duration, int):
            duration = "%dm" % duration

        fields_add_device_selection(self, keyword='netshark_device',
                                    label='NetShark', module='netshark',
                                    enabled=True)

        TableField.create(keyword='netshark_source_name', label='Source',
                          obj=self,
                          field_cls=forms.ChoiceField,
                          parent_keywords=['netshark_device'],
                          dynamic=True,
                          pre_process_func=Function(netshark_source_name_choices))

        fields_add_time_selection(self,
                                  initial_duration=duration,
                                  durations=field_options['durations'])
        fields_add_resolution(self,
                              initial=field_options['resolution'],
                              resolutions=field_options['resolutions'])
        self.fields_add_filterexpr()


class NetSharkQuery(TableQueryBase):

    def fake_run(self):
        import fake_data
        self.data = fake_data.make_data(self.table, self.job)

    def run(self):
        """ Main execution method
        """
        criteria = self.job.criteria

        self.timeseries = False         # if key column called 'time' is created
        self.column_names = []

        # Resolution comes in as a time_delta
        resolution = timedelta_total_seconds(criteria.resolution)

        default_delta = 1000000000                      # one second
        self.delta = int(default_delta * resolution)    # sample size interval


        if criteria.netshark_device == '':
            logger.debug('%s: No netshark device selected' % self.table)
            self.job.mark_error("No NetShark Device Selected")
            return False

        #self.fake_run()
        #return True

        shark = DeviceManager.get_device(criteria.netshark_device)

        logger.debug("Creating columns for NetShark table %d" % self.table.id)

        # Create Key/Value Columns
        columns = []
        for tc in self.table.get_columns(synthetic=False):
            tc_options = tc.options
            if ( tc.iskey and tc.name == 'time' and
                 tc_options.extractor == 'sample_time'):
                # don't create column, use the sample time for timeseries
                self.timeseries = True
                self.column_names.append('time')
                continue
            elif tc.iskey:
                c = Key(tc_options.extractor,
                        description=tc.label,
                        default_value=tc_options.default_value)
            else:
                if tc_options.operation:
                    try:
                        operation = getattr(Operation, tc_options.operation)
                    except AttributeError:
                        operation = Operation.sum
                        print ('ERROR: Unknown operation attribute '
                               '%s for column %s.' %
                               (tc_options.operation, tc.name))
                else:
                    operation = Operation.none

                c = Value(tc_options.extractor,
                          operation,
                          description=tc.label,
                          default_value=tc_options.default_value)
                self.column_names.append(tc.name)

            columns.append(c)

        # Identify Sort Column
        sortidx = None
        if self.table.sortcols is not None:
            sortcol = Column.objects.get(table=self.table,
                                         name=self.table.sortcols[0])
            sort_name = sortcol.options.extractor
            for i, c in enumerate(columns):
                if c.field == sort_name:
                    sortidx = i
                    break

        # Initialize filters
        criteria = self.job.criteria

        filters = []
        filterexpr = self.job.combine_filterexprs(
            exprs=criteria.netshark_filterexpr,
            joinstr="&"
        )
        if filterexpr:
            filters.append(NetSharkFilter(filterexpr))

        tf = TimeFilter(start=criteria.starttime, end=criteria.endtime)
        filters.append(tf)

        logger.info("Setting netshark table %d timeframe to %s" % (self.table.id,
                                                                str(tf)))

        # Get source type from options
        try:
            with lock:
                source = path_to_class(shark,
                                       self.job.criteria.netshark_source_name)

        except RvbdHTTPException, e:
            source = None
            raise e

        resolution = criteria.resolution
        if resolution.seconds == 1:
            sampling_time_msec = 1000
        elif resolution.microseconds == 1000:
            sampling_time_msec = 1
            if criteria.duration > parse_timedelta('1s'):
                msg = ("Cannot run a millisecond report with a duration "
                       "longer than 1 second")
                raise ValueError(msg)
        else:
            sampling_time_msec = 1000

        # Setup the view
        if source is not None:
            with lock:
                view = shark.create_view(source, columns, filters=filters,
                                         sync=False,
                                         sampling_time_msec=sampling_time_msec)
        else:
            # XXX raise other exception
            return None

        done = False
        logger.debug("Waiting for netshark table %d to complete" % self.table.id)
        while not done:
            time.sleep(0.5)
            with lock:
                s = view.get_progress()
                self.job.progress = s
                self.job.save()
            done = (s == 100)

        # Retrieve the data
        with lock:
            if self.table.options.aggregated:
                self.data = view.get_data(
                    aggregated=self.table.options.aggregated,
                    sortby=sortidx
                )
            else:
                self.data = view.get_data(delta=self.delta, sortby=sortidx)
            view.close()

        if self.table.rows > 0:
            self.data = self.data[:self.table.rows]

        self.parse_data()

        logger.info("NetShark Report %s returned %s rows" %
                    (self.job, len(self.data)))

        return True

    def parse_data(self):
        """ Reformat netshark data results to be uniform tabular format
        """
        out = []
        if self.timeseries:
            # use sample times for each row
            for d in self.data:
                if d['t'] is not None:
                    t = timeutils.datetime_to_microseconds(d['t']) / float(10 ** 6)
                    out.extend([t] + x for x in d['vals'])

        else:
            for d in self.data:
                out.extend(x for x in d['vals'])

        self.data = out
