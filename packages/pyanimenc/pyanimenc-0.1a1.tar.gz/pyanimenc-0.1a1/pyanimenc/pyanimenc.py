#!/usr/bin/env python3

import os
import re
import subprocess
import yaml
from concurrent.futures import ThreadPoolExecutor
from gi.repository import GLib, GObject, Gtk
from pyanimenc.helpers import Encode, MatroskaOps
from pkg_resources import resource_string
from threading import Lock

# Constants
vencs = ['x264', 'x264-10bit', 'x265', 'x265-10bit']
vconts = ['avi', 'mkv', 'mp4', 'ogm']
vtypes = {'V_MPEG4/ISO/AVC': 'h264'}
aencs = ['fdkaac', 'lame']
aconts= ['aac', 'ac3', 'dts', 'flac', 'mka', 'mp3', 'mp4', 'thd', 'ogg',
         'wv']
atypes = {'A_AAC': 'aac', 'A_AC3': 'ac3', 'A_DTS': 'dts', 'A_FLAC': 'flac',
          'A_MP3': 'mp3', 'A_TRUEHD': 'thd', 'A_VORBIS': 'ogg',
          'A_WAVPACK4': 'wv'}
stypes = {'S_HDMV/PGS': 'sup', 'S_TEXT/ASS': 'ass', 'S_TEXT/SSA': 'ass',
          'S_TEXT/UTF8': 'srt', 'S_VOBSUB': 'sub'}

# Main UI

builder = Gtk.Builder()
pyanimenc_glade = resource_string(__name__, 'glade/pyanimenc.glade')
pyanimenc_glade = pyanimenc_glade.decode('utf8')
builder.add_from_string(pyanimenc_glade)

window = builder.get_object('window')
vsrc_fcbutton = builder.get_object('vsrc-fcbutton')
vqueue_button = builder.get_object('vqueue-button')
venc_cbtext = builder.get_object('venc-cbtext')
vconf_button = builder.get_object('vconf-button')
asrc_fcbutton = builder.get_object('asrc-fcbutton')
aqueue_button = builder.get_object('aqueue-button')
aenc_cbtext = builder.get_object('aenc-cbtext')
aconf_button = builder.get_object('aconf-button')

batch_src_fcbutton = builder.get_object('batch_src-fcbutton')
batch_venc_cbtext = builder.get_object('batch_venc-cbtext')
batch_vconf_button = builder.get_object('batch_vconf-button')
batch_aenc_cbtext = builder.get_object('batch_aenc-cbtext')
batch_aconf_button = builder.get_object('batch_aconf-button')
batch_queue_button = builder.get_object('batch_queue-button')
batch_tracks_vbox = builder.get_object('batch_tracks-vbox')
track_mismatch_dialog = builder.get_object('track_mismatch-dialog')

queue_treeview = builder.get_object('queue-treeview')
queue_selection = builder.get_object('queue-selection')
status_pbar = builder.get_object('status-pbar')

# Available encoders
x264_found = False
x264_depth = []
x265_found = False
x265_depth = []

for enc in vencs:
    if os.path.isfile('/usr/bin/' + enc):
        if enc == 'x264':
            x264_depth.append('8')
            x264_found = True
        elif enc == 'x264-10bit':
            x264_depth.append('10')
            x264_found = True
        elif enc == 'x265':
            x265_depth.append('8')
            x265_found = True
        elif enc == 'x265-10bit':
            x265_depth.append('10')
            x265_found = True
        else:
            venc_cbtext.append_text(enc)
            batch_venc_cbtext.append_text(enc)
        print('Found ' + enc + '.')
    else:
        vencs.pop(vencs.index(enc))

if x264_found:
    venc_cbtext.append_text('x264')
    batch_venc_cbtext.append_text('x264')
if x265_found:
    venc_cbtext.append_text('x265')
    batch_venc_cbtext.append_text('x265')

for enc in aencs:
    if os.path.isfile('/usr/bin/' + enc):
        aenc_cbtext.append_text(enc)
        batch_aenc_cbtext.append_text(enc)
        print('Found ' + enc + '.')
    else:
        aencs.pop(aencs.index(enc))

if vencs:
    venc_cbtext.set_active(0)
    vconf_button.set_sensitive(True)
    batch_venc_cbtext.set_active(0)
    batch_vconf_button.set_sensitive(True)
if aencs:
    aenc_cbtext.set_active(0)
    aconf_button.set_sensitive(True)
    batch_aenc_cbtext.set_active(0)
    batch_aconf_button.set_sensitive(True)

# Encoders UI
encoders_glade = resource_string(__name__, 'glade/encoders.glade')
encoders_glade = encoders_glade.decode('utf8')
builder.add_from_string(encoders_glade)

if x264_found:
    x264_dialog = builder.get_object('x264-dialog')
    x264_depth_cbtext = builder.get_object('x264_depth-cbtext')
    for dp in x264_depth:
        x264_depth_cbtext.append_text(dp)
    x264_depth_cbtext.set_active(0)
    x264_quality_spin = builder.get_object('x264_quality-spin')
    x264_preset_cbtext = builder.get_object('x264_preset-cbtext')
    x264_tune_cbtext = builder.get_object('x264_tune-cbtext')
    x264_container_cbtext = builder.get_object('x264_container-cbtext')

