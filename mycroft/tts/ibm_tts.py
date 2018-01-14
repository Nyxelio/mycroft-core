from mycroft.tts import TTS, TTSValidator
from os.path import join, dirname
from watson_developer_cloud import TextToSpeechV1
from threading import Thread
from time import sleep
from mycroft.tts import mimic_tts


class IBMTTS(TTS):
    def __init__(self, lang, voice, username, password, timeout):
        self.type = 'mp3'
        super(IBMTTS, self).__init__(lang, voice, IBMTTSValidator(self))
        self.text_to_speech = TextToSpeechV1(
            username=username,
            password=password)

    def get_tts(self, sentence, wav_file):
        try:
            result = self.text_to_speech.synthesize(sentence, \
              accept="audio/mp3", voice=self.voice)

	    with open(wav_file, 'wb') as audio_file:
	        audio_file.write(result) 

            return (wav_file, None)

        except Exception as e:
            print e
            print "IBM TTS ran into an error."

class IBMTTSValidator(TTSValidator):
    def __init__(self, tts):
        super(IBMTTSValidator, self).__init__(tts)

    def validate_lang(self):
	#TODO
        pass

    def validate_connection(self):
	#TODO
	pass
	
    def get_tts_class(self):
        return IBMTTS
