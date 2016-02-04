from chatterbot.adapters.io import IOAdapter

import speech_recognition


class WitAISTT(IOAdapter):
    """
    Speech-To-Text implementation which relies on the Wit.ai Speech API.

    This implementation requires an Wit.ai Access Token to be present in
    ChatterBot configuration. Please sign up at https://wit.ai and copy
    your instance token, which can be found under Settings in the Wit console.

    A fair portion of this code has been copied from the JasperProject, which
    is licensed under the MIT license. Their copyright notice is as follows:
    Copyright (c) 2014-2015 Charles Marsh, Shubhro Saha & Jan Holthuis
    """

    def __init__(self, **kwargs):
        super(WitAISTT, self).__init__(**kwargs)

        self.token = kwargs.get("wit_api_token")
        self.headers = {'Authorization': 'Bearer %s' % self.token,
                         'accept': 'application/json',
                         'Content-Type': 'audio/wav'}

    def process_input(self):
        """
        Read the user's input from the terminal.
        """

    def process_response(self, statement):
        """
        Return the response (STT engines do not have any output).
        """
        return statement.text

    def transcribe(self, fp):
        data = fp.read()
        r = requests.post('https://api.wit.ai/speech?v=20150101',
                          data=data,
                          headers=self.headers)
        try:
            r.raise_for_status()
            text = r.json()['_text']
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with response: %r',
                                  r.text,
                                  exc_info=True)
            return []
        except requests.exceptions.RequestException:
            self._logger.critical('Request failed.', exc_info=True)
            return []
        except ValueError as e:
            self._logger.critical('Cannot parse response: %s',
                                  e.args[0])
            return []
        except KeyError:
            self._logger.critical('Cannot parse response.',
                                  exc_info=True)
            return []
        else:
            transcribed = []
            if text:
                transcribed.append(text.upper())
            self._logger.info('Transcribed: %r', transcribed)
            return transcribed