if x265_found:
    x265_dialog = builder.get_object('x265-dialog')
    x265_depth_cbtext = builder.get_object('x265_depth-cbtext')
    for dp in x265_depth:
        x265_depth_cbtext.append_text(dp)
    x265_depth_cbtext.set_active(0)
    x265_quality_spin = builder.get_object('x265_quality-spin')
    x265_preset_cbtext = builder.get_object('x265_preset-cbtext')
    x265_tune_cbtext = builder.get_object('x265_tune-cbtext')
    x265_container_cbtext = builder.get_object('x265_container-cbtext')

for enc in aencs:
    if enc == 'fdkaac':
        fdkaac_dialog = builder.get_object('fdkaac-dialog')
        fdkaac_mode_cbtext = builder.get_object('fdkaac_mode-cbtext')
        fdkaac_bitrate_spin = builder.get_object('fdkaac_bitrate-spin')
        fdkaac_quality_spin = builder.get_object('fdkaac_quality-spin')
        fdkaac_container_cbtext = builder.get_object('fdkaac_container-cbtext')
    elif enc == 'lame':
        lame_dialog = builder.get_object('lame-dialog')
        lame_mode_cbtext = builder.get_object('lame_mode-cbtext')
        lame_bitrate_spin = builder.get_object('lame_bitrate-spin')
        lame_quality_spin = builder.get_object('lame_quality-spin')

# VapourSynth UI
filters_glade = resource_string(__name__, 'glade/filters.glade')
filters_glade = filters_glade.decode('utf8')
builder.add_from_string(filters_glade)

vpy_dialog = builder.get_object('vpy-dialog')
fps_check = builder.get_object('fps-check')
fpsnum_spin = builder.get_object('fpsnum-spin')
fpsden_spin = builder.get_object('fpsden-spin')
crop_check = builder.get_object('crop-check')
lcrop_spin = builder.get_object('lcrop-spin')
rcrop_spin = builder.get_object('rcrop-spin')
tcrop_spin = builder.get_object('tcrop-spin')
bcrop_spin = builder.get_object('bcrop-spin')
resize_check = builder.get_object('resize-check')
wresize_spin = builder.get_object('wresize-spin')
hresize_spin = builder.get_object('hresize-spin')
resize_algo_cbtext = builder.get_object('resize_algo-cbtext')

sdenoise_check = builder.get_object('sdenoise-check')
sdenoise_cbtext = builder.get_object('sdenoise-cbtext')
sdenoise_conf_button = builder.get_object('sdenoise_conf-button')
rgvs_dialog = builder.get_object('rgvs-dialog')
rgvs_mode_spin = builder.get_object('rgvs_mode-spin')
rgvs_adv_check = builder.get_object('rgvs_adv-check')
rgvs_umode_spin = builder.get_object('rgvs_umode-spin')
rgvs_vmode_spin = builder.get_object('rgvs_vmode-spin')
rgvs_ok_button = builder.get_object('rgvs_ok-button')

tdenoise_check = builder.get_object('tdenoise-check')
tdenoise_cbtext = builder.get_object('tdenoise-cbtext')
tdenoise_conf_button = builder.get_object('tdenoise_conf-button')
tsoft_dialog = builder.get_object('tsoft-dialog')
tsoft_rad_spin = builder.get_object('tsoft_rad-spin')
tsoft_lt_spin = builder.get_object('tsoft_lt-spin')
tsoft_ct_spin = builder.get_object('tsoft_ct-spin')
tsoft_sc_spin = builder.get_object('tsoft_sc-spin')
tsoft_ok_button = builder.get_object('tsoft_ok-button')

stdenoise_check = builder.get_object('stdenoise-check')
stdenoise_cbtext = builder.get_object('stdenoise-cbtext')
stdenoise_conf_button = builder.get_object('stdenoise_conf-button')
fsmooth_dialog = builder.get_object('fsmooth-dialog')
fsmooth_tt_spin = builder.get_object('fsmooth_tt-spin')
fsmooth_st_spin = builder.get_object('fsmooth_st-spin')
fsmooth_yplane_check = builder.get_object('fsmooth_yplane-check')
fsmooth_uplane_check = builder.get_object('fsmooth_uplane-check')
fsmooth_vplane_check = builder.get_object('fsmooth_vplane-check')
fsmooth_ok_button = builder.get_object('fsmooth_ok-button')

deband_check = builder.get_object('deband-check')
deband_cbtext = builder.get_object('deband-cbtext')
deband_conf_button = builder.get_object('deband_conf-button')
f3kdb_dialog = builder.get_object('f3kdb-dialog')
f3kdb_preset_cbtext = builder.get_object('f3kdb_preset-cbtext')
f3kdb_planes_cbtext = builder.get_object('f3kdb_planes-cbtext')
f3kdb_grain_check = builder.get_object('f3kdb_grain-check')
f3kdb_depth_spin = builder.get_object('f3kdb_depth-spin')
f3kdb_ok_button = builder.get_object('f3kdb_ok-button')

