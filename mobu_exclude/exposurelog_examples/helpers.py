from dataclasses import field, dataclass
from datetime import datetime
from http import HTTPStatus
import os
import pandas as pd
import requests
from typing import List

__all__ = ('ENDPOINT', 'add_message', 'get_messages', 'get_message_by_id', 'edit_message',
           'delete_message', 'MessageSearcher', 'ExposureSearcher')

ENDPOINT = 'https://base-lsp.lsst.codes/exposurelog/'

def check_resp(resp, success=HTTPStatus.OK):
    """Check the response code
    
    Parameters
    ----------
    resp : `requests.Response`
        The response to check
    success : `HTTPStatus`, optional
        The status code defining success, default is `HTTPStatus.OK`.

    Raises
    ------
    ValueError
        Raises if the response code does not agree with the success code.
    """
    if resp.status_code == success:
        return
    else:
        # Maybe try to get some info out of the response on failure
        raise ValueError(f'Request failed with code: {resp.status_code}')

def add_message(obs_id, instrument, message_text, user_id=None, user_agent=None, is_new=False, is_human=True, exposure_flag='none'):
    """Add a message to the exposure log

    Parameters
    ----------
    obs_id : `str`
        The string identifier for the observation ID to associate with this message.
        It must exist in the backing registry if ``is_new`` is set to `False` (the default).
    instrument : `str`
        The name of the instrument for the observation.
        These are not validated against a known set by the service, so convention must be followed.
    message_text : `str`
        The text of the message
    user_id : `str`, optional
        The identifier for the user adding the messge.
        If no identifier is provided, the user's username is used instead.
    user_agent : `str`, optional
        A description of the system producing the message.
        Default is ``notebook:nublado``
    is_new : `bool`, optional
        Is this message for an observation id that is too new to be ingested?
        Default is `False`.
    is_human : `bool`, optional
        Is the entitly submitting this message a human?
        Default is `True`.
    exposure_flag : `str`, optional
        A flag for the exposure related to this message.
        Must be one of ``none``, ``junk`` or ``questionable``.
        Default is ``none``.

    Returns
    -------
    results : `dict`
        A dictionary describing the message as ingested into the service.
    """
    if exposure_flag not in ['none', 'junk', 'questionable']:
        raise ValueError('The exposure_flag argument must be one of: none, junk, or questionable')
    data = {'obs_id': obs_id, 'instrument': instrument, 'message_text': message_text, 'is_new': is_new, 'is_human': is_human, 'exposure_flag': exposure_flag}
    if user_id:
        data['user_id'] = user_id
    else:
        data['user_id'] = os.environ['JUPYTERHUB_USER']
    if user_agent:
        data['user_agent'] = user_agent
    else:
        data['user_agent'] = 'notebook:nublado'
        
    resp = requests.post(ENDPOINT+'messages/', json=data)
    check_resp(resp)
    return resp.json()

def get_messages(all=False, num=50, as_dataframe=True):
    """Get messages from the service
    
    Parameters
    ----------
    all : `bool`, optional
        Return all of the messages instead of just the valid ones?
        Default is `False`.
    num : `int`, optional
        The number of messages to return.
        Default is 50.
    as_dataframe : `bool`, optional
        Return the messages as a `pd.DataFrame`?
        Default is True.

    Returns
    -------
    results : `list` of `dict` or `pd.DataFrame`
        The messages as either a `list` of `dict` objects or a `pd.DataFrame` containing the messages.
    """
    if all:
        params = {'is_valid': 'either', 'limit': num}
        resp = requests.get(ENDPOINT+'messages/', params=params)
        check_resp(resp)
        messages = resp.json()
    else:
        params = {'is_valid': 'true', 'limit': num}
        resp = requests.get(ENDPOINT+'messages/')
        check_resp(resp)
        messages = resp.json() 
    if as_dataframe:
        return pd.DataFrame(messages)
    return messages

