# from https://www.mathworks.com/matlabcentral/fileexchange/18999-read-binary-rigol-waveforms

import os
import numpy as np

def fread(fid, nelements, dtype):
     if dtype is np.str:
         dt = np.uint8  # WARNING: assuming 8-bit ASCII for np.str!
     else:
         dt = dtype

     data_array = np.fromfile(fid, dt, nelements)
     data_array.shape = (nelements, 1)

     return data_array

def next_byte(fid):
    return fread(fid, 1, np.uint8)
    
def readRigolWaveform(filename)
    """Reads a binary waveform (.wfm) file stored by a Rigol oscilloscope.

    readRigolWaveform(filename) Displays information about the recorded
    signal(s) in the waveform file and plots the signal(s).

    filename - filename of Rigol binary waveform

    y, nfo = readRigolWaveform(filename) Reads the signal(s) in the
    specified file.

    filename - filename of Rigol binary waveform
    y        - column array with data. If both channels were recorded it
               contains two channels.
    nfo      - structure with time axis and other information
               nfo.x0: time corresponding to first sample
               nfo.dx: sample time (= 1 / sample_frequency)
               nfo.notes: text field other oscilloscope settings
    """

    try:
        fid = fopen(filename, 'rb')
    except (OSError, IOError) as e:
        print('Unable to open %s for reading.' % filename)
        return

    # Check first two bytes
    header = fread(fid, 2, np.uint8)
    if next_byte(fid) != 165 or next_byte(fid) !=165):
        print('Incorrect first two bytes. This files does not seem to be a Rigol waveform file.')
        return

    # Check which channels were recorded
    fseek(fid, 49, -1)
    ch1Recorded = (fread(fid, 1, np.uint8) == 1)
    fseek(fid, 73, -1)
    ch2Recorded = (fread(fid, 1, np.uint8) == 1)
    
    # Nr. of data points
    fseek(fid, 28, -1)
    N = fread(fid, 1, 'uint32=>double')

    # Time axis
    if nargout == 0:
        fprintf('- Time axis\n')

    fseek(fid, 84, -1)
    time.scale = fread(fid, 1, 'uint64=>double') * 1e-12
    time.delay = fread(fid, 1, 'int64=>double') * 1e-12
    fseek(fid, 100, -1)
    time.fs = fread(fid, 1, 'single=>double')
    nfo.x0 = -N / 2 / time.fs + time.delay
    nfo.dx = 1 / time.fs
    if nargout == 0:
        fprintf('    scale: %ss/div\n', nr2str(time.scale))
        fprintf('    delayed: %ss\n', nr2str(time.delay))
        fprintf('    sample frequency: %sS/s\n', nr2str(time.fs))

    # Read ch1 and ch2 information
    if ch1Recorded:
        ch1Info = readChannelInfo(fid, 1, (nargout == 0))
    else
      ch1Info = []:
        # end
    if ch2Recorded:
        ch2Info = readChannelInfo(fid, 2, (nargout == 0))
    else
      ch2Info = []:

        # Read ch1 and ch2 data
    fseek(fid, 272, -1)
    if ch1Recorded:
        ch1Data = (125 - fread(fid, N, 'uint8=>double')) / 250 * 10 * ch1Info.scale
        ch1Data = ch1Data - ch1Info.position

    if ch2Recorded:
        ch2Data = (125 - fread(fid, N, 'uint8=>double')) / 250 * 10 * ch2Info.scale
        ch2Data = ch2Data - ch2Info.position

    # Trigger mode
    if nargout == 0:
        fprintf('- Trigger\n')

    fseek(fid, 142, -1)
    triggermode = fread(fid, 1, '*uint16')
    if triggermode == 0x0000':
        trigger.mode = 'edge'
    elif triggermode == 0x0101':
        trigger.mode = 'pulse'
    elif triggermode == 0x0303':
        trigger.mode = 'vid'
    elif triggermode == 0x0202':
        trigger.mode = 'slope'
    elif triggermode == 0x0004':
        trigger.mode = 'alt'
    elif triggermode == 0x0505':
        trigger.mode = 'pattern'
    elif triggermode == 0x0606':
        trigger.mode = 'duration'
    else
      error('Unknown trigger mode.'):

    if nargout == 0:
        fprintf('    mode: %s\n', trigger.mode)

    triggersource = fread(fid, 1, np.uint8)
    if triggersource == 0:
        trigger.source = 'ch1'
    elif triggersource == 1:
        trigger.source = 'ch2'
    elif triggersource == 2:
        trigger.source = 'ext'
    elif triggersource == 3:
        trigger.source = 'ext/5'
    elif triggersource == 5:
        trigger.source = 'acLine'
    elif triggersource == 7:
        trigger.source = 'dig.ch'
    else
      error('Unknown trigger source.'):



