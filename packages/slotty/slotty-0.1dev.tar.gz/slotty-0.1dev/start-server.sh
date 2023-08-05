#!/bin/bash
gunicorn -k socketio.sgunicorn.GeventSocketIOWorker slotty.app:app $@