def get_message_by_id(message_id):
    """Get a message by its ID.
    
    Parameters
    ----------
    message_id : `str`
        The ID of the message to retrieve.

    Returns
    -------
    returns : `dict`
        A dictionary with message contents.

    Raises
    ------
    ValueError
        Raises if the message ID is not found.
    """
    resp = requests.get(f'{ENDPOINT}messages/{message_id}')
    check_resp(resp)
    return resp.json()

def edit_message(message_id, message_text=None, site_id=None, user_id=None, user_agent=None, is_human=None, exposure_flag=None, check_validity=True):
    """Edit the contents of a message.
    
    Parameters
    ----------
    message_id : `str`
        The ID of the message to edit.
    message_text : `str`, optional
        Edited text.
    site_id : `str`, optional
        Edited site ID.
    user_id : `str`, optional
        Edited user ID.
    user_agent : `str`, optional
        Edited user agent string.
    is_human : `bool`, optional
        Edited ``is_human`` value.
    exposure_flag : `str`, optional
        Edited exposure flag.
        Must be one of ``none``, ``junk`` or ``questionable``.
    check_validity : `bool`, optional
        Check whether the message being edited is marked valid.
        
    Returns
    -------
    returns : 'dict'
        A dictionary containing the edited contents of the message as ingested in the service.

    Raises
    ------
    ValueError
        Raises if the message being edited is marked invalid and ``check_validity`` is `True`.
    """
    resp = requests.get(f'{ENDPOINT}messages/{message_id}')
    check_resp(resp)
    message = resp.json()
    if not message['is_valid'] and check_validity:
        raise ValueError(f'Message {message_id} is marked as invalid in the database.')
    data = {}
    loc_vars = locals()
    for k in ['message_text', 'site_id', 'user_id', 'user_agent', 'is_human', 'exposure_flag']:
        if loc_vars[k]:
            data[k] = loc_vars[k]
        else:
            data[k] = message[k]
    resp = requests.patch(f'{ENDPOINT}messages/{message_id}', json=data)
    check_resp(resp)
    return resp.json()

def delete_message(message_id):
    """Delete a message given a message ID.

    Parameters
    ----------
    message_id : `str`
        Identifier of the message to delete.

    Raises
    ------
    ValueError
        Raises if the message ID is not found.
    """
    resp = requests.delete(f'{ENDPOINT}messages/{message_id}')
    check_resp(resp, success=HTTPStatus.NO_CONTENT)

@dataclass
class MessageSearcher:
    site_ids: List[str] = None
    obs_id: str = None
    instruments: List[str] = None
    min_day_obs: int = None
    max_day_obs: int = None
    message_text: str = None
    user_ids: List[str] = None
    user_agents: List[str] = None
    is_human: str = 'either'  # Must be 'true', 'false' or 'either'
    is_valid: str = 'true'  # Must be 'true', 'false' or 'either'
    exposure_flags: str = None
    min_date_added: datetime = None
    max_date_added: datetime = None
    has_date_invalidated: bool = None
    min_date_invalidated: datetime = None
    max_date_invalidated: datetime = None
    has_parent_id: bool = None
    order_by: List[str] = None
    offset: int = 0
    limit: int = 50

    def search(self, as_dataframe=True):
        params = {}
        for k in self.__dict__:
            if self.__dict__[k] is not None:
                params[k] = self.__dict__[k]
        resp = requests.get(f'{ENDPOINT}messages/', params=params)
        check_resp(resp)
        if as_dataframe:
            return pd.DataFrame(resp.json())
        return resp.json()

@dataclass
class ExposureSearcher:
    instrument: str
    min_day_obs: int = None
    max_day_obs: int = None
    min_seq_num: int = None
    max_seq_num: int = None
    group_names: List[str] = None
    observation_reasons: List[str] = None
    observation_types: List[str] = None
    min_date: datetime = None
    max_date: datetime = None
    limit: int = 50

    def search(self, as_dataframe=True):
        params = {}
        for k in self.__dict__:
            if self.__dict__[k]:
                params[k] = self.__dict__[k]
        resp = requests.get(f'{ENDPOINT}exposures/', params=params)
        check_resp(resp)
        if as_dataframe:
            return pd.DataFrame(resp.json())
        return resp.json()