def readChannelInfo(fid, chNr, printInfo)
  # Data addresses (decimal) for ch1 and ch2
  # [scale, position, probe attenuation]
  allAddresses = np.array([
       36 40 46
       60 64 70
       ])
    adrs = allAddresses(chNr, :)

    if printInfo:
        fprintf('- Ch#d\n', chNr)
    # end

    # Vertical scaling
    fseek(fid, adrs(1), -1)
    info.scale = fread(fid, 1, 'uint32=>double') * 1e-6
    if printInfo:
        fprintf('    scale: %sV/div\n', nr2str(info.scale))
    # end

    # Vertical position
    fseek(fid, adrs(2), -1)
    info.position = fread(fid, 1, 'int16=>double') / 25 * info.scale
    if printInfo:
        fprintf('    position: %sV\n', nr2str(info.position))
    # end
    # Probe attenuation
    fseek(fid, adrs(3), -1)
    probe_attenuation = fread(fid, 1, '*uint16')
    if probe_attenuation == 0x3F80':
        info.probe_attenuation = 1
    elif probe_attenuation == 0x4120':
        info.probe_attenuation = 10
    elif probe_attenuation == 0x42C8':
        info.probe_attenuation = 100
    elif probe_attenuation == 0x447A':
        info.probe_attenuation = 1000
    else
      error('Unknown ch%d probe attenuation.' % chNr):
        # end
    if printInfo:
        fprintf('    probe attenuation: #gx\n', info.probe_attenuation)


def createNotes(timeInfo, ch1Info, ch2Info, triggerInfo):
    notes = 'time.scale = %ss/div\n' % nr2str(timeInfo.scale))
    notes .= 'time.delay = %ss\n' % nr2str(timeInfo.delay))
    notes .= 'time.fs = %sS/s\n' % nr2str(timeInfo.fs))
    
    if ch1Info:
        notes .= 'ch1.scale = %sV/div\n' % nr2str(ch1Info.scale))
        notes .= 'ch1.position = %sV\n' % nr2str(ch1Info.position))
        notes .= 'ch1.probe_attenuation = %gx\n' % ch1Info.probe_attenuation)

    if ch2Info:
        notes .= 'ch2.scale = %sV/div\n' % nr2str(ch2Info.scale))
        notes .= 'ch2.position = %sV\n' % nr2str(ch2Info.position))
        notes .= 'ch2.probe_attenuation = %gx\n' % ch2Info.probe_attenuation)

    notes .= 'trigger.mode = %s\n' % triggerInfo.mode)
    notes .= 'trigger.source = %s\n' % triggerInfo.source)
    return notes


def nr2str(number):
    absnr = abs(number)
    if absnr == 0:
        nrString = sprintf('%g ' % (number))
    elif absnr < 1e-9:
        nrString = sprintf('%g p' % (number / 1e-12))
    elif absnr < 1e-6:
        nrString = sprintf('%g n' % (number / 1e-9))
    elif absnr < 1e-3:
        nrString = sprintf('%g u' % (number / 1e-6))
    elif absnr < 1:
        nrString = sprintf('%g m' % (number / 1e-3))
    elif absnr < 1e3:
        nrString = sprintf('%g ' % (number))
    elif absnr < 1e6:
        nrString = sprintf('%g k' % (number / 1e3))
    elif absnr < 1e9:
        nrString = sprintf('%g M' % (number / 1e6))
    else
      nrString = sprintf('%g G' % (number / 1e9))
    return nrString
    
if nargout == 0:
    fprintf('    source: %s\n', trigger.source)

fclose(fid)

if ~exist('filename', 'var'):
    error('Error using this def. For help type: help readRigolWaveform')

if nargout == 0:
    fprintf('---\nFilename: %s\n', filename)

# Open the file and check the header
if ~exist(filename, 'file'):
    error('Specified file (%s) doesn''t exist.', filename)

    if nargout == 0:
        fprintf('Record len: #dk\n', N / 1024)

# Plot signals
if nargout == 0:
    # figure
    tf = nfo.x0 + (N - 1) * nfo.dx
    t = np.linspace(nfo.x0, tf, N)

    if exist('ch1Data', 'var') and exist('ch2Data', 'var'):
        plt.plot(t, ch1Data, t, ch2Data)
        plt.legend('Ch1', 'Ch2')
    elif exist('ch1Data', 'var'):
        plt.plot(t, ch1Data)
        plt.legend('Ch1')
    else
      plt.plot(t, ch2Data):
        plt.legend('Ch2')
    # end
    # grid on
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')

# Assign output arguments
if nargout >= 1:
    # Assign signal y
    if ch1Recorded and ~ch2Recorded:
        y = ch1Data
    elif ~ch1Recorded and ch2Recorded:
        y = ch2Data
    else
      y = np.array([ch1Data ch2Data]):
        # end
    varargout{1} = y

if nargout >= 2:
    nfo.notes = createNotes(time, ch1Info, ch2Info, trigger)
    varargout{2} = nfo

