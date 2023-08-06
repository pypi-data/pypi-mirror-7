#!/usr/bin/python
# -*- coding: utf-8 -*-

def sbo_slackbuild_dwn(sbo_url, name):
    '''
    Convert http repository link to 
    slackbuild download link
    '''
    sbo_url = sbo_url.replace(name + "/", name + ".tar.gz")
    return sbo_url.replace("repository", "slackbuilds")