class Handler:
    def __init__(self):
        self.queue = Gtk.TreeStore(GObject.TYPE_PYOBJECT, str, str, str)
        queue_treeview.set_model(self.queue)
        self.idle = True
        self.lock = Lock()
        self.lock.acquire()
        self.worker = ThreadPoolExecutor(max_workers=1)
        self.tools_worker = ThreadPoolExecutor(max_workers=2)

    def _wait(self):
        if self.idle:
            self.lock.acquire()
        else:
            self.lock.release()

    def _update_treeview(self):
        njobs = len(self.queue)
        for i in range(njobs):
            path = Gtk.TreePath(i)
            job = self.queue.get_iter(path)
            future = self.queue.get_value(job, 0)
            status = self.queue.get_value(job, 3)
            if self.queue.iter_has_child(job):
                nsteps = self.queue.iter_n_children(job)
                for j in range(nsteps):
                    path = Gtk.TreePath([i, j])
                    step = self.queue.get_iter(path)
                    future = self.queue.get_value(step, 0)
                    status = self.queue.get_value(step, 3)
                    # Mark done children as such
                    if future.done() and status != 'Failed':
                        GLib.idle_add(self.queue.set_value, step, 3, 'Done')
                        # Mark parent as done if all children are
                        if j == nsteps - 1:
                            GLib.idle_add(self.queue.set_value, job, 3, 'Done')
                            # Mark as idle if child was the last job
                            if i == njobs - 1:
                                self.idle = True
                                self.lock.acquire()
                    # Mark running child as such
                    elif future.running():
                        GLib.idle_add(self.queue.set_value, step, 3, 'Running')
                        # Mark parent as running if a child is
                        GLib.idle_add(self.queue.set_value, job, 3, 'Running')
            else:
                # Mark done jobs as such
                if future.done() and status != 'Failed':
                    GLib.idle_add(self.queue.set_value, job, 3, 'Done')
                    # Mark as idle if job was the last
                    if i == njobs - 1:
                        self.idle = True
                        self.lock.acquire()
                # Mark running job as such
                elif future.running():
                    GLib.idle_add(self.queue.set_value, job, 3, 'Running')

    def on_script_creator_clicked(self, button):
        self.tools_worker.submit(self._script_creator)

    def _script_creator(self):
        subprocess.call('pyae-script')

    def on_chap_editor_clicked(self, button):
        self.tools_worker.submit(self._chapter_editor)

    def _chapter_editor(self):
        subprocess.call('pyae-chapter')

    def on_vsrc_set(self, button):
        vqueue_button.set_sensitive(True)

    def on_asrc_set(self, button):
        aqueue_button.set_sensitive(True)

    def on_vqueue_clicked(self, button):
        self.worker.submit(self._wait)
        x = venc_cbtext.get_active_text()
        s = vsrc_fcbutton.get_filename()
        wd, f = os.path.split(s)
        if not os.path.isdir(wd + '/out'):
            os.mkdir(wd + '/out')
        d = wd + '/out/' + os.path.splitext(f)[0]
        if x == 'x264':
            dp = int(x264_depth_cbtext.get_active_text())
            q = x264_quality_spin.get_value_as_int()
            p = x264_preset_cbtext.get_active_text()
            if p == 'none':
                p = ''
            t = x264_tune_cbtext.get_active_text()
            if t == 'none':
                t = ''
            c = x264_container_cbtext.get_active_text()
            future = self.worker.submit(self._x264, s, d, dp, q, p, t, c)
        elif x == 'x265':
            dp = int(x265_depth_cbtext.get_active_text())
            q = x265_quality_spin.get_value_as_int()
            p = x265_preset_cbtext.get_active_text()
            if p == 'none':
                p = ''
            t = x265_tune_cbtext.get_active_text()
            if t == 'none':
                t = ''
            c = x265_container_cbtext.get_active_text()
            future = self.worker.submit(self._x265, s, d, dp, q, p, t, c)
        self.queue.append(None, [future, f, x, 'Waiting'])
        self.worker.submit(self._update_treeview)

    def on_aqueue_clicked(self, button):
        self.worker.submit(self._wait)
        x = aenc_cbtext.get_active_text()
        s = asrc_fcbutton.get_filename()
        wd, f = os.path.split(s)
        if not os.path.isdir(wd + '/out'):
            os.mkdir(wd + '/out')
        d = wd + '/out/' + os.path.splitext(f)[0]
        if x == 'fdkaac':
            m = fdkaac_mode_cbtext.get_active_text()
            b = fdkaac_bitrate_spin.get_value_as_int()
            q = fdkaac_quality_spin.get_value_as_int()
            c = fdkaac_container_cbtext.get_active_text()
            future = self.worker.submit(self._fdkaac, s, d, m, b, q, c)
        elif x == 'lame':
            m = lame_mode_cbtext.get_active_text()
            b = lame_bitrate_spin.get_value_as_int()
            q = lame_quality_spin.get_value_as_int()
            future = self.worker.submit(self._lame, s, d, m, b, q)
        self.queue.append(None, [future, f, x, 'Waiting'])
        self.worker.submit(self._update_treeview)

    def on_batch_src_set(self, button):
        wd = button.get_filename()
        self.sources = []
        self.data = []
        self.tracks = []

        # Keep videos only
        for f in os.listdir(wd):
            for cont in vconts:
                if re.search('\.' + cont + '$', f):
                    f = wd + '/' + f
                    self.sources.append(f)

        # Get source infos
        for i in range(len(self.sources)):
            s = self.sources[i]
            data = MatroskaOps(s).get_data()
            self.data.append(data)

        # Make sure tracks are identical across files
        # Dirty way of modifying a GtkMessageDialog primary message.
        error = track_mismatch_dialog.get_children()[0].get_children()[0]
        error = error.get_children()[0].get_children()[0]
        for i in range(1, len(self.data)):
            tracks_orig = self.data[0]
            tracks = self.data[i]
            o = os.path.basename(self.sources[0])
            f = os.path.basename(self.sources[i])
            if len(tracks) != len(tracks_orig):
                t = ('{} ({} tracks) and {} ({} tracks) differ from each '
                     'other. Please make sure all files share the same '
                     'layout.'
                    ).format(o, str(len(tracks_orig)), f, str(len(tracks)))
                error.set_text(t)
                track_mismatch_dialog.run()
            # -1 because there is a 'uid' entry
            for j in range(len(tracks) - 1):
                k = 'track' + str(j)
                codec_orig = tracks_orig[k]['codec']
                lang_orig = tracks_orig[k].get('lang', '')
                channels_orig = tracks_orig[k].get('channels', '')
                codec = tracks[k]['codec']
                lang = tracks[k].get('lang', '')
                channels = tracks[k].get('channels', '')
                if codec != codec_orig:
                    t = ('{} (track {}: {}) and {} (track {}: {}) have '
                         'different codecs. Please make sure all files '
                         'share the same layout.'
                        ).format(o, str(j), codec_orig, f, str(j), codec)
                    error.set_text(t)
                    track_mismatch_dialog.run()
                elif lang != lang_orig:
                    t = ('{} (track {}: {}) and {} (track {}: {}) have '
                         'different languages. Please make sure all files '
                         'share the same layout.'
                        ).format(o, str(j), lang_orig, f, str(j), lang)
                    error.set_text(t)
                    track_mismatch_dialog.run()
                elif channels != channels_orig:
                    t = ('{} (track {}: {}) and {} (track {}: {}) have '
                         'different channels. Please make sure all files '
                         'share the same layout.'
                        ).format(o, str(j), channels_orig, f, str(j), channels)
                    error.set_text(t)
                    track_mismatch_dialog.run()
        self._update_tracks()
        batch_queue_button.set_sensitive(True)

    def _update_tracks(self):
        # A new builder instance needs to be created for each entry,
        # therefore put the template on its own to avoid loading a large
        # file every time
        for track in batch_tracks_vbox.get_children():
            batch_tracks_vbox.remove(track)

        # -1 because there is a 'uid' entry
        tracks = self.data[0]
        for i in range(len(tracks) - 1):
            builder = Gtk.Builder()
            track_glade = resource_string(__name__, 'glade/track.glade')
            track_glade = track_glade.decode('utf8')
            builder.add_from_string(track_glade)
            grid = builder.get_object('grid')
            batch_tracks_vbox.pack_start(grid, False, False, 0)
            enable_check = builder.get_object('enable-check')
            enable_check.connect('toggled', handler.on_track_enable_toggled, i)
            codec_entry = builder.get_object('codec-entry')
            name_entry = builder.get_object('name-entry')
            name_entry.connect('changed', handler.on_track_name_changed, i)
            lang_entry = builder.get_object('lang-entry')
            lang_entry.connect('changed', handler.on_track_lang_changed, i)
            encode_check = builder.get_object('encode-check')
            encode_check.connect('toggled', handler.on_track_encode_toggled, i)

            track = tracks['track' + str(i)]
            codec = track['codec']
            name = track.get('name', '')
            lang = track.get('lang', 'und')
            if codec in vtypes:
                type = 'video'
                enable_check.set_label('Video')
                enable_check.set_sensitive(False)
                codec = vtypes[codec]
            elif codec in atypes:
                type = 'audio'
                enable_check.set_label('Audio')
                channels = track['channels']
                if channels == '2':
                    channels = '2.0'
                elif channels == '6':
                    channels = '5.1'
                elif channels == '7':
                    channels = '6.1'
                elif channels == '8':
                    channels = '7.1'
                codec = atypes[codec]
            elif codec in stypes:
                type = 'subtitle'
                enable_check.set_label('Subtitle')
                encode_check.set_sensitive(False)
                codec = stypes[codec]

            self.tracks.append([type, codec, name, lang, True, True, i])
            if type == 'audio':
                codec = codec + ' ' + channels
            if type == 'subtitle':
                # Put this here to avoid out of range index.
                encode_check.set_active(False)
            codec_entry.set_text(codec)
            name_entry.set_text(name)
            lang_entry.set_text(lang)

        window.show()

    def on_track_mismatch_ok_clicked(self, button):
        track_mismatch_dialog.hide()

    def on_batch_queue_clicked(self, button):
        wd = batch_src_fcbutton.get_filename()
        if not os.path.isdir(wd + '/out'):
            os.mkdir(wd + '/out')

        for i in range(len(self.sources)):
            self.worker.submit(self._wait)
            vtrack = []
            atracks = []
            stracks = []
            s = self.sources[i]
            f = os.path.basename(s)
            uid = self.data[i]['uid']
            job = self.queue.append(None, [None, f, '', 'Waiting'])
            for track in self.tracks:
                # track = [id, filename, extension, name, language, transcode?]
                j = track[6]
                fn, ex = os.path.splitext(f)
                ex = ex.strip('.')
                n = track[2]
                l = track[3]
                t = track[5]
                if track[0] == 'video' and track[4]:
                    if track[5]:
                        fn = wd + '/out/' + fn
                        ex = track[1]
                    else:
                        fn = wd + '/' + fn
                    vtrack = [j, fn, ex, n, l, t]
                if track[0] == 'audio' and track[4]:
                    if track[5]:
                        fn = wd + '/out/' + fn + '_' + str(j)
                        ex = track[1]
                    else:
                        fn = wd + '/' + fn
                    atracks.append([j, fn, ex, n, l, t])
                if track[0] == 'subtitle' and track[4]:
                    fn = wd + '/' + fn
                    stracks.append([j, fn, ex, n, l, t])

            # Create VapourSynth script
            if vtrack[5]:
                vtrack[0] = 0
                fps = []
                if fps_check.get_active():
                    fn = fpsnum_spin.get_value_as_int()
                    fd = fpsden_spin.get_value_as_int()
                    fps = [fn, fd]
                crop = []
                if crop_check.get_active():
                    cl = lcrop_spin.get_value_as_int()
                    cr = rcrop_spin.get_value_as_int()
                    ct = tcrop_spin.get_value_as_int()
                    cb = bcrop_spin.get_value_as_int()
                    crop = [cl, cr, ct, cb]
                resize = []
                if resize_check.get_active():
                    rw = wresize_spin.get_value_as_int()
                    rh = hresize_spin.get_value_as_int()
                    rf = resize_algo_cbtext.get_active_text()
                    resize = [rw, rh, rf]
                sdenoise = []
                if sdenoise_check.get_active():
                    sdf = sdenoise_cbtext.get_active_text()
                    if sdf == 'RemoveGrain':
                        rgm = [rgvs_mode_spin.get_value_as_int()]
                        if rgvs_adv_check.get_active():
                            rgm.append(rgvs_umode_spin.get_value_as_int())
                            rgm.append(rgvs_vmode_spin.get_value_as_int())
                        sdenoise = [sdf, rgm]
                tdenoise = []
                if tdenoise_check.get_active():
                    tdf = tdenoise_cbtext.get_active_text()
                    if tdf == 'TemporalSoften':
                        tsr = tsoft_rad_spin.get_value_as_int()
                        tsl = tsoft_lt_spin.get_value_as_int()
                        tsc = tsoft_ct_spin.get_value_as_int()
                        tss = tsoft_sc_spin.get_value_as_int()
                        tdenoise = [tdf, tsr, tsl, tsc, tss]
                    elif tdf == 'FluxSmoothT':
                        fst = fsmooth_tt_spin.get_value_as_int()
                        fsp = []
                        if fsmooth_yplane_check.get_active():
                            fsp.append(0)
                        if fsmooth_uplane_check.get_active():
                            fsp.append(1)
                        if fsmooth_vplane_check.get_active():
                            fsp.append(2)
                        tdenoise = [tdf, fst, fsp]
                stdenoise = []
                if stdenoise_check.get_active():
                    stdf = stdenoise_cbtext.get_active_text()
                    if stdf == 'FluxSmoothST':
                        fst = fsmooth_tt_spin.get_value_as_int()
                        fss = fsmooth_st_spin.get_value_as_int()
                        fsp = []
                        if fsmooth_yplane_check.get_active():
                            fsp.append(0)
                        if fsmooth_uplane_check.get_active():
                            fsp.append(1)
                        if fsmooth_vplane_check.get_active():
                            fsp.append(2)
                        stdenoise = [stdf, fst, fss, fsp]
                deband = []
                if deband_check.get_active():
                    df = deband_cbtext.get_active_text()
                    if df == 'f3kdb':
                        fpr = f3kdb_preset_cbtext.get_active_text()
                        fpl = f3kdb_planes_cbtext.get_active_text()
                        fdp = f3kdb_depth_spin.get_value_as_int()
                        if fpl in ['luma', 'chroma']:
                            fpr = fpr + '/' + fpl
                        if not f3kdb_grain_check.get_active():
                            fpr = fpr + '/nograin'
                        deband = [df, fpr, fdp]

                self.worker.submit(self._vpy, s, fps, crop, resize, sdenoise,
                                  tdenoise, stdenoise, deband)

                # Encode video
                x = batch_venc_cbtext.get_active_text()
                if x == 'x264':
                    dp = int(x264_depth_cbtext.get_active_text())
                    q = x264_quality_spin.get_value_as_int()
                    p = x264_preset_cbtext.get_active_text()
                    if p == 'none':
                        p = ''
                    t = x264_tune_cbtext.get_active_text()
                    if t == 'none':
                        t = ''
                    c = x264_container_cbtext.get_active_text()
                    vtrack[2] = c

                    future = self.worker.submit(self._x264, s, vtrack[1], dp,
                                                q, p, t, c)
                if x == 'x265':
                    dp = int(x265_depth_cbtext.get_active_text())
                    q = x265_quality_spin.get_value_as_int()
                    p = x265_preset_cbtext.get_active_text()
                    if p == 'none':
                        p = ''
                    t = x265_tune_cbtext.get_active_text()
                    if t == 'none':
                        t = ''
                    c = x265_container_cbtext.get_active_text()
                    vtrack[2] = c

                    future = self.worker.submit(self._x265, s, vtrack[1], dp,
                                                q, p, t, c)

                self.queue.append(job, [future, '', x, 'Waiting'])

            # Extract audio
            tracks = []
            for track in atracks:
                if track[5]:
                    tracks.append(track)

                    future = self.worker.submit(self._extract, s, tracks)
                    self.queue.append(job, [future, '', 'extract', 'Waiting'])

            # Encode audio
            for track in atracks:
                if track[5]:
                    x = batch_aenc_cbtext.get_active_text()
                    a = track[1] + '.' + track[2]
                    if x == 'fdkaac':
                        m = fdkaac_mode_cbtext.get_active_text()
                        b = fdkaac_bitrate_spin.get_value_as_int()
                        q = fdkaac_quality_spin.get_value_as_int()
                        c = fdkaac_container_cbtext.get_active_text()

                        future = self.worker.submit(self._fdkaac, a, track[1],
                                                    m, b, q, c)

                    elif x == 'lame':
                        m = lame_mode_cbtext.get_active_text()
                        b = lame_bitrate_spin.get_value_as_int()
                        q = lame_quality_spin.get_value_as_int()

                        future = self.worker.submit(self._lame, a, track[1], m,
                                                    b, q)

                    self.queue.append(job, [future, '', x, 'Waiting'])

            # Merge tracks
            o = wd + '/out/' + f
            future = self.worker.submit(self._merge, s, o, vtrack, atracks,
                                        stracks, uid)
            self.queue.append(job, [future, '', 'merge', 'Waiting'])

            # Clean up
            self.worker.submit(self._clean, wd)

            self.worker.submit(self._update_treeview)

    def _extract(self, source, tracks):
        self._update_treeview()
        cmd = MatroskaOps(source).extract(tracks)
        self.proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                     universal_newlines=True)
        self._mkvtoolnix_progress('x')

    def _merge(self, source, dest, vtrack, atracks, stracks, uid):
        self._update_treeview()
        # Put that here until I figure out why it screws the extract step when
        # done above.
        for track in atracks:
            if track[5]:
                track[0] = 0
                x = batch_aenc_cbtext.get_active_text()
                if x == 'fdkaac':
                    c = fdkaac_container_cbtext.get_active_text()
                    track[2] = c
                elif x == 'lame':
                    track[2] = 'mp3'

        cmd = MatroskaOps(source).merge(dest, vtrack, atracks, stracks, uid)
        self.proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                     universal_newlines=True)
        self._mkvtoolnix_progress('m')

    def _clean(self, directory):
        for f in os.listdir(directory):
            if re.search('\.vpy$', f) or re.search('\.ffindex$', f):
                os.remove(directory + '/' + f)
        for f in os.listdir(directory + '/out/'):
            if not re.search('\.mkv$', f):
                os.remove(directory + '/out/' + f)

    def _vpy(self, source, fps, crop, resize, sdenoise, tdenoise, stdenoise,
            deband):
        s = Encode(source).vpy(fps, crop, resize, sdenoise, tdenoise,
                               stdenoise, deband)
        print(s)
        vpy = re.sub('[^.]*$', 'vpy', source)
        print(vpy)
        with open(vpy, 'w') as f:
            f.write(s)

    def _info(self, source):
        cmd = Encode(source).info()
        self.proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                     universal_newlines=True)
        GLib.idle_add(status_pbar.set_fraction, 0)
        GLib.idle_add(status_pbar.set_text, 'Encoding video...')
        while self.proc.poll() == None:
            line = self.proc.stdout.readline()
            # Get the frame total
            if 'Frames:' in line:
                d = int(line.split(' ')[1])
        print(d)
        return d

    def _x264(self, source, dest, depth, quality, preset, tune, container):
        self._update_treeview()
        d = self._info(source)
        cmd = Encode(source).x264(dest, depth, quality, preset, tune,
                                  container)
        self.proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                                     universal_newlines=True)
        self._video_progress(d)

    def _x265(self, source, dest, depth, quality, preset, tune, container):
        self._update_treeview()
        d = self._info(source)
        cmd = Encode(source).x265(dest, depth, quality, preset, tune,
                                  container)
        self.proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                                     universal_newlines=True)
        self._video_progress(d)

    def _fdkaac(self, source, dest, mode, bitrate, quality, container):
        self._update_treeview()
        cmd = Encode(source).fdkaac(dest, mode, bitrate, quality, container)
        self.proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                                     universal_newlines=True)
        self._audio_progress()

    def _lame(self, source, dest, mode, bitrate, quality):
        self._update_treeview()
        cmd = Encode(source).lame(dest, mode, bitrate, quality)
        self.proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE,
                                     universal_newlines=True)
        self._audio_progress()

    def _mkvtoolnix_progress(self, mode):
        GLib.idle_add(status_pbar.set_fraction, 0)
        if mode == 'x':
            GLib.idle_add(status_pbar.set_text, 'Extracting tracks...')
        elif mode == 'm':
            GLib.idle_add(status_pbar.set_text, 'Merging tracks...')
        while self.proc.poll() == None:
            line = self.proc.stdout.readline()
            if 'Progress:' in line:
                f = int(re.findall('[0-9]+', line)[0]) / 100
                GLib.idle_add(status_pbar.set_fraction, f)
        if self.proc.poll() < 0:
            GLib.idle_add(status_pbar.set_fraction, 0)
        else:
            GLib.idle_add(status_pbar.set_fraction, 1)
        GLib.idle_add(status_pbar.set_text, 'Ready')

    def _video_progress(self, duration):
        while self.proc.poll() == None:
            line = self.proc.stderr.readline()
            # Get the current frame
            if re.match('^[0-9]+ ', line):
                position = int(line.split(' ')[0])
                f = round(position / duration, 2)
                GLib.idle_add(status_pbar.set_fraction, f)
        if self.proc.poll() < 0:
            GLib.idle_add(status_pbar.set_fraction, 0)
        else:
            GLib.idle_add(status_pbar.set_fraction, 1)
        GLib.idle_add(status_pbar.set_text, 'Ready')

    def _audio_progress(self):
        GLib.idle_add(status_pbar.set_fraction, 0)
        GLib.idle_add(status_pbar.set_text, 'Encoding audio...')
        while self.proc.poll() == None:
            line = self.proc.stderr.readline()
            # Get the clip duration
            if 'Duration:' in line:
                d = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}', line)[0]
                h, m, s = d.split(':')
                d = int(h) * 3600 + int(m) * 60 + int(s)
            # Get the current timestamp
            if 'time=' in line:
                p = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}', line)[0]
                h, m, s = p.split(':')
                p = int(h) * 3600 + int(m) * 60 + int(s)
                f = round(p / d, 2)
                GLib.idle_add(status_pbar.set_fraction, f)
        if self.proc.poll() < 0:
            GLib.idle_add(status_pbar.set_fraction, 0)
        else:
            GLib.idle_add(status_pbar.set_fraction, 1)
        GLib.idle_add(status_pbar.set_text, 'Ready')

    def on_batch_sconf_clicked(self, button):
        vpy_dialog.run()

    def on_vpy_ok_clicked(self, button):
        vpy_dialog.hide()

    def on_fps_toggled(self, check):
        state = check.get_active()
        fpsnum_spin.set_sensitive(state)
        fpsden_spin.set_sensitive(state)

    def on_crop_toggled(self, check):
        state = check.get_active()
        lcrop_spin.set_sensitive(state)
        rcrop_spin.set_sensitive(state)
        tcrop_spin.set_sensitive(state)
        bcrop_spin.set_sensitive(state)

    def on_resize_toggled(self, check):
        state = check.get_active()
        wresize_spin.set_sensitive(state)
        hresize_spin.set_sensitive(state)
        resize_algo_cbtext.set_sensitive(state)

    def on_sdenoise_toggled(self, check):
        state = check.get_active()
        sdenoise_cbtext.set_sensitive(state)
        sdenoise_conf_button.set_sensitive(state)

    def on_sdenoise_conf_clicked(self, button):
        f = sdenoise_cbtext.get_active_text()
        if f == 'RemoveGrain':
            rgvs_dialog.run()

    def on_tdenoise_toggled(self, check):
        state = check.get_active()
        tdenoise_cbtext.set_sensitive(state)
        tdenoise_conf_button.set_sensitive(state)

    def on_tdenoise_conf_clicked(self, button):
        f = tdenoise_cbtext.get_active_text()
        if f == 'TemporalSoften':
            tsoft_dialog.run()
        elif f == 'FluxSmoothT':
            fsmooth_st_spin.set_sensitive(False)
            fsmooth_dialog.run()

    def on_stdenoise_toggled(self, check):
        state = check.get_active()
        stdenoise_cbtext.set_sensitive(state)
        stdenoise_conf_button.set_sensitive(state)

    def on_stdenoise_conf_clicked(self, button):
        f = stdenoise_cbtext.get_active_text()
        if f == 'FluxSmoothST':
            fsmooth_st_spin.set_sensitive(True)
            fsmooth_dialog.run()

    def on_rgvs_adv_toggled(self, check):
        state = check.get_active()
        rgvs_umode_spin.set_sensitive(state)
        rgvs_vmode_spin.set_sensitive(state)

    def on_rgvs_ok_clicked(self, button):
        rgvs_dialog.hide()

    def on_tsoft_ok_clicked(self, button):
        tsoft_dialog.hide()

    def on_fsmooth_ok_clicked(self, button):
        fsmooth_dialog.hide()

    def on_deband_toggled(self, check):
        state = check.get_active()
        deband_cbtext.set_sensitive(state)
        deband_conf_button.set_sensitive(state)

    def on_deband_conf_clicked(self, button):
        f = deband_cbtext.get_active_text()
        if f == 'f3kdb':
            f3kdb_dialog.run()

    def on_f3kdb_ok_clicked(self, button):
        f3kdb_dialog.hide()

    def on_track_name_changed(self, entry, i):
        self.tracks[i][2] = entry.get_text()

    def on_track_lang_changed(self, entry, i):
        self.tracks[i][3] = entry.get_text()

    def on_track_enable_toggled(self, check, i):
        self.tracks[i][4] = check.get_active()

    def on_track_encode_toggled(self, check, i):
        self.tracks[i][5] = check.get_active()

    def on_vconf_clicked(self, button):
        x = venc_cbtext.get_active_text()
        if x in ['x264', 'x264-10bit']:
            x264_dialog.run()
        elif x in ['x265', 'x265-10bit']:
            x265_dialog.run()

    def on_batch_vconf_clicked(self, button):
        x = batch_venc_cbtext.get_active_text()
        if x in ['x264', 'x264-10bit']:
            x264_dialog.run()
        if x in ['x265', 'x265-10bit']:
            x265_dialog.run()

    def on_x264_ok_clicked(self, button):
        x264_dialog.hide()

    def on_x265_ok_clicked(self, button):
        x265_dialog.hide()

    def on_aconf_clicked(self, button):
        x = aenc_cbtext.get_active_text()
        if x == 'fdkaac':
            fdkaac_dialog.run()
        elif x == 'lame':
            lame_dialog.run()

    def on_batch_aconf_clicked(self, button):
        x = batch_aenc_cbtext.get_active_text()
        if x == 'fdkaac':
            fdkaac_dialog.run()
        elif x == 'lame':
            lame_dialog.run()

    def on_fdkaac_mode_changed(self, combo):
        m = combo.get_active_text()
        if m == 'CBR':
            fdkaac_bitrate_spin.set_sensitive(True)
            fdkaac_quality_spin.set_sensitive(False)
        elif m == 'VBR':
            fdkaac_bitrate_spin.set_sensitive(False)
            fdkaac_quality_spin.set_sensitive(True)

    def on_fdkaac_ok_clicked(self, button):
        fdkaac_dialog.hide()

    def on_lame_mode_changed(self, combo):
        m = combo.get_active_text()
        if m == 'CBR' or m == 'ABR':
            lame_bitrate_spin.set_sensitive(True)
            lame_quality_spin.set_sensitive(False)
        elif m == 'VBR':
            lame_bitrate_spin.set_sensitive(False)
            lame_quality_spin.set_sensitive(True)

    def on_lame_ok_clicked(self, button):
        lame_dialog.hide()

    def on_start_clicked(self, button):
        if len(self.queue):
            self.idle = False
            self.lock.release()

    def on_delete_clicked(self, button):
        job = queue_selection.get_selected()[1]
        if job != None:
            # If child, select parent instead
            if self.queue.iter_depth(job) == 1:
                job = self.queue.iter_parent(job)
            # If parent, delete all children
            if self.queue.iter_has_child(job):
                nsteps = self.queue.iter_n_children(job)
                for i in range(nsteps):
                    step = self.queue.iter_nth_child(job, 0)
                    future = self.queue.get_value(step, 0)
                    # Cancel and delete child only if not running
                    if not future.running():
                        future.cancel()
                        self.queue.remove(step)
                # Delete parent only when all children are
                if not self.queue.iter_has_child(job):
                    self.queue.remove(job)
            else:
                future = self.queue.get_value(job, 0)
                # Cancel and delete job only if not running
                if not future.running():
                    future.cancel()
                    self.queue.remove(job)

    def on_clear_clicked(self, button):
        # Don't clear when jobs are running
        if self.idle:
            njobs = len(self.queue)
            for i in range(njobs):
                path = Gtk.TreePath(i)
                job = self.queue.get_iter(path)
                # Clear children before parents
                if self.queue.iter_has_child(job):
                    nsteps = self.queue.iter_n_children(job)
                    for j in range(nsteps):
                        path = Gtk.TreePath([i, j])
                        step = self.queue.get_iter(path)
                        future = self.queue.get_value(step, 0)
                        # Cancel pending children before deleting them
                        if not future.done():
                            future.cancel()
                else:
                    future = self.queue.get_value(job, 0)
                    # Cancel pending jobs before deleting them
                    if not future.done():
                        future.cancel()
            # Clear queue
            self.queue.clear()

    def on_stop_clicked(self, button):
        if not self.idle:
            self.idle = True
            # Wait for the process to terminate
            while self.proc.poll() == None:
                self.proc.terminate()

            njobs = len(self.queue)
            for i in range(njobs):
                path = Gtk.TreePath(i)
                job = self.queue.get_iter(path)
                status = self.queue.get_value(job, 3)
                if status == 'Running':
                    if self.queue.iter_has_child(job):
                        nsteps = self.queue.iter_n_children(job)
                        for j in range(nsteps):
                            path = Gtk.TreePath([i, j])
                            step = self.queue.get_iter(path)
                            future = self.queue.get_value(step, 0)
                            # Mark children as failed
                            self.queue.set_value(step, 3, 'Failed')
                            # Cancel pending children
                            if not future.done():
                                future.cancel()
                    # Mark job as failed
                    self.queue.set_value(job, 3, 'Failed')

            status_pbar.set_fraction(0)
            status_pbar.set_text('Ready')

    def on_window_delete_event(self, *args):
        Gtk.main_quit(*args)

handler = Handler()
builder.connect_signals(handler)

window.show_all()

Gtk.main()

# vim: ts=4 sw=4 et:
