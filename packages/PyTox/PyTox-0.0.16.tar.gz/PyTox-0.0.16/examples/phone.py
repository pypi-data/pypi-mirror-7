#
# @file   phone.py
# @author Wei-Ning Huang (AZ) <aitjcize@gmail.com>
#
# Copyright (C) 2013 - 2014 Wei-Ning Huang (AZ) <aitjcize@gmail.com>
# All Rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys

import cv2
import numpy as np
import pyaudio

from time import sleep
from os.path import exists
from threading import Thread
from select import select

from tox import Tox, ToxAV

SERVER = ["54.199.139.199", 33445, "7F9C31FE850E97CEFD4C4591DF93FC757C7C12549DDD55F8EEAECC34FE76C029"]


DATA = 'data'
cap = cv2.VideoCapture(0)
audio = pyaudio.PyAudio()

class AV(ToxAV):
    def __init__(self, core, width, height, debug=False):
        self.debug = debug
        self.core = self.get_tox()
        self.stop = True
        self.call_type = self.TypeAudio
        self.ae_thread = None
        self.ad_thread = None
        self.ve_thread = None
        self.vd_thread = None

    def on_invite(self):
        self.call_type = self.get_peer_transmission_type(0)
        print("Incoming %s call from %s ..." % (
                "video" if self.call_type == self.TypeVideo else "audio",
                self.core.get_name(self.get_peer_id(0))))

        self.answer(self.call_type)
        print("Answered, in call...")

    def on_start(self):
        self.call_type = self.get_peer_transmission_type(0)
        self.prepare_transmission(True)

        self.stop = False
        self.aistream = audio.open(format=pyaudio.paInt16, channels=1,
                                  rate=48000, input=True,
                                  frames_per_buffer=960)
        self.aostream = audio.open(format=pyaudio.paInt16, channels=1,
                                  rate=48000, output=True)

        self.ae_thread = Thread(target=self.audio_encode)
        self.ae_thread.daemon = True
        self.ad_thread = Thread(target=self.audio_decode)
        self.ad_thread.daemon = True
        self.ae_thread.start()
        self.ad_thread.start()

        if self.call_type == self.TypeVideo:
            self.ve_thread = Thread(target=self.video_encode)
            self.ve_thread.daemon = True
            self.vd_thread = Thread(target=self.video_decode)
            self.vd_thread.daemon = True
            self.ve_thread.start()
            self.vd_thread.start()

    def on_end(self):
        self.stop = True
        if self.ae_thread:
            self.ae_thread.join()
        if self.ad_thread:
            self.ad_thread.join()
        if self.call_type == self.TypeVideo:
            if self.ve_thread:
                self.ve_thread.join()
            if self.vd_thread:
                self.vd_thread.join()

        self.kill_transmission()
        print("Call ended")

    def on_starting(self):
        self.on_start()

    def on_ending(self):
        self.on_end()

    def on_cancel(self):
        try:
            self.stop_call()
        except: pass

    def on_peer_timeout(self):
        self.on_cancel()

    def on_request_timeout(self):
        self.on_cancel()

    def audio_encode(self):
        print("Starting audio encode thread...")

        while not self.stop:
            try:
                self.send_audio(960, self.aistream.read(960))
            except Exception as e:
                print(e)

            sleep(0.005)

    def audio_decode(self):
        print("Starting audio decode thread...")

        while not self.stop:
            try:
                aret = self.recv_audio()
                if aret:
                    if self.debug:
                        sys.stdout.write('.')
                        sys.stdout.flush()
                    self.aostream.write(aret["data"])
            except Exception as e:
                print(e)

            sleep(0.005)

    def video_encode(self):
        print("Starting video encode thread...")

        while not self.stop:
            try:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.send_video(frame.tostring())
            except Exception as e:
                print(e)

            sleep(0.001)

    def video_decode(self):
        print("Starting video decode thread...")

        while not self.stop:
            try:
                vret = self.recv_video()
                if vret:
                    if self.debug:
                        sys.stdout.write('*')
                        sys.stdout.flush()

                    frame = np.ndarray(shape=(vret['d_h'], vret['d_w'], 3),
                            dtype=np.dtype(np.uint8), buffer=vret["data"])
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    cv2.imshow('frame', frame)
                    cv2.waitKey(1)
            except Exception as e:
                print(e)

            sleep(0.001)


class Phone(Tox):
    def __init__(self):
        if exists(DATA):
            self.load_from_file(DATA)

        self.set_name("PyTox-Phone")
        print('ID: %s' % self.get_address())

        self.connect()
        self.av = AV(self, 640, 480)

    def connect(self):
        print('connecting...')
        self.bootstrap_from_address(SERVER[0], 1, SERVER[1], SERVER[2])

    def loop(self):
        checked = False

        try:
            while True:
                status = self.isconnected()

                if not checked and status:
                    print('Connected to DHT.')
                    checked = True

                if checked and not status:
                    print('Disconnected from DHT.')
                    self.connect()
                    checked = False

                readable, _, _ = select([sys.stdin], [], [], 0.01)

                if readable:
                    args = sys.stdin.readline().strip().split()
                    if args:
                        if args[0] == "add":
                            try:
                                self.add_friend(args[1], "Hi")
                            except: pass
                            print('Friend added')
                        elif args[0] == "msg":
                            try:
                                if len(args) > 2:
                                    friend_number = int(args[1])
                                    msg = ' '.join(args[2:])
                                    self.send_message(friend_number, msg)
                            except: pass
                        elif args[0] == "call":
                            if len(args) == 2:
                                self.call(int(args[1]))
                        elif args[0] == "cancel":
                            try:
                                if len(args) == 2:
                                    self.av.cancel(int(args[1]), 'cancel')
                                    print('Canceling...')
                            except: pass
                        elif args[0] == "hangup":
                            try:
                                self.av.hangup()
                            except: pass
                        elif args[0] == "quit":
                            raise KeyboardInterrupt

                self.do()
        except KeyboardInterrupt:
            self.save_to_file(DATA)
            cap.release()
            cv2.destroyAllWindows()

    def on_friend_request(self, pk, message):
        print('Friend request from %s: %s' % (pk, message))
        self.add_friend_norequest(pk)
        print('Accepted.')

    def on_friend_message(self, friendId, message):
        name = self.get_name(friendId)
        print('%s: %s' % (name, message))

    def on_connection_status(self, friendId, status):
        print('%s %s' % (self.get_name(friendId),
                'online' if status else 'offline'))

    def call(self, friend_number):
        print('Calling %s ...' % self.get_name(friend_number))
        self.av.call(friend_number, self.av.TypeVideo, 60)

if len(sys.argv) == 2:
    DATA = sys.argv[1]

t = Phone()
t.loop()
