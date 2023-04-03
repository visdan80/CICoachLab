function resultStruct = playVocoderRun(signalStruct,playerStruct,parHandle) %#ok<INUSD>
% usage playSoundRun(signal,playerStruct,parHandle)
%
% The vocoder is implemented using bufferworth filter bands and the
% stimulation can be used with a pulse train, sinusoids and noise like
% stimulation.
%
% input:
%   signalStruct    player expects sound vector in signal.ac
%                   with a provided signal.fs.
%   playerStruct    settings for the player
%
% ouput:
%   resultSignal    the generated vocoder signal is put out.
%____________________________________________________________
% SVN: $Revision$
%      $Date$
%      $Author$
%____________________________________________________________

global psyVar

% check for correct input format of signal
if ~isstruct(signalStruct)||~isfield(signalStruct,'ac')
    error('Input must be a struct with signal.ac: signal.ac.sig signal.ac.fs;')
end
% check if data should be played
if isempty(signalStruct.ac.sig)
    disp('Not playing sound in vocoder because of empty signal!');
    return
end

if isfield(psyVar,'cal') && ...
   ~isnan( psyVar.cal.gen.value)
    % "generatorCorrectionLevel" level has to be added to the other levels.
    % A negative correction level means that the level of the signal has to
    % be decreased by this amount to reach a clibrated signal. A signal
    % with rms 1 after the correction corresponds to the level of the
    % player + sigLevelCorrectdB
    generatorLevel = psyVar.cal.gen.value;
else
    generatorLevel = 0;
end

% same functionality as in playSound player
dbTmp = ( ( playerStruct.level - psyVar.cal.system.valueDB ) + psyVar.cal.sigLevelCorrectdB - generatorLevel);
scaleFac =  10^(dbTmp/20);

% get settings
fs = signalStruct.ac.fs; % smapling frequency
fmin = playerStruct.fmin; % lower and ..
fmax = playerStruct.fmax;% upper frequency limit of filter bands
numberOfChannels = playerStruct.numberOfChannels;% number of bandpass filters 
% style of acoustic stimulation of vocoder signal. Another idea for the future 
% is to extract fine structure and degrade it to some extent.
stimSignalType = playerStruct.stimSignalType; 
% filter order of bandpass filters
filtN = playerStruct.filterOrder;
% getting cut off frequencies of filter bands
freqsCut = logspace(log10(fmin), log10(fmax),numberOfChannels+1);
% time step between two samples
dt = 1/fs;
% make it as loud as it should be
signal = signalStruct.ac.sig*scaleFac;


sigLen = length(signal);
% initializing the matrix which will contain the instantaneous amplitude of
% a signal.
amps = zeros(sigLen,numberOfChannels);
% getting filter bands
for ii = 1:numberOfChannels
    % getting filter coefficients
   [b, a] = butter( filtN, freqsCut([ii ii+1])/(fs/2));
   % filtering
   sigFilt = filter(b,a,signal);
   % getting envelope
   amps(:,ii) =  abs(hilbert( sigFilt ));
end
% %% Display spectral information over time
if psyVar.figureMode;
    % time vector of signal
    t = 0:dt:length(signal)/fs-dt;
    % center frequencies of filter bands
    freqsLabel = round( geomean( [freqsCut(1:end-1);freqsCut(2:end)] ) );
    figure; imagesc(freqsLabel,t,db( amps) );
    xlabel('Frequency (Hz)');
    ylabel('Time (s)');
end
%% generate vocoding signal
if strcmp(stimSignalType,'noise')
    noise = rand(sigLen,1);
elseif  strcmp(stimSignalType,'sinus')
    % time vector of signal
    t = 0:dt:length(signal)/fs-dt;
end
% initialize memory for output signal
resultSignal = zeros( size( signal ) );

% looping through different filter bands.
for ii = 1:numberOfChannels
    [b, a] = butter( filtN, freqsCut([ii ii+1])/(fs/2));
    switch stimSignalType
        % noise, sinusoidal, or pulse train excitation?
        case 'noise'
            noiseFilt = filter(b,a,noise);
        case 'sinus'
            fc = geomean( freqsCut([ii ii+1]) );
            noiseFilt = sin(2*pi*fc*t)';
        case 'pulsetrain'
            fc = geomean( freqsCut([ii ii+1]) );
            noise = zeros(length(signal),1);
            noise( round( (1:fs/fc:length(signal)) ) ) = 1;
            noiseFilt = filter(b,a,noise);
        otherwise
            error([ 'unknown option: ' stimSignalType])
    end
    % refilter noise after applying envelope to cut off introduced higher
    % and lower frequencies.
    resultSignal = resultSignal + filter(b,a,noiseFilt.* amps(:,ii));
end

%% get the same level asthe input signal
resultSignal = resultSignal *  sqrt( mean( signal.^2))/sqrt( mean(resultSignal.^2));

if max(abs(resultSignal))>1
    warning('clipping of played signal!'); %#ok<WNTAG>
    if psyVar.detailedOutput; fprintf(' || Clipping of %3d samples! || ',...
            sum(abs(resultSignal) > 1)); 
    end;
end

if isunix
    % linux
    sound(resultSignal,fs);
else
    % microsoft
    wavplay(resultSignal,fs);
end
resultStruct = signalStruct;
resultStruct.ac.sig =  resultSignal;
end


% EOF