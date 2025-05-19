import numpy as np



def read_one_channel(filename, format, channel_name, scaled=True):
    """
    Simple function on top of neo that read one channel from file in supported format.
    
    >>>  ecg, srate = physio.read_one_channel('/path/to/micromed_file.TRC', 'micromed', 'p7+', scaled=True)


    Parameters
    ----------
    filename: str or Path
        The file
    format: str
        The foormat of the file 'micromed', 'brainvision' or 'biosemi' 
    channel_name: str | list[str]
        The channel names.
    scaled: bool (default True)
        Return traces scaled to unit or unscaled (int16)

    Returns
    -------
    trace: np.array
        The trace of the channel as a numpy 1d array.
    srate: float
        The sampling rate.
    """

    import neo
    supported_format = {
        'micromed' : neo.MicromedIO,
        'brainvision' : neo.BrainVisionIO,
    }    

    if format not in supported_format.keys():
        if format == 'biosemi':
            channels = channel_name if isinstance(channel_name, list) else list(channel_name)
            return read_bdf(file_name=filename, channels=channels)
        raise ValueError(f'{format} is not a supported format ({list(supported_format.keys())})')

    neo_class = supported_format[format]
    reader = neo_class(filename)

    # channel must be unique
    all_names = reader.header['signal_channels']['name']
    inds,  = np.nonzero(all_names == channel_name)
    if inds.size == 0:
        raise ValueError(f'{channel_name} do not exists in this file.\n Possible channels : {list(all_names)}')
    if inds.size > 1:
        raise ValueError(f'{channel_name} is not unique in this file.\n Possible channels : {list(all_names)}')
    ind = inds[0]

    # find the stream
    stream_id = reader.header['signal_channels']['stream_id'][ind]
    stream_index = np.nonzero(reader.header['signal_streams']['id'] == stream_id)[0][0]

    # find channel index in stream
    mask = reader.header['signal_channels']['stream_id'] == stream_id
    chans = reader.header['signal_channels'][mask]
    channel_indexes, = np.nonzero(chans['name'] == channel_name)

    traces = reader.get_analogsignal_chunk(block_index=0, seg_index=0, i_start=None,i_stop=None,
                                         stream_index=stream_index, 
                                         channel_indexes=channel_indexes)
                                        #   channel_names=[channel_name])
    
    if scaled:
        traces = reader.rescale_signal_raw_to_float(traces, dtype='float32',
                                    stream_index=stream_index, channel_indexes=channel_indexes)

    trace = traces[:, 0]

    srate = reader.header['signal_channels']['sampling_rate'][0]

    return trace, srate


def read_bdf(file_name, channels: list[str]):
    """
    Simple function on top of mne that read a bdf file from biosemi environment.
    The function returns the channels in parameter.

    Parameters
    ----------
    file_name: str
        The file name
    channels: list[str]
        The list of channels to extract.

    Returns
    -------
    data: pd.DataFrame
       DataFrame with the signals
    srate: float
        Sampling rate.
    """
    import mne
    from pandas import DataFrame
    content_bdf  = mne.io.read_raw_bdf(file_name, preload=True)
    channels_bdf = content_bdf.ch_names
    data = {}
    srate = channels_bdf.info["sfreq"]
    
    for ch in channels:
        if ch in channels_bdf:
            data[ch] = content_bdf.get_data(picks=ch).flatten()
        else:
            raise ValueError(f"{ch} does not exist in the file. \nPossible channel{list(channels_bdf)}")
    
    return DataFrame(data=data), srate

    